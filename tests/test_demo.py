"""Small checks of archived evidence; no experiment execution."""
import contextlib,hashlib,io,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import demo

class EvidenceTests(unittest.TestCase):
    def test_archived_replay(self):
        out=io.StringIO()
        with contextlib.redirect_stdout(out):demo.main()
        self.assertIn('PASS: archived counts',out.getvalue())
        self.assertIn('theta=0.10',out.getvalue())
    def test_artifact_provenance(self):
        for name,item in json.loads((ROOT/'results/provenance.json').read_text()).items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),item['sha256'])
    def test_frozen_null_result_and_inference_units(self):
        s=json.loads((ROOT/'results/krr_statistics.json').read_text())
        self.assertEqual((s['n_datasets'],s['shot_repeats'],s['df'],len(s['contrasts'])),(12,100,11,24))
        self.assertEqual(s['failed_or_missing_cells'],0)
        self.assertTrue(all(r['holm_p']>=.05 for r in s['contrasts']))
        self.assertFalse(any(r['passes_practical_and_statistical_rule'] for r in s['contrasts']))
if __name__=='__main__':unittest.main()
