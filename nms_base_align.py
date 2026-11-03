#!/usr/bin/env python3
"""Align an NMSE base transfer using two manually positioned objects.

Python 3.9+; standard library only. Run `python nms_base_align.py --help`.
The legacy mode reads four exports and writes a NEW .nmsbase file.
For full 3D correction and a browser editor, run:
  python nms_base_align.py 3d BEFORE.nmsbase AFTER.nmsbase -o Preview.html
"""

import argparse
from collections import Counter, defaultdict
import copy
import json
import math
from pathlib import Path
import sys

FLAG = '^BASE_FLAG'
POSITION_TOLERANCE = 0.05


class AlignmentError(Exception):
    pass


def read_base(path):
    try:
        base = json.loads(path.read_text(encoding='utf-8-sig'))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AlignmentError(f'Cannot read {path}: {exc}') from exc
    if not isinstance(base, dict) or not isinstance(base.get('Objects'), list):
        raise AlignmentError(f'{path} is not an NMSE base JSON export.')
    for i, obj in enumerate(base['Objects']):
        if not isinstance(obj, dict) or not isinstance(obj.get('ObjectID'), str):
            raise AlignmentError(f'Invalid object #{i} in {path}.')
        for field in ('Position', 'Up', 'At'):
            value = obj.get(field)
            if not isinstance(value, list) or len(value) != 3 or any(
                not isinstance(n, (int, float)) or not math.isfinite(n) for n in value
            ):
                raise AlignmentError(f'Invalid {field} on object #{i} in {path}.')
    flags = [o for o in base['Objects'] if o['ObjectID'] == FLAG]
    if len(flags) != 1:
        raise AlignmentError(f'{path} must contain exactly one {FLAG}; found {len(flags)}.')
    return base


def distance(a, b):
    return math.dist(a, b)


def ids_without_flag(base):
    return Counter(o['ObjectID'] for o in base['Objects'] if o['ObjectID'] != FLAG)


def flag(base):
    return next(o for o in base['Objects'] if o['ObjectID'] == FLAG)


def check_inputs(template, fresh, imported, corrected):
    if len(fresh['Objects']) != 1:
        raise AlignmentError('The new target export must have only its Base Computer.')
    source_ids = ids_without_flag(template)
    if not source_ids:
        raise AlignmentError('The template contains no construction objects to transfer.')
    for name, base in (('initially imported', imported), ('corrected', corrected)):
        if ids_without_flag(base) != source_ids:
            raise AlignmentError(f'The {name} export has different object IDs/counts from the template.')
        for field in ('GalacticAddress', 'Position', 'Forward'):
            if base.get(field) != fresh.get(field):
                raise AlignmentError(f'The {name} export does not match the new target {field}.')
        for field in ('LID', 'UID'):
            if base.get('Owner', {}).get(field) != fresh.get('Owner', {}).get(field):
                raise AlignmentError(f'The {name} export has a different owner {field}.')
        if distance(flag(base)['Position'], flag(fresh)['Position']) > POSITION_TOLERANCE:
            raise AlignmentError(f'The Base Computer moved in the {name} export.')
    if distance(flag(imported)['Position'], flag(corrected)['Position']) > 1e-5:
        raise AlignmentError('The Base Computer differs between the imported and corrected exports.')
    for field in ('Up', 'At'):
        if distance(flag(imported)[field], flag(corrected)[field]) > 1e-5:
            raise AlignmentError(f'The Base Computer {field} changed during calibration.')


def find_pairs(imported, corrected):
    """Pair equal IDs at nearly equal positions; leave moved objects unpaired."""
    old, new = imported['Objects'], corrected['Objects']
    old_groups, new_groups = defaultdict(list), defaultdict(list)
    for i, o in enumerate(old):
        if o['ObjectID'] != FLAG:
            old_groups[o['ObjectID']].append(i)
    for j, o in enumerate(new):
        if o['ObjectID'] != FLAG:
            new_groups[o['ObjectID']].append(j)
    pairs = []
    for object_id, old_indices in old_groups.items():
        unmatched = set(new_groups[object_id])
        for i in old_indices:
            matches = sorted(
                (distance(old[i]['Position'], new[j]['Position']), j) for j in unmatched
            )
            if matches and matches[0][0] <= POSITION_TOLERANCE:
                _, j = matches[0]
                unmatched.remove(j)
                pairs.append((i, j))
        # For a unique ID, even a moved object has an unambiguous match.
        if len(old_indices) == 1 and not any(i == old_indices[0] for i, _ in pairs):
            pairs.append((old_indices[0], new_groups[object_id][0]))
    return pairs


def describe_pair(pair, imported, corrected):
    i, j = pair
    a, b = imported['Objects'][i], corrected['Objects'][j]
    return f'{i}:{j} {a["ObjectID"]} moved {distance(a["Position"], b["Position"]):.3f}'


def parse_reference(selector, imported, corrected, pairs):
    old, new = imported['Objects'], corrected['Objects']
    if ':' in selector:
        try:
            i, j = (int(v) for v in selector.split(':'))
            if i < 0 or j < 0:
                raise ValueError('negative index')
            a, b = old[i], new[j]
        except (ValueError, IndexError) as exc:
            raise AlignmentError(f'Bad reference {selector!r}; use old_index:new_index.') from exc
        if a['ObjectID'] == FLAG or a['ObjectID'] != b['ObjectID']:
            raise AlignmentError(f'Reference {selector!r} does not identify the same non-computer part.')
        return i, j
    matches = [pair for pair in pairs if old[pair[0]]['ObjectID'] == selector]
    if len(matches) != 1:
        raise AlignmentError(f'{selector!r} is not uniquely identifiable. Use old_index:new_index.')
    return matches[0]


def choose_references(args, imported, corrected, pairs):
    moved = [p for p in pairs if distance(
        imported['Objects'][p[0]]['Position'], corrected['Objects'][p[1]]['Position']
    ) > POSITION_TOLERANCE]
    if args.references:
        selectors = [s.strip() for s in args.references.split(',')]
        if len(selectors) != 2:
            raise AlignmentError('--references needs two comma-separated IDs or index pairs.')
        chosen = [parse_reference(s, imported, corrected, pairs) for s in selectors]
    elif len(moved) == 2:
        chosen = moved
        print('Automatically identified two moved objects:')
    else:
        print(f'Found {len(moved)} unambiguous moved objects. Select exactly two.')
        print('Candidates (indices are zero-based, as listed in the JSON Objects arrays):')
        for pair in moved:
            print(' ', describe_pair(pair, imported, corrected))
        if not sys.stdin.isatty():
            raise AlignmentError('Specify --references ID1,ID2 or old:new,old:new.')
        chosen = [parse_reference(input(f'Reference {n} (ObjectID or old:new): ').strip(),
                                  imported, corrected, pairs) for n in (1, 2)]
    if chosen[0] == chosen[1] or chosen[0][0] == chosen[1][0] or chosen[0][1] == chosen[1][1]:
        raise AlignmentError('The two references must be different objects.')
    for p in chosen:
        print(' ', describe_pair(p, imported, corrected))
    return chosen


def choose_anchor(args, references, imported, corrected):
    """Return (anchor, angle reference) in that order."""
    print('Choose the well-placed object (the pin). The other sets the angle:')
    for number, pair in enumerate(references, 1):
        i, j = pair
        print(f'  {number}. {imported["Objects"][i]["ObjectID"]} '
              f'(initial object #{i}, corrected object #{j})')
    if args.anchor:
        matches = [n for n, (i, j) in enumerate(references, 1)
                   if args.anchor in (str(n), imported['Objects'][i]['ObjectID'], f'{i}:{j}')]
        if len(matches) != 1:
            raise AlignmentError('--anchor must be 1, 2, a unique ^ObjectID, or old:new index pair.')
        selected = matches[0]
    else:
        if not sys.stdin.isatty():
            raise AlignmentError('Run interactively to choose the well-placed object, '
                                 'or pass --anchor 1 / --anchor 2 / --anchor ^ObjectID.')
        while True:
            response = input('Well-placed anchor [1 or 2]: ').strip()
            if response in ('1', '2'):
                selected = int(response)
                break
            print('Enter 1 or 2.')
    ordered = (references[selected - 1], references[2 - selected])
    print('Anchor:', imported['Objects'][ordered[0][0]]['ObjectID'])
    print('Angle reference:', imported['Objects'][ordered[1][0]]['ObjectID'])
    return ordered


def rotate(v, angle):
    c, s = math.cos(angle), math.sin(angle)
    return [c * v[0] - s * v[2], v[1], s * v[0] + c * v[2]]


def calculate_transform(imported, corrected, references):
    old, new = imported['Objects'], corrected['Objects']
    a, b = [old[i]['Position'] for i, _ in references]  # anchor, angle reference
    a2, b2 = [new[j]['Position'] for _, j in references]
    ux, uz = b[0] - a[0], b[2] - a[2]
    vx, vz = b2[0] - a2[0], b2[2] - a2[2]
    before, after = math.hypot(ux, uz), math.hypot(vx, vz)
    if min(before, after) < 0.5:
        raise AlignmentError('Reference objects are too close together to measure a reliable rotation.')
    angle = math.atan2(ux * vz - uz * vx, ux * vx + uz * vz)
    rotated_anchor = rotate(a, angle)
    shift = [a2[k] - rotated_anchor[k] for k in range(3)]
    residuals = [distance([rotate(p, angle)[k] + shift[k] for k in range(3)], q)
                 for p, q in ((a, a2), (b, b2))]
    print(f'Horizontal rotation: {math.degrees(angle):+.4f} degrees')
    print('Local XYZ shift:', ', '.join(f'{v:+.5f}' for v in shift))
    print(f'Reference separation: {before:.4f} before, {after:.4f} after')
    print(f'Anchor fit error: {residuals[0]:.6f} (should be zero)')
    print(f'Angle-reference fit error: {residuals[1]:.4f}')
    if residuals[1] > 0.25:
        raise AlignmentError('The angle reference misses by more than 0.25 units. '
                             'Check the match and placement.')
    return angle, shift


def make_result(imported, corrected, references, angle, shift):
    result = copy.deepcopy(corrected)  # retain the target's latest metadata
    result['Objects'] = []
    replacements = {i: j for i, j in references}
    for i, original in enumerate(imported['Objects']):
        if original['ObjectID'] == FLAG:
            item = copy.deepcopy(flag(corrected))
        elif i in replacements:
            item = copy.deepcopy(corrected['Objects'][replacements[i]])
        else:
            item = copy.deepcopy(original)
            item['Position'] = [v + d for v, d in zip(rotate(item['Position'], angle), shift)]
            for field in ('Up', 'At'):
                item[field] = rotate(item[field], angle)  # vectors: no translation or normalization
        result['Objects'].append(item)
    assert ids_without_flag(result) == ids_without_flag(imported)
    assert len(result['Objects']) == len(imported['Objects'])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('template', type=Path, help='source/base-to-copy NMSE export')
    parser.add_argument('fresh_target', type=Path, help='target export with only its Base Computer')
    parser.add_argument('imported_target', type=Path, help='target export after initial import, before manual correction')
    parser.add_argument('corrected_target', type=Path, help='target export after moving two reference objects')
    parser.add_argument('-o', '--output', type=Path, required=True, help='new NMSE .nmsbase import file')
    parser.add_argument('--references', help='two unique ObjectIDs, e.g. ^BUILDBEACON,^POWERLINE_HIDER; '
                        'for duplicate IDs use zero-based imported:corrected indexes, e.g. 13:14,15:16')
    parser.add_argument('--anchor', help='well-placed reference: 1 or 2 as displayed, unique ^ObjectID, '
                        'or old:new indices. Otherwise the script prompts for it.')
    parser.add_argument('--overwrite', action='store_true', help='replace an existing output file')
    args = parser.parse_args()
    try:
        inputs = [read_base(path) for path in
                  (args.template, args.fresh_target, args.imported_target, args.corrected_target)]
        check_inputs(*inputs)
        _, fresh, imported, corrected = inputs
        pairs = find_pairs(imported, corrected)
        refs = choose_anchor(args, choose_references(args, imported, corrected, pairs), imported, corrected)
        chosen_old = {i for i, _ in refs}
        chosen_new = {j for _, j in refs}
        paired_old = {i for i, _ in pairs}
        paired_new = {j for _, j in pairs}
        if any(i not in paired_old and i not in chosen_old for i, o in enumerate(imported['Objects']) if o['ObjectID'] != FLAG) or any(
            j not in paired_new and j not in chosen_new for j, o in enumerate(corrected['Objects']) if o['ObjectID'] != FLAG
        ):
            raise AlignmentError('Some repeated-ID objects could not be paired. Identify both references '
                                 'with --references old:new,old:new or check the exports.')
        unexpected = [p for p in pairs if p[0] not in chosen_old and distance(
            imported['Objects'][p[0]]['Position'], corrected['Objects'][p[1]]['Position']
        ) > POSITION_TOLERANCE]
        if unexpected:
            raise AlignmentError('Other objects also moved: ' + ', '.join(
                describe_pair(p, imported, corrected) for p in unexpected[:8]))
        angle, shift = calculate_transform(imported, corrected, refs)
        result = make_result(imported, corrected, refs, angle, shift)
        if args.output.resolve() in (p.resolve() for p in
                                     (args.template, args.fresh_target, args.imported_target, args.corrected_target)):
            raise AlignmentError('Output must not overwrite any of the four input exports.')
        if args.output.exists() and not args.overwrite:
            raise AlignmentError(f'{args.output} exists. Choose a new path or pass --overwrite.')
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        print(f'Wrote {args.output} ({len(result["Objects"])} objects).')
        print('Restore a backed-up computer-only target save, then import this file with NMSE.')
    except AlignmentError as exc:
        parser.exit(2, f'Error: {exc}\n')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '3d':
        del sys.argv[1]
        from nms_base_align_3d import main as main_3d
        main_3d()
    else:
        main()
