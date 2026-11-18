import sys,json,random,re,csv,hashlib
from pathlib import Path
from collections import defaultdict
import numpy as np
HERE=Path(__file__).resolve().parent
SRC=HERE.parent/'repository-update-20261115'
sys.path.insert(0,str(SRC/'src'))
from math_tokenizer.eqgpt.latex_codec import structure_to_latex,LatexParser,key
from math_tokenizer.eqgpt.compact_alphabet import CompactAlphabet
from math_tokenizer.hard_ast_2026 import HardASTBPE
SIZES=list(range(64,481,32))
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2))
def metrics(model,texts):
 used=set();initial=final=ct=cg=nt=ng=0
 for text in texts:
  ids=model.encode(text);assert model.decode(ids)==text
  used.update(ids);initial+=len(text.encode());final+=len(ids)
  cuts=set(np.cumsum([len(model.vocab[i]) for i in ids]))
  for pat,typ in [(r'\\[A-Za-z]+','c'),(r'[0-9]+(?:\.[0-9]+)?','n')]:
   for m in re.finditer(pat,text):
    good=not any(len(text[:m.start()].encode())<v<len(text[:m.end()].encode()) for v in cuts)
    if typ=='c':ct+=1;cg+=good
    else:nt+=1;ng+=good
 added={i for i,v in enumerate(model.vocab) if len(v)>1}
 return dict(compression=initial/final,command_integrity=cg/max(ct,1),number_integrity=ng/max(nt,1),added_token_usage=len(used&added)/max(len(added),1),initial_tokens=initial,final_tokens=final,commands=ct,numbers=nt,roundtrip=len(texts))
def main():
 allrows=[]
 for scale in (212,636):
  sources=[json.loads(l) for l in (SRC/f'restarts/stage01_20261113/stage1/corpora/{scale}/sources.jsonl').read_text().splitlines()]
  groups=defaultdict(list)
  for r in sources:groups[repr(key(LatexParser(structure_to_latex(r['gre_ids'])).parse()))].append(r)
  for split,ratios in [('811',[.8,.1,.1]),('622',[.6,.2,.2])]:
   folder=HERE/'upstream'/str(scale)/split;folder.mkdir(parents=True,exist_ok=True)
   rng=random.Random(525);best=None
   for _ in range(1000):
    order=list(groups);rng.shuffle(order);order.sort(key=lambda k:-len(groups[k]));parts=[[],[],[]]
    for k in order:
     costs=[]
     for i in range(3):costs.append(sum((len(parts[j])+(len(groups[k]) if i==j else 0)-scale*ratios[j])**2 for j in range(3)))
     i=min(range(3),key=lambda j:(costs[j],rng.random()));parts[i].extend(groups[k])
    cost=sum((len(parts[j])-scale*ratios[j])**2 for j in range(3))
    if best is None or cost<best[0]:best=(cost,parts)
   parts=best[1];manifest=dict(scale=scale,split=split,ratios=ratios,seed=525,grouping='canonical AST, commutative add/mul; whole-group size balancing',counts=dict(zip(['train','validation','test'],map(len,parts))),ids={n:[r['source_id'] for r in p] for n,p in zip(['train','validation','test'],parts)})
   dump(folder/'split.json',manifest)
   for n,p in zip(['train','validation','test'],parts):
    (folder/(n+'.jsonl')).write_text(''.join(json.dumps(r)+'\n' for r in p))
   texts=[structure_to_latex(r['gre_ids']) for r in parts[0]];validation=[structure_to_latex(r['gre_ids']) for r in parts[1]]
   alphabet=json.loads((SRC/'restarts/stage01_20261113/stage1/assets/legacy_alphabet_212.json').read_text())['alphabet']
   dump(folder/'protocol.json',dict(sizes=SIZES,metrics=['compression','command_integrity','number_integrity','added_token_usage'],selection='validation only; no integrity threshold; Pareto and balanced rank analysis',alphabet=alphabet,test_metrics_read=False))
   largest=HardASTBPE.train(texts,max(SIZES)+256-len(alphabet)-3)
   results=[]
   for capacity in SIZES:
    n=capacity+256-len(alphabet)-3
    if len(largest.vocab)<n:
     results.append(dict(scale=scale,split=split,vocab_size=capacity,status='unfilled'));continue
    merges=[]
    for m in largest.merges:
     if max(m)>=n:break
     merges.append(m)
    model=CompactAlphabet('ast_bpe',alphabet,HardASTBPE(largest.vocab[:n],merges));assert len(model.vocab)+3==capacity
    model.save(folder/f'ast-bpe-{capacity}.json')
    row=dict(scale=scale,split=split,vocab_size=capacity,status='ok',**metrics(model,validation));results.append(row);allrows.append(row)
   dump(folder/'four-metrics.json',results)
   dump(HERE/'upstream-progress.json',dict(completed=f'{scale}/{split}',rows=len(allrows)))
   print(scale,split,manifest['counts'],'capacities',len(results),flush=True)
 dump(HERE/'upstream-results.json',allrows)
 with (HERE/'UPSTREAM_TABLES.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(allrows[0]));w.writeheader();w.writerows(allrows)
if __name__=='__main__':main()
