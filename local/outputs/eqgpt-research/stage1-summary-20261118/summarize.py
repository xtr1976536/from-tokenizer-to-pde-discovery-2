# -*- coding: utf-8 -*-
import json,csv,collections,datetime
from pathlib import Path
b=Path(__file__).resolve().parent;d=json.loads((b/'snapshot.json').read_text());rows=d['records'];groups=collections.defaultdict(list)
for x in rows:groups[(x['scale'],x['split'],x['arm'],x['sampling'])].append(x)
summary=[]
for k,a in sorted(groups.items()):
 assert len({(x['seed'],x['case']) for x in a})==len(a)
 z=dict(scale=k[0],split=k[1],model=k[2],sampling=k[3],completed=len(a),expected=24,top1=sum(x['top1'] for x in a),top10=sum(x['top10'] for x in a),complete=len(a)==24)
 for seed in [525,526,527]:
  ss=[x for x in a if x['seed']==seed];z[f'seed{seed}']=f"{sum(x['top1'] for x in ss)}/{len(ss)};{sum(x['top10'] for x in ss)}/{len(ss)}"
 summary.append(z)
with (b/'per_model_summary.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
with (b/'per_case_results.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
time=datetime.datetime.fromtimestamp(d['timestamp'],datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec='seconds')
lines=['# 阶段1：逐模型结果汇总','',f'快照时间（北京时间）：{time}。只计有complete标记且result.json哈希通过校验的案例。每个完整配置24个案例-种子结果（8案例×3种子）。不将不同词表、采样或语料的结果合并成总体恢复率。','', '单元格均为Top1正确数／完成数；Top10正确数／完成数。Top10为正确结构进入最终Top10，非恰好生成过。当前只展示完成结果，未完成项不当作失败。','']
labels={'eqgpt_reference':'EqGPT','ast_bpe_96':'AST-BPE96','ast_bpe_128':'AST-BPE128','ast_bpe_160':'AST-BPE160'}
for scale in [212,636]:
 for split in ['811','622']:
  lines += [f'## {scale} / {split}','','|模型|采样|完成数|Top1|Top10|525（Top1;Top10）|526|527|','|---|---|---:|---:|---:|---|---|---|']
  for z in summary:
   if (z['scale'],z['split'])!=(scale,split):continue
   lines.append(f"|{labels[z['model']]}|{z['sampling']}|{z['completed']}/24|{z['top1']}/{z['completed']}|{z['top10']}/{z['completed']}|{z['seed525']}|{z['seed526']}|{z['seed527']}|")
lines += ['','## 配对口径','','AST model为纯模型采样；EqGPT eqgpt_model为关闭均匀随机混合但保留原SAT约束的模型概率采样。EqGPT legacy与AST mix20都为token级20%随机混合，EqGPT仍有SAT约束，不能说完全隔离分词器因果效应。旧预训练参数历史实验未纳入本表；本表是新版模型与当前采样对照。','', '混合采样只有部分配置齐全；完整24案例配置可直接配对，未齐配置需按交集单独比较，不能以分母不同的计数排名。']
(b/'SUMMARY.md').write_text('\n'.join(lines));print(time)
for z in summary:print(z['scale'],z['split'],z['model'],z['sampling'],z['completed'],z['top1'],z['top10'],z['seed525'],z['seed526'],z['seed527'])
