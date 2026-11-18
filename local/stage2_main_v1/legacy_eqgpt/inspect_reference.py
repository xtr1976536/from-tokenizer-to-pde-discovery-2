"""Inspect the frozen old EQGPT assets without training or modifying them."""
from pathlib import Path
import hashlib,json

def inspect():
 base=Path(__file__).resolve().parent;reference=json.loads((base/'REFERENCE.json').read_text())
 missing=[]
 for rel,expected in reference['files_sha256'].items():
  p=base/rel
  if not p.exists():
   if not (rel.startswith('checkpoint/') or '/.native_cache/' in rel):raise ValueError('Missing reference source: '+rel)
   missing.append(rel);continue
  if hashlib.sha256(p.read_bytes()).hexdigest()!=expected:raise ValueError('Reference hash mismatch: '+rel)
 return {'version':reference['version'],'fields':reference['fields'],'equation_count':reference['equation_count'],
         'all_present_files_hash_verified':True,'server_only_assets_not_mirrored_locally':missing,
         'new_eqgpt_training_started':False}
if __name__=='__main__':print(json.dumps(inspect(),indent=2))
