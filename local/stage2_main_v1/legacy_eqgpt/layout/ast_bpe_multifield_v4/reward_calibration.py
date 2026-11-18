"""Calibrate each error against visible persistence; future targets never read."""
import numpy as np

def calibration(obs,derivative_scales,field_scales,check):
 d=[];r=[]
 for f in ('u','v'):
  tr=check['trajectory'];m=tr['fit_mask'];target=tr['targets'][f]
  d.append(max(float(np.mean(target[m]**2))/derivative_scales[f],1e-8))
  losses=[]
  for origin in (11,15):losses.append(float(np.mean((obs['fields'][f][origin+1:origin+3]-obs['fields'][f][origin])**2))/field_scales[f])
  r.append(max(float(np.mean(losses)),1e-8))
 return dict(derivative=d,rollout=r)

def calibrated_score(derivative,rollout,k,reference,alpha=.5,complexity=.001):
 # Dimensionless relative errors: persistence has1 in both objectives.
 # Log1p has diminishing slope and no change of penalty sign.
 d=np.asarray(derivative)/reference['derivative'];r=np.asarray(rollout)/reference['rollout']
 agg=lambda a:.5*float(a.mean())+.5*float(a.max())
 return -((1-alpha)*agg(d)+alpha*agg(r))-complexity*np.log1p(k)
