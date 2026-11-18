from pathlib import Path
import json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Patch
ROOT=Path('/data1/users/liugang/src/eq-bpe/project')
base=ROOT/'data/cylinder_numerical_stage2_v1';geo=json.loads((base/'geometry.json').read_text());p=base/'trajectories'/geo['training_reference_trajectory'][:-3]
x=np.load(p/'x.npy');y=np.load(p/'y.npy');mask=np.load(p/'valid_mask.npy');solid=np.load(p/'solid_mask.npy');u=np.load(p/'u.npy',mmap_mode='r')[0]
fig,axes=plt.subplots(1,2,figsize=(12,4.4),layout='constrained')
im=axes[0].pcolormesh(x*1000,y*1000,u,shading='nearest',cmap='cividis',rasterized=True)
axes[0].contour(x*1000,y*1000,mask.astype(float),levels=[.5],colors=['#d1495b'],linewidths=1)
axes[0].add_patch(Circle((geo['center_x_m']*1000,geo['center_y_m']*1000),15,facecolor='#eeeeee',edgecolor='#222222',lw=.8))
axes[0].set_title('Training reference u; red = effective mask boundary');fig.colorbar(im,ax=axes[0],label='u (released units)',shrink=.8)
classes=np.where(solid,0,np.where(mask,2,1))
from matplotlib.colors import ListedColormap
axes[1].pcolormesh(x*1000,y*1000,classes,shading='nearest',cmap=ListedColormap(['#333333','#e6ad54','#d5e7ee']),vmin=0,vmax=2)
axes[1].set_title('62 x 126 cropped grid; 7,660 effective points')
axes[1].legend(handles=[Patch(color='#333333',label='Cylinder'),Patch(color='#e6ad54',label='Excluded interface'),Patch(color='#d5e7ee',label='Effective fluid')],loc='upper right',fontsize=8)
for ax in axes:ax.set(xlabel='x (mm)',ylabel='y (mm)',aspect='equal')
fig.savefig(ROOT/'maintenance/stage2-data-20261115/geometry-preview.png',dpi=160);plt.close(fig)
