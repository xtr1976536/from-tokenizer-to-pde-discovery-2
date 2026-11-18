import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
b=Path(__file__).resolve().parent
plt.style.use(b.parent/'stage1-tuning-20261116/analysis-v128/academic.mplstyle')
d=json.loads((b/'review.json').read_text());fig,axes=plt.subplots(2,2,figsize=(11,7.5),layout='constrained')
for ax,g in zip(axes.flat,d['summary']):
 for row,label,color in [(g['baseline'],'Previous','#99938C'),(g['winner'],'Candidate','#725B88')]:
  h=json.loads((b/'records/jobs'/row['job']/'training.json').read_text())['history'];x=[t['epoch'] for t in h]
  ax.plot(x,[t['validation']['loss'] for t in h],color=color,lw=1.8,label=label+' validation');ax.plot(x,[t['train']['loss'] for t in h],color=color,ls='--',lw=1.1,label=label+' train')
 w=g['winner'];ax.scatter([w['best_epoch']],[w['ce']],color='#725B88',s=25,zorder=5);ax.axvline(w['T'],color='#9AADA4',ls=':',lw=1);ax.set_title(f"EqGPT {g['scale']} | {'8:1:1' if g['split']=='811' else '6:2:2'}",loc='left');ax.set_xlabel('Epoch');ax.set_ylabel('Token cross entropy');ax.text(.98,.95,f"Best CE {w['ce']:.4f}\nGain {g['improvement_pct']:.2f}%\nRebound {w['rise_pct']:.2f}%",ha='right',va='top',transform=ax.transAxes,fontsize=9)
handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside lower center',ncol=4,fontsize=9);fig.savefig(b/'selected_vs_previous.png',dpi=240);fig.savefig(b/'selected_vs_previous.pdf')
