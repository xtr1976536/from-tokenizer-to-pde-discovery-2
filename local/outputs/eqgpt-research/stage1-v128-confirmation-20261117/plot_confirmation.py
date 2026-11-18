# -*- coding: utf-8 -*-
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
b=Path(__file__).resolve().parent
plt.style.use(b.parent/'stage1-tuning-20261116/analysis-v128/academic.mplstyle')
fig,axes=plt.subplots(2,2,figsize=(11,7.5),layout='constrained')
for ax,(scale,split) in zip(axes.flat,[(212,'811'),(212,'622'),(636,'811'),(636,'622')]):
 for seed,color in zip([525,526,527],['#725B88','#658F88','#B18B67']):
  d=json.loads((b/f'records/jobs/{scale}-{split}-v128-seed{seed}/training.json').read_text());h=d['history'];x=[v['epoch'] for v in h]
  ax.plot(x,[v['validation']['loss'] for v in h],color=color,lw=1.7,label=f'{seed} validation')
  ax.plot(x,[v['train']['loss'] for v in h],color=color,lw=1,ls='--',label=f'{seed} train')
  v=min(h,key=lambda v:v['validation']['loss']);ax.scatter([v['epoch']],[v['validation']['loss']],s=20,color=color,zorder=4)
 ax.axvline(20,color='#AAAAAA',lw=1,ls=':');ax.set_title(f"{scale} formulas | {'8:1:1' if split=='811' else '6:2:2'}",loc='left');ax.set_xlabel('Epoch');ax.set_ylabel('Token cross entropy');ax.set_xlim(1,55)
handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside lower center',ncol=3,fontsize=9)
fig.savefig(b/'confirmation_curves.png',dpi=240);fig.savefig(b/'confirmation_curves.pdf')
