"""Reparse original coefficient-bearing equations; no blind reuse of old normalization."""
from pathlib import Path
import json,collections
from structure_latex import normalize_system,structure_key
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/eqgpt-research/stage2-corpus-2026-11-15'
rows=[json.loads(l) for l in (ROOT/'stage2_main_v1/legacy_eqgpt/training_corpus/equations.jsonl').read_text().splitlines()]
parsed=[];rejected=[]
for r in rows:
 source=r.get('source_parameterized_equations')
 if not source:rejected.append({'id':r['id'],'reason':'no coefficient-bearing equation list; extract again from source'});continue
 try:
  n=normalize_system(source,r['fields']);key=structure_key(n['residual_support_ast'],n['fields'])
  parsed.append({'old_id':r['id'],'source_group':r['source_group'],'source_url':r['source_url'],'title':r['title'],'family':r['family'],
   'original_equations':source,'normalized':n,'structure_key':key,'source_context':r.get('source_context'),
   'status':'REPARSED_NOT_ADMITTED; source-native2D, leakage and completeness review still required'})
 except (ValueError,TypeError,IndexError,KeyError) as e:rejected.append({'id':r['id'],'reason':str(e)})
(OUT/'reparsed-original-candidates.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in parsed))
(OUT/'reparse-rejections.json').write_text(json.dumps(rejected,indent=2,ensure_ascii=False))
print('REPARSED',len(parsed),'REJECTED',len(rejected),'UNIQUE_SUPPORTS',len({r['structure_key'] for r in parsed}),'FIELDS',dict(collections.Counter(len(r['normalized']['fields']) for r in parsed)))
