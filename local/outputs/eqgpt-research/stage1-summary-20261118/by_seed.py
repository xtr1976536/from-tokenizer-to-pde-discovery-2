# -*- coding: utf-8 -*-
import json,csv,collections
from pathlib import Path
b=Path(__file__).resolve().parent;d=json.loads((b/'snapshot.json').read_text());rows=d['records'];groups=collections.defaultdict(list)
for x in rows:groups[(x['scale'],x['split'],x['seed'],x['arm'],x['sampling'])].append(x)
labels={'ast_bpe_96':'AST-BPE 96','ast_bpe_128':'AST-BPE 128','ast_bpe_160':'AST-BPE 160','eqgpt_reference':'EqGPT'};out=[]
lines=['# 阶段1：每个种子独立比较','','使用2026-11-18 10:56北京时间的已核验快照，不合并种子。每个完整单元为8个PDE案例。下文Top1/Top10分别为正确案例数；未完成配置不以缺失案例作为错误。','']
for scale in [212,636]:
 for split in ['811','622']:
  lines += [f'## {scale}条语料 / {split} / 纯模型采样','','|种子|模型|完成|Top1|Top10|','|---:|---|---:|---:|---:|']
  for seed in [525,526,527]:
   for arm in ['eqgpt_reference','ast_bpe_96','ast_bpe_128','ast_bpe_160']:
    sampling='eqgpt_model' if arm=='eqgpt_reference' else 'model';a=groups.get((scale,split,seed,arm,sampling),[]);assert len(a)==8
    z=dict(scale=scale,split=split,seed=seed,model=labels[arm],sampling=sampling,completed=len(a),top1=sum(x['top1'] for x in a),top10=sum(x['top10'] for x in a));out.append(z);lines.append(f"|{seed}|{labels[arm]}|8/8|{z['top1']}/8|{z['top10']}/8|")
lines+=['','## EqGPT：各种子独立比较采样方式','','|语料|划分|种子|纯模型Top1|纯模型Top10|20%混合Top1|20%混合Top10|','|---|---|---:|---:|---:|---:|---:|']
for scale in [212,636]:
 for split in ['811','622']:
  for seed in [525,526,527]:
   a=groups[(scale,split,seed,'eqgpt_reference','eqgpt_model')];m=groups[(scale,split,seed,'eqgpt_reference','legacy')];assert len(a)==len(m)==8
   lines.append(f"|{scale}|{split}|{seed}|{sum(x['top1'] for x in a)}/8|{sum(x['top10'] for x in a)}/8|{sum(x['top1'] for x in m)}/8|{sum(x['top10'] for x in m)}/8|")
   out.append(dict(scale=scale,split=split,seed=seed,model='EqGPT',sampling='legacy',completed=8,top1=sum(x['top1'] for x in m),top10=sum(x['top10'] for x in m)))
lines+=['','## AST-BPE：当前混合采样按种子独立比较','','只展示存在混合采样完成结果的配置；纯模型列只取与混合采样已完成案例相同的案例交集。','', '|语料|划分|种子|词表|混合完成|同案例纯模型Top1/Top10|混合Top1/Top10|','|---|---|---:|---:|---:|---|---|']
for scale in [212,636]:
 for split in ['811','622']:
  for seed in [525,526,527]:
   for arm in ['ast_bpe_96','ast_bpe_128','ast_bpe_160']:
    mix=groups.get((scale,split,seed,arm,'mix20'),[])
    if not mix:continue
    cases={x['case'] for x in mix};pure=[x for x in groups[(scale,split,seed,arm,'model')] if x['case'] in cases];assert len(pure)==len(mix)
    lines.append(f"|{scale}|{split}|{seed}|{arm.split('_')[-1]}|{len(mix)}/8|{sum(x['top1'] for x in pure)}/{len(pure)}；{sum(x['top10'] for x in pure)}/{len(pure)}|{sum(x['top1'] for x in mix)}/{len(mix)}；{sum(x['top10'] for x in mix)}/{len(mix)}|")
    out.append(dict(scale=scale,split=split,seed=seed,model=labels[arm],sampling='mix20',completed=len(mix),top1=sum(x['top1'] for x in mix),top10=sum(x['top10'] for x in mix)))
lines+=['','EqGPT纯模型仍保留SAT语法约束，只关闭均匀随机token混合；AST纯模型不引入EqGPT同类SAT约束。全部为调参后预训练模型的下游结果，不是与旧预训练设置的直接比较。未完成混合任务须后续更新，不能当作最终指标。']
(b/'BY_SEED.md').write_text('\n'.join(lines))
with (b/'by_seed.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
print('\n'.join(lines))
