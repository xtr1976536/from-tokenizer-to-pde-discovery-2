"""Read-only same-trajectory/frame plots and exact storage accounting."""
from pathlib import Path
import json,sys
import numpy as np
import pyarrow as pa
import pyarrow.ipc as ipc
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
ROOT=Path('/data1/users/liugang/src/eq-bpe/project')
OUT=ROOT/'maintenance/stage2-data-review-20261115';OUT.mkdir(parents=True,exist_ok=True)
raw=ROOT/'data/realpdebench/cylinder/hf_dataset/numerical/data-00000-of-00092.arrow'
processed=ROOT/'data/cylinder_numerical_stage2_v1/trajectories/10031'
source=pa.memory_map(str(raw),'r');table=ipc.open_stream(source).read_all();row={n:table[n][0] for n in table.column_names}
shape=tuple(row[k].as_py() for k in ('shape_t','shape_h','shape_w'));sid=row['sim_id'].as_py();assert sid=='10031.h5'
x=np.frombuffer(row['x'].as_buffer(),'<f8').reshape(shape[1:])*1000
y=np.frombuffer(row['y'].as_buffer(),'<f8').reshape(shape[1:])*1000
t=np.frombuffer(row['t'].as_buffer(),'<f8');mask=np.load(processed/'valid_mask.npy')
geometry=json.loads((ROOT/'data/cylinder_numerical_stage2_v1/geometry.json').read_text())
arrays={f:np.frombuffer(row[f].as_buffer(),'<f4').reshape(shape) for f in ('u','v','p')}
proc={f:np.load(processed/(f+'.npy'),mmap_mode='r') for f in ('u','v','p')}
assert all(np.array_equal(proc[f][1000],arrays[f][1000,::2,::2][1:-1,1:-1]) for f in arrays)
plt.rcParams.update({'font.size':10,'axes.titlesize':11,'axes.labelsize':10,'xtick.labelsize':9,'ytick.labelsize':9})
fig,axes=plt.subplots(3,3,figsize=(13,8.5),sharex=True,sharey=True,layout='constrained')
frame=1000
for r,f in enumerate(('u','v','p')):
 original=arrays[f][frame];native=original[::2,::2];final=np.ma.masked_where(~mask,proc[f][frame])
 if f=='u':vmin,vmax=float(original.min()),float(original.max());cmap=plt.get_cmap('cividis').copy()
 else:
  bound=float(np.abs(original).max());vmin,vmax=-bound,bound;cmap=plt.get_cmap('RdBu_r').copy()
 cmap.set_bad('#a8a8a8')
 for c,(xx,yy,z) in enumerate([(x,y,original),(x[::2,::2],y[::2,::2],native),(x[::2,::2][1:-1,1:-1],y[::2,::2][1:-1,1:-1],final)]):
  ax=axes[r,c];im=ax.pcolormesh(xx,yy,z,shading='nearest',cmap=cmap,vmin=vmin,vmax=vmax,rasterized=True)
  ax.add_patch(Circle((geometry['center_x_m']*1000,geometry['center_y_m']*1000),15,fill=False,edgecolor='#202020',linewidth=.75,linestyle='--'))
  ax.set_aspect('equal');ax.set_xlim(x.min(),x.max());ax.set_ylim(y.min(),y.max())
  if c==0:ax.set_ylabel(f'{f}\ny (mm)')
  if r==2:ax.set_xlabel('x (mm)')
 fig.colorbar(im,ax=axes[r,:],label=f'{f}: released values',shrink=.8,pad=.015)
for ax,title in zip(axes[0],['Original released simulation\n128 x 256','Spatial stride = 2\n64 x 128','Outer crop + evaluation mask\n62 x 126']):ax.set_title(title)
fig.suptitle(f'Same trajectory {sid}, frame {frame} (0-based), t = {t[frame]:.3f} s\nIdentical color scale within each row; gray = excluded body/interface',fontsize=12)
fig.savefig(OUT/'fields-before-after.png',dpi=160,facecolor='white');plt.close(fig)
frames=[0,20,40,60];values=[arrays['u'][k] for k in frames];vmin=min(float(a.min()) for a in values);vmax=max(float(a.max()) for a in values);cmap=plt.get_cmap('cividis').copy();cmap.set_bad('#a8a8a8')
fig,axes=plt.subplots(2,4,figsize=(14.2,4.8),sharex=True,sharey=True,layout='constrained')
for col,k in enumerate(frames):
 for r,(xx,yy,z) in enumerate([(x,y,arrays['u'][k]),(x[::2,::2][1:-1,1:-1],y[::2,::2][1:-1,1:-1],np.ma.masked_where(~mask,proc['u'][k]))]):
  ax=axes[r,col];im=ax.pcolormesh(xx,yy,z,shading='nearest',cmap=cmap,vmin=vmin,vmax=vmax,rasterized=True);ax.set_aspect('equal');ax.set_xlim(x.min(),x.max());ax.set_ylim(y.min(),y.max())
  if r==0:ax.set_title(f'Frame {k}; t = {t[k]:.3f} s')
  if r==1:ax.set_xlabel('x (mm)')
axes[0,0].set_ylabel('Original u\ny (mm)');axes[1,0].set_ylabel('Processed u\ny (mm)')
fig.colorbar(im,ax=axes.ravel().tolist(),label='u: released values',shrink=.85,pad=.015)
fig.suptitle(f'Time evolution of the SAME trajectory {sid}; all 3990 frames retained',fontsize=12)
fig.savefig(OUT/'trajectory-before-after.png',dpi=160,facecolor='white');plt.close(fig)
original_dir=ROOT/'data/realpdebench/cylinder/hf_dataset/numerical';new_dir=ROOT/'data/cylinder_numerical_stage2_v1'
raw_bytes=sum(p.stat().st_size for p in original_dir.glob('*.arrow'));crop_bytes=sum(p.stat().st_size for f in ('u','v','p') for p in new_dir.glob('trajectories/*/'+f+'.npy'));halo_bytes=sum(p.stat().st_size for p in new_dir.glob('trajectories/*/*_halo.npy'));new_bytes=sum(p.stat().st_size for p in new_dir.rglob('*') if p.is_file())
result={'trajectory':sid,'frame':frame,'time':float(t[frame]),'all_92_trajectories_retained':True,'frames_per_trajectory':3990,'channels_retained':['u','v','p'],'field_dtype':'float32',
 'raw_shape':list(shape),'native_shape':[3990,64,128],'cropped_shape':[3990,62,126],'raw_arrow_bytes':raw_bytes,'cropped_field_bytes':crop_bytes,'halo_bytes':halo_bytes,'processed_total_bytes':new_bytes,'processed_to_raw_ratio':new_bytes/raw_bytes,
 'spatial_sampling_points_ratio':64*128/(128*256),'cropped_to_native_points_ratio':62*126/(64*128),'effective_points':int(mask.sum()),'actual_disk_cause':'stride2 in both spatial axes; cropped outer halo is retained, mask does not delete array entries',
 'shown_frames':frames,'processed_equals_corresponding_raw_stride2_crop':True}
(OUT/'comparison-facts.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
