# Adapted from paper-plot line_aime.py training-curve template.
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
b=Path(__file__).resolve().parent
d=json.loads((b/'selection_analysis.json').read_text())
style=Path('/Users/xiao/.codex/skills/figure-polish/assets/deepscientist-academic.mplstyle').read_text().replace(': #', ': ');(b/'academic.mplstyle').write_text(style);plt.style.use(b/'academic.mplstyle')
fig,axes=plt.subplots(2,2,figsize=(11,7.5),layout='constrained')
for ax,w in zip(axes.flat,d['selected']):
 for row,label,color in [(w['baseline'],'Previous schedule','#99938C'),(w,'Selected schedule','#725B88')]:
  h=json.loads((b/'records/jobs'/row['job']/'training.json').read_text())['history'];x=[v['epoch'] for v in h]
  ax.plot(x,[v['validation']['loss'] for v in h],color=color,lw=1.9,label=label+' validation')
  ax.plot(x,[v['train']['loss'] for v in h],color=color,lw=1.2,ls='--',label=label+' train')
 ax.axvline(20,color='#9AADA4',lw=1,ls=':',label='Nominal cosine T=20')
 ax.scatter([w['best_epoch']],[w['val_best']],s=30,color='#725B88',zorder=5)
 ax.set_title(f"{w['scale']} formulas | {'8:1:1' if w['split']=='811' else '6:2:2'}",loc='left')
 ax.set_xlabel('Epoch');ax.set_ylabel('Token cross entropy');ax.set_xlim(1,36)
 ax.text(.98,.95,f"Best validation: {w['val_best']:.4f}\nImprovement: {w['improvement_pct']:.2f}%\nFinal rebound: {w['rise_pct']:.3f}%",ha='right',va='top',transform=ax.transAxes,fontsize=9)
handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside lower center',ncol=3,fontsize=9)
fig.savefig(b/'selected_vs_previous.png',dpi=300);fig.savefig(b/'selected_vs_previous.pdf')
