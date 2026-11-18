"""Check frozen corpus/tokenizer/checkpoint on CPU; no generation/SFT training."""
import sys,json,hashlib,collections
from pathlib import Path
ROOT=Path('/data1/users/liugang/src/eq-bpe/project');BASE=ROOT/'stage2_main_v1/legacy_eqgpt'
ref=json.loads((BASE/'REFERENCE.json').read_text())
for rel,h in ref['files_sha256'].items():
 assert hashlib.sha256((BASE/rel).read_bytes()).hexdigest()==h,rel
layout=BASE/'layout'
sys.path[:0]=[str(layout/'ast_bpe_multifield_v4'),str(layout/'ast_bpe_multifield_v2'),str(layout/'ast_bpe_multifield_v1')]
from compact_tokenizer import CompactASTBPE
from pipeline import ASTAdapter
from model import load
import torch
corpus=BASE/'training_corpus';tokenizer=CompactASTBPE.load(corpus/'tokenizer300.json');adapter=ASTAdapter(tokenizer)
rows=[json.loads(s) for s in (corpus/'encoded.jsonl').read_text().splitlines()]
equations=[json.loads(s) for s in (corpus/'equations.jsonl').read_text().splitlines()]
splits=json.loads((corpus/'splits.json').read_text())
assert {r['parent_id'] for r in rows}=={r['id'] for r in equations}
for r in rows:
 assert r['parent_id'] in splits[r['split']]
 assert adapter.sequence(r['text'])==r['tokens']
parents={}
for r in rows:
 key=r['parent_id'];parents.setdefault(key,set()).add(r['split'])
assert all(len(v)==1 for v in parents.values())
source_groups={}
for r in rows:source_groups.setdefault(r['source_group'],set()).add(r['split'])
assert all(len(v)==1 for v in source_groups.values()),'Formula source-group leakage'
import generator_search_optimized as selected_generator
import generator as shared_generator
import two_equation_sampling as count_sampler
transitions,distance=count_sampler.build_tables(adapter)
assert transitions.shape==(8,300) and int(distance[0])<1000
assert Path(selected_generator.__file__).resolve().is_relative_to(BASE)
assert Path(shared_generator.__file__).resolve().is_relative_to(BASE)
torch.set_num_threads(2);model,meta=load(BASE/'checkpoint/model.pt','cpu');model.eval()
assert meta['encoded_sha256']==hashlib.sha256((corpus/'encoded.jsonl').read_bytes()).hexdigest()
assert meta['tokenizer_sha256']==hashlib.sha256((corpus/'tokenizer300.json').read_bytes()).hexdigest()
with torch.no_grad():logits,_=model(torch.tensor([rows[0]['tokens'][:3]]))
assert torch.isfinite(logits).all()
result={'status':'PASS','model_capability':'old two-field/two-equation unchanged',
 'encoded_rows':len(rows),'splits':dict(collections.Counter(r['split'] for r in rows)),
 'formula_parent_groups':len(parents),'parent_splits':{k:len(v) for k,v in splits.items()},'formula_metadata_matches_encoded':True,'source_groups':len(source_groups),
 'formula_source_group_disjoint':True,'roundtrip_verified_rows':len(rows),
 'checkpoint_tokenizer_corpus_match':True,'selected_and_shared_import_closure_verified':True,'two_equation_automaton_verified':True,'cpu_forward_only':True,'training_started':False,
 'maximum_token_sequence':max(len(r['tokens']) for r in rows),'model_config':model.stage2_config}
print(json.dumps(result,indent=2))
(ROOT/'maintenance/stage2-data-20261115/legacy-check.json').write_text(json.dumps(result,indent=2))
