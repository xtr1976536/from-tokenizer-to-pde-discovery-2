"""Visible-only derivative holdout + short rollout, worst-field and additive complexity."""
import json
import numpy as np
from multitrajectory_data import observation
from runtime import design,solve,terms
from pinn import diffusion_bounds
from scipy.optimize import lsq_linear
from reward_calibration import calibration,calibrated_score
from order2_backend import forecast

def aggregate(losses):
    a=np.asarray(losses,float)
    return .5*float(a.mean())+.5*float(a.max())

class SingleReward:
    def __init__(self,obs,alpha=.5,complexity=.001):
        self.obs=obs;self.alpha=alpha;self.complexity=complexity;self.calls=0;self.cache={}
        self.fit=self.slice(0,12);self.check=self.slice(12,20)
        self.scales={f:max(float(np.var(obs['fields'][f][:12])),1e-12) for f in ('u','v')}
        self.derivative_scales={f:max(float(np.mean(self.fit['trajectory']['targets'][f]**2)),1e-12) for f in ('u','v')}
        self.reference=calibration(obs,self.derivative_scales,self.scales,self.check)
    def slice(self,start,end):
        x,y=np.meshgrid(self.obs['coordinates']['x'],self.obs['coordinates']['y'])
        o=observation(self.obs['t'][start:end],x,y,{f:a[start:end] for f,a in self.obs['fields'].items()},1,2)
        m=np.zeros_like(o['trajectory']['fit_mask']);m[2:-2:2,2:-2:2,2:-2:2]=True
        o['trajectory']['fit_mask']=m
        return o
    def __call__(self,system):
        key=repr(system.rhs)
        if key in self.cache:return dict(self.cache[key])
        coef={};deriv=[]
        for f,rhs in zip(system.fields,system.rhs):
            X,y=design(rhs,self.fit['trajectory'],f);mask=self.fit['trajectory']['fit_mask'].ravel()
            c=solve([X[mask]],[y[mask]])
            lo,hi=diffusion_bounds(system,f)
            if np.any(c<lo) or np.any(c>hi):
                scales=np.linalg.norm(X[mask],axis=0)
                fit=lsq_linear(X[mask]/scales,y[mask],bounds=(lo*scales,hi*scales),tol=1e-10)
                if not fit.success:raise ValueError('Constrained temporary fit failed')
                c=fit.x/scales
            coef[f]=c.tolist()
            A,b=design(rhs,self.check['trajectory'],f);m=self.check['trajectory']['fit_mask'].ravel()
            deriv.append(float(np.mean((A[m]@c-b[m])**2))/self.derivative_scales[f])
        errors={f:[] for f in system.fields};failure=None
        for origin in (11,15):
            # All references remain inside the20visible frames. Boundary policy matches final solver.
            o=dict(self.obs);o['t']=self.obs['t'][:origin+1];o['fields']={f:a[:origin+1] for f,a in self.obs['fields'].items()}
            try:
                p,_=forecast(system,coef,o,steps=2,max_rhs_calls=2000,max_seconds=5,max_state_factor=20)
                for i,f in enumerate(system.fields):
                    target=self.obs['fields'][f][origin+1:origin+3]
                    errors[f].append(float(np.mean((p[...,i]-target)**2))/self.scales[f])
            except (ValueError,RuntimeError,FloatingPointError,np.linalg.LinAlgError) as e:
                failure=str(e)
                for f in system.fields:errors[f].append(1e6)
        roll=[float(np.mean(errors[f])) for f in system.fields]
        k=sum(len(terms(rhs)) for rhs in system.rhs)
        value=calibrated_score(deriv,roll,k,self.reference,self.alpha,self.complexity)
        self.calls+=1
        if self.calls%20==0:print('REWARD_V2',self.calls,'reward',value,flush=True)
        result=dict(status='evaluated',reward=float(value),derivative_losses=deriv,rollout_losses=roll,
                    complexity_terms=k,rollout_failure=failure,temporary_coefficients=coef,
                    protocol='fit frames0:12; derivative check12:20;2step rollouts from11,15; visible only',
                    calibration_reference=self.reference,version='persistence-calibrated-v3',alpha=self.alpha,complexity_weight=self.complexity,worst_field_weight=.5)

        self.cache[key]=result
        return dict(result)
