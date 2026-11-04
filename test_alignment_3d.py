import copy
from collections import Counter
import contextlib
import io
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import nms_base_align_3d as a


def part(id, p):
    return dict(ObjectID=id, Position=p, Up=[0, 2, 0], At=[0, 0, 3], UserData={'keep': 42})


def fixture():
    return dict(Owner={'UID': 'synthetic-test'}, GalacticAddress='test', Position=[1,2,3], Forward=[0,0,1],
                Objects=[part(a.FLAG,[0,0,0]),part('^FLOOR',[2,3,4]),part('^FLOOR',[8,9,10]),part('^OTHER',[-2,0,4])])


class AlignmentTests(unittest.TestCase):
    def assertVector(self, x, y):
        for v,w in zip(x,y): self.assertAlmostEqual(v,w,places=7)

    def corrected(self):
        before=fixture(); after=copy.deepcopy(before)
        # Combined rotations, including a vertical inversion component.
        rx,ry,rz=map(math.radians,[37,-53,121])
        def rotate(v):
            x,y,z=v
            y,z=y*math.cos(rx)-z*math.sin(rx),y*math.sin(rx)+z*math.cos(rx)
            x,z=x*math.cos(ry)+z*math.sin(ry),-x*math.sin(ry)+z*math.cos(ry)
            return [x*math.cos(rz)-y*math.sin(rz),x*math.sin(rz)+y*math.cos(rz),z]
        ref=after['Objects'][1]
        ref['Position']=[x+d for x,d in zip(rotate(ref['Position']),[5,-7,11])]
        for k in ('Up','At'): ref[k]=rotate(ref[k])
        return before,after,rotate

    def test_combined_rotation_reordered_duplicate_reference(self):
        before,after,rotate=self.corrected()
        after['Objects'].reverse()
        pairs=a.reference_pairs(before,after)
        self.assertEqual(pairs,[(1,2)])
        out=a.align(before,after,pairs[0])
        self.assertEqual(out['Objects'][2],after['Objects'][2])
        self.assertEqual(a.flag(out),a.flag(before))
        for original, result in zip(before['Objects'],reversed(out['Objects'])):
            if original['ObjectID']==a.FLAG: continue
            self.assertVector(result['Position'],[x+d for x,d in zip(rotate(original['Position']),[5,-7,11])])
            for k in ('Up','At'): self.assertVector(result[k],rotate(original[k]))
            self.assertEqual(result['UserData'],original['UserData'])
        self.assertEqual(out['Owner'],after['Owner'])

    def test_orientation_only_and_translation_only(self):
        for orientation in (True,False):
            b=fixture(); c=copy.deepcopy(b)
            if orientation: c['Objects'][1]['At']=[3,0,0]
            else: c['Objects'][1]['Position']=[99,3,4]
            self.assertEqual(a.reference_pairs(b,c),[(1,1)])

    def test_reject_unrelated_changes_and_computer(self):
        b,c,_=self.corrected(); c['Objects'][2]['Position'][0]+=1
        with self.assertRaises(a.AlignmentError): a.reference_pairs(b,c)
        with self.assertRaises(a.AlignmentError): a.reference_pairs(b,c,'1:1')
        b=fixture(); c=copy.deepcopy(b); c['Objects'][0]['Up']=[1,0,0]
        with self.assertRaises(a.AlignmentError): a.reference_pairs(b,c)

    def test_reject_identity_scale_and_degenerate(self):
        for change in ('owner','scale','zero','parallel','removed'):
            b=fixture(); c=copy.deepcopy(b)
            if change=='owner': c['Owner']['UID']='different'
            if change=='scale': c['Objects'][1]['Up']=[0,4,0]
            if change=='zero': c['Objects'][1]['Up']=[0,0,0]
            if change=='parallel': c['Objects'][1]['At']=[0,3,0]
            if change=='removed': c['Objects'].pop()
            with self.assertRaises(a.AlignmentError): a.reference_pairs(b,c,'1:1')

    def test_manual_mode_and_selectors(self):
        b=fixture()
        self.assertEqual(len(a.reference_pairs(b,b)),3)
        self.assertEqual(a.reference_pairs(b,b,'^OTHER'),[(3,3)])
        for selector in ('^FLOOR','-1:0','999:0','0:0'):
            with self.assertRaises(a.AlignmentError): a.reference_pairs(b,b,selector)

    def test_html_generation_and_protected_inputs(self):
        b,c,_=self.corrected(); b['Name']=c['Name']='</script><script>alert(1)</script>'
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); old=root/'before.nmsbase'; new=root/'after.nmsbase'; out=root/'preview.html'
            old.write_text(json.dumps(b));new.write_text(json.dumps(c))
            with patch('sys.argv',['tool',str(old),str(new),'-o',str(out)]): a.main()
            html=out.read_text(encoding='utf-8')
            self.assertNotIn('</script><script>alert',html)
            self.assertNotIn('/*BASE_DATA*/null',html)
            with patch('sys.argv',['tool',str(old),str(new),'-o',str(out)]):
                with self.assertRaises(SystemExit): a.main()
            self.assertEqual(json.loads(old.read_text()),b)

    def test_tolerance_metadata_and_reordered_detection(self):
        b = fixture(); c = copy.deepcopy(b)
        c['Objects'][2]['UserData'] = {'color': 'new'}
        c['Objects'][2]['Position'][0] += 5e-7
        self.assertEqual(len(a.reference_pairs(b, c)), 3)
        c['Objects'][1]['Position'][1] += 4
        c['Objects'].reverse()
        self.assertEqual(a.reference_pairs(b, c), [(1, 2)])

    def test_axis_masks_without_rotation(self):
        b, c, _ = self.corrected()
        delta = [y-x for x, y in zip(b['Objects'][1]['Position'], c['Objects'][1]['Position'])]
        for mask in range(8):
            axes = [bool(mask & (1 << k)) for k in range(3)]
            out = a.align(b, c, (1, 1), axes, False)
            self.assertEqual(out['Objects'][0], b['Objects'][0])
            self.assertEqual(out['Objects'][1], c['Objects'][1])
            for i in (2, 3):
                self.assertVector(out['Objects'][i]['Position'],
                                  [v+(delta[k] if axes[k] else 0) for k, v in enumerate(b['Objects'][i]['Position'])])
                self.assertEqual(out['Objects'][i]['Up'], b['Objects'][i]['Up'])
                self.assertEqual(out['Objects'][i]['At'], b['Objects'][i]['At'])

    def test_identity_preserves_exact_values(self):
        b = fixture()
        b['Objects'][1]['Up'] = [0.001, 2, 0]
        b['Objects'][1]['At'] = [0, 0, 3]
        self.assertEqual(a.align(b, b, (1, 1)), b)

    def test_single_file_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'base.nmsbase'; output = Path(tmp) / 'manual.html'
            source.write_text(json.dumps(fixture()))
            with patch('sys.argv', ['tool', str(source), '-o', str(output)]):
                a.main()
            html = output.read_text(encoding='utf-8')
            self.assertIn('"after": null', html)
            self.assertIn('id="afterFile"', html)
            with patch('sys.argv', ['tool', str(source), '-o', str(source)]):
                with self.assertRaises(SystemExit): a.main()

    def test_moved_wiring_is_ignored_and_transformed_from_before(self):
        b, c, rotate = self.corrected()
        wires = [part('^U_POWERLINE', [10, 20, 30]), part('^U_POWERLINE', [-4, 8, 12])]
        for wire in wires:
            wire['Up'] = [1, 2, 3]
            wire['At'] = [4, 5, 6]  # Wiring need not have a regular orientation frame.
        b['Objects'].extend(copy.deepcopy(wires))
        c['Objects'].extend(copy.deepcopy(wires))
        c['Objects'][4]['Position'] = [999, 888, 777]
        c['Objects'][4]['At'] = [9, 9, 9]
        c['Objects'][4]['UserData'] = {'latest': True}
        c['Objects'].reverse()
        self.assertEqual(a.reference_pairs(b, c), [(1, 4)])
        self.assertEqual(a.reference_pairs(b, c, '1:4'), [(1, 4)])
        out = a.align(b, c, (1, 4))
        for i, j in a.wiring_pairs(b, c).items():
            original, result = b['Objects'][i], out['Objects'][j]
            self.assertVector(result['Position'], [x+d for x,d in zip(rotate(original['Position']), [5,-7,11])])
            for field in ('Up', 'At'):
                self.assertVector(result[field], rotate(original[field]))
            self.assertEqual(result['UserData'], c['Objects'][j]['UserData'])
        self.assertEqual(a.flag(out), a.flag(b))
        with self.assertRaises(a.AlignmentError):
            a.reference_pairs(b, c, '4:1')
        c['Objects'][3]['Position'][0] += 1
        with self.assertRaises(a.AlignmentError):
            a.reference_pairs(b, c)

    def test_wire_only_changes_and_part_counts(self):
        b = fixture(); b['Objects'].append(part('^U_POWERLINE', [1, 2, 3]))
        c = copy.deepcopy(b); c['Objects'][-1]['Position'][0] += 4
        self.assertEqual(len(a.reference_pairs(b, c)), 3)
        self.assertEqual(a.align(b, c, (1, 1)), b)
        c['Objects'].append(part('^U_POWERLINE', [3, 4, 5]))
        self.assertEqual(len(a.reference_pairs(b, c)), 3)
        self.assertEqual(a.align(b, c, (1, 1)), b)
        c['Objects'] = [o for o in c['Objects'] if not a.is_wiring(o)]
        self.assertEqual(len(a.reference_pairs(b, c)), 3)
        self.assertEqual(a.align(b, c, (1, 1)), b)

    def test_missing_wire_before_reordered_reference(self):
        b, c, rotate = self.corrected()
        b['Objects'].insert(0, part('^U_PORTALLINE', [10, 20, 30]))
        c['Objects'].append(part('^U_POWERLINE', [99, 88, 77]))
        c['Objects'].reverse()
        pair = a.reference_pairs(b, c)[0]
        self.assertEqual(pair, (2, 3))
        out = a.align(b, c, pair)
        self.assertEqual(Counter(o['ObjectID'] for o in out['Objects']),
                         Counter(o['ObjectID'] for o in b['Objects']))
        wire = next(o for o in out['Objects'] if a.is_wiring(o))
        self.assertVector(wire['Position'], [v+d for v,d in zip(rotate([10,20,30]), [5,-7,11])])
        self.assertEqual(next(o for o in out['Objects'] if o['ObjectID'] == '^FLOOR' and o == c['Objects'][3]), c['Objects'][3])

    def test_missing_editor_template_explains_recovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'base.nmsbase'
            output = root / 'Preview.html'
            source.write_text(json.dumps(fixture()))
            error = io.StringIO()
            with patch.object(a, '__file__', str(root / 'nms_base_align_3d.py')):
                with patch('sys.argv', ['tool', str(source), str(source), '-o', str(output)]):
                    with contextlib.redirect_stderr(error):
                        with self.assertRaises(SystemExit) as caught:
                            a.main()
            self.assertEqual(caught.exception.code, 2)
            self.assertIn('Restore nms_base_editor.html', error.getvalue())
            self.assertFalse(output.exists())


if __name__=='__main__': unittest.main()
