"""Validate all histories and produce within-vocabulary and cross-vocabulary tables."""
import json,csv,statistics,math
from pathlib import Path
b=Path(__file__).resolve().parent;rows=[];histories={}
for p in sorted((b/'jobs').glob('*/training.json')):
 d=json.loads(p.read_text());h=d['history'];s=d['settings'];c=json.loads((p.parent/'COMPLETE.json').read_text());v=[x['validation']['loss'] for x in h];i=min(range(len(h)),key=lambda i:v[i]);n=len(h);selected='-selected-' in p.parent.name
 assert c['epochs']==n and d['best_epoch']==c['best_epoch']==h[i]['epoch'] and abs(min(v)-d['best_validation_loss'])<1e-10
 assert all(math.isfinite(x['validation']['loss']) and math.isfinite(x['train']['loss']) for x in h)
 if selected:
  assert n>=30 and all(math.isclose(x['learning_rate'],1e-6,abs_tol=1e-16) for x in h[20:])
 row=dict(job=p.parent.name,scale=d['scale'],split=p.parent.name.split('-')[1],vocab=int(d['arm'].split('_')[-1]),seed=s['seed'],selected=selected,epochs=n,best_epoch=h[i]['epoch'],best_ce=min(v),best_npb=h[i]['validation']['nats_per_byte'],train_at_best=h[i]['train']['loss'],gap_at_best=min(v)-h[i]['train']['loss'],rise_pct=100*(v[-1]/min(v)-1),tail10_change_pct=100*(v[-1]/v[-min(10,n)]-1),at_cap=n==s['max_epochs'])
 rows.append(row);histories[row['job']]=d
assert len(rows)==32
summary=[]
for scale in [212,636]:
 for split in ['811','622']:
  for vocab in [96,160]:
   a=[x for x in rows if x['scale']==scale and x['split']==split and x['vocab']==vocab];base=next(x for x in a if not x['selected']);sel=[x for x in a if x['selected']];paired=next(x for x in sel if x['seed']==525)
   summary.append(dict(scale=scale,split=split,vocab=vocab,ce_mean=statistics.mean(x['best_ce'] for x in sel),ce_sd=statistics.stdev(x['best_ce'] for x in sel),npb_mean=statistics.mean(x['best_npb'] for x in sel),npb_sd=statistics.stdev(x['best_npb'] for x in sel),seed525_improvement_pct=100*(1-paired['best_ce']/base['best_ce']),max_rise_pct=max(x['rise_pct'] for x in sel),max_gap=max(x['gap_at_best'] for x in sel),capped=sum(x['at_cap'] for x in sel),flags=[x['job'] for x in sel if x['rise_pct']>1 or (x['at_cap'] and x['tail10_change_pct']<-.05)]))
with (b/'per_run_analysis.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(b/'analysis.json').write_text(json.dumps(dict(rows=rows,summary=summary),indent=2))
lines=['# Vocabulary96/160 validation results','','Paired improvements compare seed525 selected and previous strategy on identical vocabulary and split. Three-seed SD is descriptive, not a significance test. Cross-vocabulary comparisons use NLL per rendered byte (NPB), not token CE. Flags are triage only; train-validation gaps require inspection.','','|Scale|Split|Vocab|CE mean +/- SD|NPB mean +/- SD|Paired improvement|Max rebound|Capped|','|---|---|---:|---:|---:|---:|---:|---:|']
for x in summary:lines.append(f"|{x['scale']}|{x['split']}|{x['vocab']}|{x['ce_mean']:.6f} +/- {x['ce_sd']:.6f}|{x['npb_mean']:.6f} +/- {x['npb_sd']:.6f}|{x['seed525_improvement_pct']:.3f}%|{x['max_rise_pct']:.3f}%|{x['capped']}|")
lines+=['','Inspect flagged histories and cap trends before declaring training adequate or accepting shared parameters. Do not automatically launch additional tuning or downstream PDE search.']
(b/'ANALYSIS.md').write_text('\n'.join(lines));print(json.dumps(summary,indent=2))
# Common byte-normalized comparison with the completed vocabulary128 validation.
reference=json.loads((b/'v128_reference.json').read_text())['summary'];comparison=[]
for x in summary:comparison.append({k:x[k] for k in ['scale','split','vocab','npb_mean','npb_sd','max_rise_pct']})
for x in reference:comparison.append(dict(scale=x['scale'],split=x['split'],vocab=128,npb_mean=x['npb_mean'],npb_sd=x['npb_sd'],max_rise_pct=x['max_rise_pct']))
comparison.sort(key=lambda x:(x['scale'],x['split'],x['vocab']));(b/'three_vocab_comparison.json').write_text(json.dumps(comparison,indent=2))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(2,4,figsize=(16,7),layout='constrained')
for rowi,vocab in enumerate([96,160]):
 for coli,(scale,split) in enumerate([(212,'811'),(212,'622'),(636,'811'),(636,'622')]):
  ax=axes[rowi,coli]
  for seed,color in zip([525,526,527],['#725B88','#658F88','#B18B67']):
   d=histories[f'{scale}-{split}-v{vocab}-selected-seed{seed}'];h=d['history'];xx=[x['epoch'] for x in h]
   ax.plot(xx,[x['validation']['nats_per_byte'] for x in h],color=color,lw=1.5,label=f'{seed} validation')
   ax.plot(xx,[x['train']['nats_per_byte'] for x in h],color=color,lw=1,ls='--',label=f'{seed} train')
  ax.set_title(f'V{vocab} | {scale} | {split}');ax.set_xlabel('Epoch');ax.set_ylabel('NLL per byte');ax.grid(alpha=.12)
handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside lower center',ncol=3)
fig.savefig(b/'validation_curves.png',dpi=220);fig.savefig(b/'validation_curves.pdf')
