"""Freeze source/structure groups before training-only augmentation or vocab fitting."""
import json,random,math,re,argparse
from pathlib import Path
from collections import Counter,defaultdict
from hashlib import sha256
from curation import OUT
from structure_latex import normalize_system
from latex_render import latex


def skeleton(n):
    if n[0]=='pow':return ('power',skeleton(n[1]))
    if n[0]=='n':return ('n',0 if n[1]==0 else 1)
    return (n[0],*(skeleton(v) if isinstance(v,(tuple,list)) else v for v in n[1:]))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--ratios',nargs=3,type=float,default=[.8,.1,.1]);ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    if abs(sum(args.ratios)-1)>1e-8 or min(args.ratios)<=0:raise ValueError('Three positive ratios must sum to1')
    raw=(OUT/'reviewed-unique-structures.jsonl').read_bytes()
    rows=[json.loads(l) for l in raw.decode().splitlines()]
    audit=json.loads((OUT/'reviewed-corpus-audit.json').read_text())
    assert sha256(raw).hexdigest()==audit['input_corpus_sha256']
    assert len(rows)>=212 and sum(len(r['source_fields'])==3 for r in rows)>=80
    review=json.loads((OUT/'mathematical-review.json').read_text())
    assert review['input_corpus_sha256']==sha256(raw).hexdigest() and review['status']=='PASS'
    parent={r['source_group']:r['source_group'] for r in rows}
    def find(a):
        parent.setdefault(a,a)
        if parent[a]!=a:parent[a]=find(parent[a])
        return parent[a]
    def union(a,b):
        a,b=find(a),find(b)
        if a!=b:parent[max(a,b)]=min(a,b)
    by_key={}
    # Include alternate-source duplicates which were excluded from the count.
    declarations=[json.loads(l) for l in (OUT/'reviewed-source-models.jsonl').read_text().splitlines()]
    for r in declarations:
        if r['count_key'] in by_key:union(r['source_group'],by_key[r['count_key']])
        by_key[r['count_key']]=r['source_group']
    near={}
    for r in rows:
        # Remove numeric exponent choices while preserving differential orders,
        # functions and field coupling; field/axis invariant source count-key
        # still supplies exact-equivalence grouping above.
        k=repr(sorted((skeleton(n) for n in r['normalized']['residual_support_ast']),key=repr))
        if k in near:union(r['source_group'],near[k])
        near[k]=r['source_group']
    groups=defaultdict(list)
    for r in rows:groups[find(r['source_group'])].append(r)
    totals=Counter(len(r['source_fields']) for r in rows)
    targets=args.ratios
    def loss(counts):
        # Absolute count deviations avoid over-weighting the smaller roles and
        # assigning a large source group to validation merely to fill it early.
        return sum((sum(c.values())-len(rows)*q)**2+
                   .2*sum((c[n]-totals[n]*q)**2 for n in totals)
                   for c,q in zip(counts,targets))
    best=None
    # Only group sizes and variable counts enter this deterministic balance
    # optimization; no tokenizer metrics or test outcomes are available here.
    rng=random.Random(525)
    for trial in range(3000):
        order=list(groups);rng.shuffle(order);order.sort(key=lambda g:-len(groups[g]))
        counts=[Counter(),Counter(),Counter()];assign={}
        for g in order:
            c=Counter(len(r['source_fields']) for r in groups[g])
            options=[]
            for i in range(3):
                temp=[x.copy() for x in counts];temp[i].update(c)
                options.append(loss(temp))
            k=min(range(3),key=lambda i:(options[i],rng.random()))
            counts[k].update(c);assign[g]=k
        score=loss(counts)
        if best is None or score<best[0]:best=(score,assign,counts)
    _,assign,counts=best
    assert all(c[3]>=3 for c in counts),counts
    split={name:[r['id'] for r in rows if assign[find(r['source_group'])]==i] for i,name in enumerate(('train','validation','test'))}
    output=args.output or OUT/'frozen';output.mkdir(exist_ok=True,parents=True)
    frozen=[]
    for r in rows:
        r=dict(r);r['review_status']='MATHEMATICAL_REVIEW_COMPLETE_FROZEN_PREPARATION_V1'
        r['split']=next(name for name,ids in split.items() if r['id'] in ids)
        r['leakage_group']=find(r['source_group']);frozen.append(r)
    (output/'base-structures.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in frozen))
    manifest=dict(seed=525,input_corpus_sha256=sha256(raw).hexdigest(),target_ratios=targets,
                  counts={k:len(v) for k,v in split.items()},field_counts={k:dict(c) for k,c in zip(split,counts)},
                  group_count=len(groups),source_groups_disjoint=True,near_power_structure_groups_disjoint=True,
                  duplicate_alternate_source_groups_linked=True,ids=split,
                  base_sha256=sha256((output/'base-structures.jsonl').read_bytes()).hexdigest(),
                  rule='Whole source groups, alternate-source duplicates and power-erased structural groups stay together; deterministic size/field balancing only')
    for name in split:
        selected=[r for r in frozen if r['split']==name]
        (output/(name+'.jsonl')).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in selected))
    def permute(n,rng):
        children=[permute(v,rng) if isinstance(v,(list,tuple)) else v for v in n[1:]]
        if n[0] in ('add','mul'):rng.shuffle(children)
        return (n[0],*children)
    augmented=[]
    for r in frozen:
        if r['split']!='train':continue
        seen={r['normalized']['text']};variants=[r['normalized']['text']]
        rng=random.Random(int(sha256(r['id'].encode()).hexdigest()[:16],16))
        for _ in range(320):
            text=(chr(92)*2).join(latex(permute(n,rng))+'=0' for n in r['normalized']['residual_support_ast'])
            if text in seen:continue
            assert normalize_system(text.split(chr(92)*2),r['normalized']['fields'])['text']==r['normalized']['text'],r['id']
            seen.add(text);variants.append(text)
            if len(variants)>=32:break
        augmented.extend(dict(parent_id=r['id'],split='train',text=t,variant=i) for i,t in enumerate(variants))
    (output/'train-augmented.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in augmented))
    manifest['augmentation']=dict(kind='term/factor permutations',maximum_per_parent=32,count=len(augmented),
                                  validation_augmented=False,test_augmented=False,
                                  every_variant_reparsed_and_canonicalized=True)
    (output/'split-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in manifest.items() if k not in ('ids',)},ensure_ascii=False))


if __name__=='__main__':main()
