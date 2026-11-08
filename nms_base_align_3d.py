"""Full 3D correction from one existing part; creates an offline HTML editor."""
import argparse
import copy
import json
import math
import sys
from collections import Counter
from pathlib import Path
from nms_base_align import AlignmentError, FLAG, read_base, flag


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def cross(a, b):
    return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]


def unit(v):
    length = math.sqrt(dot(v, v))
    if length < 1e-9:
        raise AlignmentError('Reference has a zero or degenerate orientation vector.')
    return [x/length for x in v]


def frame(obj):
    up, at = unit(obj['Up']), unit(obj['At'])
    if abs(dot(up, at)) > 1e-4:
        raise AlignmentError('Reference Up and At must be perpendicular. Choose a regular building part, not wiring.')
    right = unit(cross(up, at))
    return [right, up, unit(cross(right, up))]


def rotation(a, b):
    old, new = frame(a), frame(b)
    for field in ('Up', 'At'):
        if not math.isclose(dot(a[field], a[field]), dot(b[field], b[field]), rel_tol=1e-5, abs_tol=1e-8):
            raise AlignmentError('Reference scale changed. Move and rotate the existing part without resizing it.')
    return [[sum(new[k][i]*old[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def mv(matrix, vector):
    return [dot(row, vector) for row in matrix]


def validate(before, after):
    for key in ('GalacticAddress', 'Position', 'Forward', 'Owner'):
        if before.get(key) != after.get(key):
            raise AlignmentError(f'Base identity field {key} changed between exports.')
    if flag(before) != flag(after):
        raise AlignmentError('The Base Computer changed. Leave it untouched during calibration.')
    if Counter(o['ObjectID'] for o in before['Objects'] if not is_wiring(o)) != Counter(o['ObjectID'] for o in after['Objects'] if not is_wiring(o)):
        raise AlignmentError('Parts were added or deleted. Move and rotate one existing part only.')


def geometry_equal(a, b):
    return a['ObjectID'] == b['ObjectID'] and all(
        abs(x-y) <= 1e-6 for key in ('Position', 'Up', 'At')
        for x, y in zip(a[key], b[key]))


# Electrical wire geometry can change when a powered reference is moved.
WIRE_IDS = frozenset({'^U_POWERLINE', '^U_PORTALLINE'})


def is_wiring(obj):
    return obj['ObjectID'] in WIRE_IDS


def wiring_pairs(before, after):
    remaining = {j for j, obj in enumerate(after['Objects']) if is_wiring(obj)}
    pairs = {}
    # Preserve exact matches first; pair remaining wires by ID/export order.
    for i, obj in enumerate(before['Objects']):
        if not is_wiring(obj):
            continue
        j = next((j for j in sorted(remaining) if geometry_equal(obj, after['Objects'][j])), None)
        if j is not None:
            pairs[i] = j
            remaining.remove(j)
    for i, obj in enumerate(before['Objects']):
        if is_wiring(obj) and i not in pairs:
            j = next((j for j in sorted(remaining) if obj['ObjectID'] == after['Objects'][j]['ObjectID']), None)
            if j is None:
                continue
            pairs[i] = j
            remaining.remove(j)
    return pairs


def reference_pairs(before, after, selector=None):
    validate(before, after)
    old, new = before['Objects'], after['Objects']
    matches = wiring_pairs(before, after)
    remaining = {j for j, obj in enumerate(new) if not is_wiring(obj)}
    for i, obj in enumerate(old):
        if i in matches or is_wiring(obj):
            continue
        options = [j for j in sorted(remaining) if geometry_equal(obj, new[j])]
        if options:
            j = options[0]
            matches[i] = j
            remaining.remove(j)
    unmatched = [i for i in range(len(old)) if i not in matches and not is_wiring(old[i])]
    changed = bool(unmatched)
    if selector:
        if ':' in selector:
            try:
                i, j = map(int, selector.split(':'))
                if i < 0 or j < 0:
                    raise ValueError()
                old[i], new[j]
            except (ValueError, IndexError):
                raise AlignmentError('Use zero-based before:after indices for --reference.')
        else:
            aa = [i for i, o in enumerate(old) if o['ObjectID'] == selector]
            bb = [j for j, o in enumerate(new) if o['ObjectID'] == selector]
            if len(aa) != 1 or len(bb) != 1:
                raise AlignmentError('Reference ID is not unique; use before:after indices.')
            i, j = aa[0], bb[0]
        candidates = [(i, j)]
    elif len(unmatched) == len(remaining) == 1:
        candidates = [(unmatched[0], next(iter(remaining)))]
    elif not changed:
        candidates = [(i, j) for i, j in matches.items() if old[i]['ObjectID'] != FLAG and not is_wiring(old[i])]
    else:
        raise AlignmentError('More than one part changed. Export again after adjusting only the reference part.')
    valid = []
    for i, j in candidates:
        a, b = old[i], new[j]
        if a['ObjectID'] == FLAG or is_wiring(a) or a['ObjectID'] != b['ObjectID']:
            if selector:
                raise AlignmentError('Reference must identify the same non-computer, non-wiring part in both exports.')
            continue
        if not changed and not geometry_equal(a, b):
            raise AlignmentError('Reference indices do not match the same unchanged part.')
        if changed and (unmatched != [i] or remaining != {j}):
            raise AlignmentError('Other parts changed besides the selected reference.')
        try:
            rotation(a, b)
        except AlignmentError:
            if selector or changed:
                raise
            continue
        valid.append((i, j))
    if not valid:
        raise AlignmentError('No reliable reference found. Choose an existing part with perpendicular, nonzero Up/At vectors.')
    return valid


def align(before, after, pair, axes=(True, True, True), apply_rotation=True):
    i, j = pair
    a, b = before['Objects'][i], after['Objects'][j]
    same_orientation = all(abs(x-y) <= 1e-6 for key in ('Up', 'At')
                           for x, y in zip(a[key], b[key]))
    r = rotation(a, b) if apply_rotation and not same_orientation else None
    shift = [(y-x) if enabled else 0 for x, y, enabled in zip(a['Position'], b['Position'], axes)]
    result = copy.deepcopy(after)
    # Ignore After wire movement: transform the original wiring exactly once.
    wire_matches = wiring_pairs(before, after)
    # Retain every original segment, even if moving a device removed/rebuilt
    # segments in After. Keep matched After properties where available.
    for old_index, new_index in wire_matches.items():
        for field in ('Position', 'Up', 'At'):
            result['Objects'][new_index][field] = copy.deepcopy(before['Objects'][old_index][field])
    kept = [k for k, obj in enumerate(after['Objects']) if not is_wiring(obj) or k in wire_matches.values()]
    result['Objects'] = [result['Objects'][k] for k in kept] + [
        copy.deepcopy(obj) for i, obj in enumerate(before['Objects'])
        if is_wiring(obj) and i not in wire_matches]
    j = kept.index(j)
    for index, obj in enumerate(result['Objects']):
        if obj['ObjectID'] == FLAG or index == j:
            continue
        if r:
            offset = [x-y for x, y in zip(obj['Position'], a['Position'])]
            obj['Position'] = [x+y for x, y in zip(mv(r, offset), a['Position'])]
            for field in ('Up', 'At'):
                obj[field] = mv(r, obj[field])
        if any(shift):
            obj['Position'] = [x+y for x, y in zip(obj['Position'], shift)]
    return result


def read_model_json(path):
    with path.open('rb') as stream:
        data = stream.read(512_001)
    if len(data) > 512_000:
        raise ValueError('Model pack file exceeds size limit.')
    return json.loads(data)


def load_models(root, objects):
    try:
        manifest = read_model_json(root / 'manifest.json')
    except (OSError, ValueError, RecursionError):
        return {}
    if not isinstance(manifest, dict) or type(manifest.get('schema')) is not int or manifest['schema'] != 1:
        return {}
    entries = manifest.get('parts')
    if not isinstance(entries, dict):
        return {}
    models = {}
    remaining_vertices = 100_000
    remaining_indices = 300_000
    for part_id in dict.fromkeys(obj['ObjectID'].removeprefix('^') for obj in objects):
        relative = entries.get(part_id)
        if not isinstance(relative, str):
            continue
        try:
            path = Path(relative)
            if path.anchor or '..' in path.parts or path.suffix.lower() != '.json':
                continue
            target = (root / path).resolve()
            if not target.is_relative_to(root.resolve()):
                continue
            mesh = read_model_json(target)
        except (OSError, ValueError, RuntimeError):
            continue
        if not isinstance(mesh, dict):
            continue
        vertices, indices = mesh.get('vertices'), mesh.get('indices')
        if not isinstance(vertices, list) or not 3 <= len(vertices) <= min(2048, remaining_vertices):
            continue
        if not all(isinstance(v, list) and len(v) == 3 and
                   all(type(x) in (int, float) and -100_000 <= x <= 100_000 for x in v)
                   for v in vertices):
            continue
        if (not isinstance(indices, list) or not 3 <= len(indices) <= min(6144, remaining_indices)
                or len(indices) % 3
                or not all(type(i) is int and 0 <= i < len(vertices) for i in indices)):
            continue
        models[part_id] = {'vertices': vertices, 'indices': indices}
        remaining_vertices -= len(vertices)
        remaining_indices -= len(indices)
    return models


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('before', type=Path)
    parser.add_argument('after', type=Path, nargs='?', help='optional corrected export; omit for manual editing')
    parser.add_argument('-o', '--output', type=Path, required=True, help='new offline .html editor')
    parser.add_argument('--reference', help='unique ^ObjectID or zero-based before:after indices')
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    try:
        before = read_base(args.before)
        after = read_base(args.after) if args.after else copy.deepcopy(before)
        pairs = reference_pairs(before, after, args.reference)
        if args.output.suffix.lower() != '.html':
            raise AlignmentError('Editor output must have an .html extension.')
        if args.output.resolve() in (p.resolve() for p in (args.before, args.after) if p):
            raise AlignmentError('Output must not replace an input.')
        if args.output.exists() and not args.overwrite:
            raise AlignmentError('Output exists; choose another name or use --overwrite.')
        app_dir = Path(sys.executable if getattr(sys, 'frozen', False) else __file__).resolve().parent
        models = load_models(app_dir / 'models', before['Objects'])
        payload = json.dumps({'before': before, 'after': after if args.after else None,
                              'pairs': pairs, 'models': models}, allow_nan=False).replace('<', '\\u003c').replace('&', '\\u0026')
        template_path = Path(__file__).with_name('nms_base_editor.html')
        try:
            template = template_path.read_text(encoding='utf-8')
        except FileNotFoundError:
            raise AlignmentError(
                f'Missing browser editor template: {template_path}. '
                'Restore nms_base_editor.html from the original download beside '
                'nms_base_align.py and nms_base_align_3d.py, then rerun this command. '
                'Keep this template for future runs; use a different name for the generated viewer.'
            ) from None
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(template.replace('/*BASE_DATA*/null', payload), encoding='utf-8')
        print(f'Created {args.output}. Open it in your browser; select the reference, refine, then download the adjusted base.')
    except (AlignmentError, OSError, ValueError) as exc:
        parser.exit(2, f'Error: {exc}\n')


if __name__ == '__main__':
    main()

