import math,json,csv
from pathlib import Path
r=Path(__file__).resolve().parent;rows=[];histories={}
for p in sorted((r/'jobs').glob('*/training.json')):
 d=json.loads(p.read_text());s=d['settings'];h=d['history'];c=json.loads((p.parent/'COMPLETE.json').read_text());best=min(h,key=lambda x:x['validation']['loss']);v=[x['validation']['loss'] for x in h];baseline='-baseline-' in p.parent.name
 assert len(h)==c['epochs'] and best['epoch']==d['best_epoch']==c['best_epoch'] and math.isclose(best['validation']['loss'],d['best_validation_loss'])
 assert all(math.isfinite(x['validation']['loss']) and math.isfinite(x['train']['loss']) for x in h)
 if not baseline:
  assert len(h)>=30
  assert all(math.isclose(x['learning_rate'],1e-6,abs_tol=1e-16) for x in h[s['T_max']:])
 row=dict(job=p.parent.name,scale=d['scale'],split=p.parent.name.split('-')[1],baseline=baseline,lr=s['lr'],l2=s['l2_matrix'],T=s['T_max'],epochs=len(h),best_epoch=best['epoch'],best_ce=min(v),best_npb=best['validation']['nats_per_byte'],gap_ce=min(v)-best['train']['loss'],rise_pct=100*(v[-1]/min(v)-1),tail10_change_pct=100*(v[-1]/v[-10]-1),capped=len(h)==s['max_epochs']);rows.append(row);histories[row['job']]=d
assert len(rows)==76
with (r/'all_runs.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary=[]
for scale in [212,636]:
 for split in ['811','622']:
  group=[x for x in rows if (x['scale'],x['split'])==(scale,split)];base=next(x for x in group if x['baseline']);candidates=sorted([x for x in group if not x['baseline']],key=lambda x:x['best_ce']);summary.append(dict(scale=scale,split=split,old_strategy=base,ranked_candidates=candidates,flags=[x['job'] for x in candidates if x['rise_pct']>1 or (x['capped'] and x['tail10_change_pct']<-.05)]))
(r/'analysis.json').write_text(json.dumps(dict(summary=summary,scope='seed525 only; no test data; inspect convergence and gap before selecting; no automatic downstream launch'),indent=2))
# Retain complete train/validation curves for all settings, six pages per cohort.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
with PdfPages(r/'all_curves.pdf') as pdf:
 for group in summary:
  candidates=group['ranked_candidates']
  for offset in range(0,len(candidates),6):
   fig,axes=plt.subplots(2,3,figsize=(13,7),layout='constrained')
   for ax,row in zip(axes.flat,candidates[offset:offset+6]):
    h=histories[row['job']]['history'];xx=[x['epoch'] for x in h];ax.plot(xx,[x['train']['loss'] for x in h],ls='--',label='Train',color='#658F88');ax.plot(xx,[x['validation']['loss'] for x in h],label='Validation',color='#725B88');ax.set_title(f"LR{row['lr']:g} L2{row['l2']:g} T{row['T']}");ax.set_xlabel('Epoch');ax.set_ylabel('Token CE');ax.legend()
   fig.suptitle(f"EqGPT {group['scale']} | {group['split']} | seed525");pdf.savefig(fig);plt.close(fig)
print('76 records audited; candidates require human/model review before selection.')
