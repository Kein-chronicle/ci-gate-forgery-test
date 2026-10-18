import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RegressionTests(unittest.TestCase):
 def test_forgery_requires_positive_and_negative_fixtures(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'spec.json';p.write_text(json.dumps({'gates':[{'name':'empty','cmd':[sys.executable,'-c','pass']}]}))
   r=subprocess.run([sys.executable,str(ROOT/'scripts/forge_test.py'),str(p)],capture_output=True)
   self.assertNotEqual(r.returncode,0,'no fixtures cannot prove a gate')
 def test_forgery_runtime_errors_are_not_rejections(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'good').mkdir();(p/'bad').mkdir()
   (p/'gate.py').write_text('import sys\nsys.exit(0 if sys.argv[1].endswith("good") else 127)\n')
   spec={'gates':[{'name':'crash','cmd':[sys.executable,'gate.py','{target}'],'good':['good'],'bad':['bad']}]}
   (p/'spec.json').write_text(json.dumps(spec))
   r=subprocess.run([sys.executable,str(ROOT/'scripts/forge_test.py'),str(p/'spec.json')],capture_output=True)
   self.assertNotEqual(r.returncode,0,'exit 127 must not qualify as a finding')
if __name__=='__main__':unittest.main()
