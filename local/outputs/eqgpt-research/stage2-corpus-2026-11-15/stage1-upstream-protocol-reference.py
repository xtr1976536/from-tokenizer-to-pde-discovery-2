import csv,gzip,json,hashlib,re,time
from collections import Counter
from pathlib import Path
from math_tokenizer.corpus import ROOT
from math_tokenizer.structure_v2 import complexity
from math_tokenizer.pde_protocol import split_corpus
from math_tokenizer.eqgpt.compact_alphabet import CompactAlphabet,train_compact
from math_tokenizer.eqgpt.latex_codec import structure_to_latex
from scripts.upstream_metrics import measure,token_coverage
from scripts.upstream_tokenizers import load
OUT=ROOT/'restarts/stage01_20261113/paper_upstream636_20261114';OUT.mkdir(exist_ok=True)
SIZES=[100,120,150,200,250,256,300,350,400,450,500,512];TARGETS=[300,450]
alphabet=json.loads((ROOT/'restarts/stage01_20261113/stage1/636/tokenizers/300.model.json').read_text())['alphabet'];source=ROOT/'data/formulas/636/sources.jsonl';records=[json.loads(x) for x in source.read_text().splitlines()];rows=[]
def digest(b):return hashlib.sha256(b).hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
for r in records:
 text=structure_to_latex(r['gre_ids']);symbols={};tokens=[]
 for v in re.findall(r'\\[A-Za-z]+|\\[^A-Za-z]|[0-9]+(?:\.[0-9]+)?|[^\s]',text):
  if re.fullmatch('[A-Za-z]',v):symbols.setdefault(v,len(symbols));tokens.append('S'+str(symbols[v]))
  elif v[0:1].isdigit():tokens.append('N')
  else:tokens.append(v)
 rows.append(dict(id=r['source_id'],latex=text,source_group=r['source_group'],template_sha256=digest(''.join(tokens).encode()),canonical_sha256=digest(re.sub(r'\s+','',text).encode()),complexity=complexity(text)))
for i,r in enumerate(sorted(rows,key=lambda x:(x['complexity']['score'],x['id']))):r['complexity_bin']='simple' if i<len(rows)*.3 else 'moderate' if i<len(rows)*.7 else 'complex'
assert len(rows)==636 and all(set(r['latex'].encode())<=set(alphabet) for r in rows)
plans,split=split_corpus(rows);protocol=dict(source_sha256=digest(source.read_bytes()),records=636,representation='same structure_to_latex(gre_ids) as downstream',alphabet=alphabet,fit='unaugmented upstream training formulas only',sizes=SIZES,predeclared_test_capacities=TARGETS,baselines=['qwen2.5','llama3','o200k_base'],split=split)
dump(OUT/'protocol.json',protocol);dump(OUT/'input_records.json',rows);dump(OUT/'split_ids.json',{k:[r['id'] for r in rr] for k,rr in plans.items()})
results=[];usage=[]
def evaluate(model,rr,protocol_name,name,split_name):
 start=time.perf_counter();summary,details,counts=measure(model,rr);summary.update(protocol=protocol_name,method=name,split=split_name,vocab_size=model.capacity+3 if hasattr(model,'capacity') else model.vocab_size,encoding_metric_seconds=time.perf_counter()-start)
 p=OUT/protocol_name/(name+'.'+split_name);dump(Path(str(p)+'.json'),summary)
 with gzip.open(str(p)+'.per_formula.jsonl.gz','wt') as f:
  for d in details:f.write(json.dumps(d)+'\n')
 # Reaggregate saved per-formula metric counts independently.
 n=sum(x['initial_character_tokens'] for x in details);den=sum(x['final_tokens'] for x in details);assert abs(n/den-summary['compression_ratio'])<1e-12
 results.append(summary)
 if hasattr(model,'vocab'):
  count,coverage,papers=token_coverage(model,rr);learned=[i for i,b in enumerate(model.vocab) if len(b)>1];M=len(learned);used=sum(count[i]>0 for i in learned)
  us=dict(protocol=protocol_name,method=name,split=split_name,total_ids=len(model.vocab)+3,learned=M,used=used,unused=M-used,usage_rate=used/M,unused_rate=(M-used)/M,**{f'low_1_{k}_rate':sum(1<=count[i]<=k for i in learned)/M for k in [2,5,10]});usage.append(us)
  with (OUT/protocol_name/(name+'.'+split_name+'.tokens.csv')).open('w',newline='') as f:
   w=csv.writer(f);w.writerow(['id','kind','hex','count','frequency','formula_count','formula_coverage'])
   for i,b in enumerate(model.vocab):w.writerow([i,'base' if len(b)==1 else 'learned',b.hex(),count[i],count[i]/sum(count.values()),coverage[i],coverage[i]/len(rr)])
 return summary
for pname,train,valid,test in [('811',plans['train'],plans['validation'],plans['test']),('simple_to_complex',[r for r in plans['train'] if r['complexity_bin']=='simple'],[r for r in plans['validation'] if r['complexity_bin']=='complex'],[r for r in plans['test'] if r['complexity_bin']=='complex'])]:
 assert train and valid and test;folder=OUT/pname;folder.mkdir(exist_ok=True);dump(folder/'split_ids.json',{k:[r['id'] for r in rr] for k,rr in [('train',train),('validation',valid),('test',test)]})
 for size in (SIZES if pname=='811' else TARGETS):
  model=train_compact('ast_bpe',[r['latex'] for r in train],size,alphabet);name=f'ast_bpe_{size}';model.save(folder/(name+'.model.json'))
  for split_name,rr in [('train',train),('validation',valid)]:evaluate(model,rr,pname,name,split_name)
  if size in TARGETS:evaluate(model,test,pname,name,'test')
  print('DONE',pname,name,flush=True)
 for name in ['qwen2.5','llama3','o200k_base']:
  model=load(name)
  for split_name,rr in [('validation',valid),('test',test)]:evaluate(model,rr,pname,name,split_name)
  print('BASELINE_DONE',pname,name,flush=True)
dump(OUT/'results.json',results);dump(OUT/'usage.json',usage);dump(OUT/'COMPLETE.json',dict(status='PASS',protocols=['811','simple_to_complex'],records=636,base_bytes=len(alphabet),split_counts={k:len(v) for k,v in plans.items()},result_rows=len(results),usage_rows=len(usage),predeclared_test_sizes=TARGETS));print('UPSTREAM636_COMPLETE',flush=True)
