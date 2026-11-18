"""EqGPT coefficient optimization: alternate TLS/SVD and neural PINN steps.

The reference PINN_optimization.py fits a surrogate, estimates coefficients by
SVD at each iteration, then updates the field network using Ldata+.01*LPDE.
This module extends the same cycle to two physical fields and physical x/y/t.
"""
import json
from pathlib import Path
import numpy as np
import torch
from torch import nn
from runtime import terms,expand_laplacian
from scipy.optimize import lsq_linear


class Surrogate(nn.Module):
    def __init__(self,low,high,mean,std,width=64):
        super().__init__()
        self.register_buffer('low',torch.tensor(low,dtype=torch.float32))
        self.register_buffer('span',torch.tensor(high-low,dtype=torch.float32))
        self.register_buffer('mean',torch.tensor(mean,dtype=torch.float32))
        self.register_buffer('std',torch.tensor(std,dtype=torch.float32))
        layers=[nn.Linear(3,width),nn.Tanh()]
        for _ in range(3):layers.extend([nn.Linear(width,width),nn.Tanh()])
        layers.append(nn.Linear(width,2));self.net=nn.Sequential(*layers)
    def forward(self,q):return self.net(2*(q-self.low)/self.span-1)*self.std+self.mean


def torch_terms(system,model,q):
    prediction=model(q);cache={}
    axes=('t',)+system.spatial
    def ev(n):
        if n in cache:return cache[n]
        k=n[0]
        if k=='n':v=torch.ones(q.shape[0],dtype=q.dtype,device=q.device)*n[1]
        elif k=='v':v=prediction[:,system.fields.index(n[1])] if n[1] in system.fields else q[:,axes.index(n[1])]
        elif k=='neg':v=-ev(n[1])
        elif k=='add':v=sum(ev(c) for c in n[1:])
        elif k=='mul':
            v=ev(n[1])
            for child in n[2:]:v=v*ev(child)
        elif k=='div':v=ev(n[1])/ev(n[2])
        elif k=='pow':v=ev(n[1])**ev(n[2])
        elif k=='d':
            v=ev(n[1])
            for a in n[2]:
                if v.requires_grad:
                    grad=torch.autograd.grad(v,q,torch.ones_like(v),create_graph=True,retain_graph=True,allow_unused=True)[0]
                    v=q[:,0]*0 if grad is None else grad[:,axes.index(a)]
                else:v=q[:,0]*0
        else:raise ValueError('Unsupported PINN operator:'+k)
        cache[n]=v;return v
    values={}
    for f,rhs in zip(system.fields,system.rhs):
        target=ev(('d',('v',f),'t'))
        matrix=torch.stack([ev(expand_laplacian(atom,system.spatial)) for atom in terms(rhs)],dim=1)
        values[f]=(target,matrix)
    return prediction,values


def tls(target,matrix):
    A=torch.cat([target[:,None],matrix],dim=1).detach().double().cpu().numpy()
    if not np.isfinite(A).all():raise ValueError('Nonfinite PINN matrix')
    norms=np.linalg.norm(A,axis=0)
    if np.any(norms<1e-14):raise ValueError('Unidentifiable PINN column')
    _,_,vh=np.linalg.svd(A/norms,full_matrices=False)
    if abs(vh[-1,0])<1e-10:raise ValueError('PINN TLS target normalization undefined')
    coefficient=-vh[-1,1:]/vh[-1,0]*norms[0]/norms[1:]
    if not np.isfinite(coefficient).all():raise ValueError('Nonfinite PINN coefficients')
    return coefficient

def diffusion_bounds(system,field):
    lo=[];hi=[]
    for node in terms(system.rhs[system.fields.index(field)]):
        sign=1
        while node[0]=='neg':sign*=-1;node=node[1]
        def affine(n):
            if n==('v',field):return (1.,0.)
            if n[0]=='n':return (0.,float(n[1]))
            if n[0]=='neg':
                a,b=affine(n[1]);return -a,-b
            if n[0]=='add':
                values=[affine(c) for c in n[1:]];return sum(a for a,b in values),sum(b for a,b in values)
            raise ValueError('not affine self field')
        diffusion=False
        if (node[0]=='lap' and node[2]==1) or (node[0]=='d' and node[2] in ('xx','yy')):
            try:
                slope,_=affine(node[1]);diffusion=slope!=0
                if diffusion:sign*=np.sign(slope)
            except ValueError:pass
        lo.append(0. if diffusion and sign==1 else -np.inf)
        hi.append(0. if diffusion and sign==-1 else np.inf)
    return np.asarray(lo),np.asarray(hi)

def identify(system,field,target,matrix):
    proposed=tls(target,matrix);lo,hi=diffusion_bounds(system,field)
    if np.any(proposed<lo) or np.any(proposed>hi):
        X=matrix.detach().double().cpu().numpy();y=target.detach().double().cpu().numpy()
        scales=np.linalg.norm(X,axis=0)
        result=lsq_linear(X/scales,y,bounds=(lo*scales,hi*scales),tol=1e-10)
        if not result.success:raise ValueError('Dissipative coefficient projection failed')
        return result.x/scales,True
    return proposed,False


def fit_pinn(system,observation,out,warm_steps=1000,physics_steps=500,validation_observation=None,coefficient_validation=None,initial_mlp_state=None,initial_coefficients=None):
    torch.set_num_threads(2);torch.manual_seed(525);rng=np.random.default_rng(525)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    coords={'t':observation['t'],**observation['coordinates']}
    meshes=np.meshgrid(*coords.values(),indexing='ij');q=np.stack([a.ravel() for a in meshes],axis=1)
    target=np.stack([observation['fields'][f].ravel() for f in system.fields],axis=1)
    valid=observation['trajectory']['fit_mask'].ravel();indices=np.flatnonzero(valid)
    if len(indices)<4:raise ValueError('PINN requires at least4 admissible observation points')
    rng.shuffle(indices);nval=min(max(1,len(indices)//10),len(indices)-2);val=indices[:nval];train=indices[nval:]
    low=q.min(0);high=q.max(0);mean=target[train].mean(0);std=np.maximum(target[train].std(0),1e-5)
    model=Surrogate(low,high,mean,std)
    if initial_mlp_state is not None:model.load_state_dict(initial_mlp_state)
    optimizer=torch.optim.Adam(model.parameters(),lr=.001)
    qt=torch.tensor(q,dtype=torch.float32);yt=torch.tensor(target,dtype=torch.float32)
    history=[];best=float('inf');best_state=None;best_step=None;projection_count=0;best_coefficients=None
    if initial_coefficients is not None and coefficient_validation is not None:
        initial_score=float(coefficient_validation(initial_coefficients))
        if np.isfinite(initial_score):
            best=initial_score;best_step=0;best_state={k:v.detach().clone() for k,v in model.state_dict().items()}
            best_coefficients={f:list(initial_coefficients[f]) for f in system.fields}
    if initial_mlp_state is not None:warm_steps=0
    for step in range(warm_steps):
        batch=rng.choice(train,min(512,len(train)),replace=False)
        optimizer.zero_grad(set_to_none=True);loss=(((model(qt[batch])-yt[batch])/model.std)**2).mean()
        if not torch.isfinite(loss):raise FloatingPointError('Surrogate warmup diverged')
        loss.backward();optimizer.step()
        if (step+1)%250==0:print('SURROGATE',step+1,float(loss.detach()),flush=True)
    scale={f:max(float(np.sqrt(np.mean(observation['trajectory']['targets'][f].ravel()[train]**2))),1e-6) for f in system.fields}
    cohort=rng.choice(train,min(2048,len(train)),replace=False)
    def refresh():
        nonlocal projection_count
        _,values=torch_terms(system,model,qt[cohort].clone().requires_grad_(True))
        coefs={}
        for field,(y,X) in values.items():
            coefficient,projected=identify(system,field,y,X);projection_count+=int(projected);coefs[field]=coefficient.tolist()
        return coefs
    coefs=refresh()
    for step in range(physics_steps):
        batch=rng.choice(train,min(256,len(train)),replace=False)
        x=qt[batch].clone().requires_grad_(True);optimizer.zero_grad(set_to_none=True)
        prediction,matrices=torch_terms(system,model,x);ldata=(((prediction-yt[batch])/model.std)**2).mean()
        if step and step%25==0:coefs=refresh()
        physics=[]
        for f,(y,X) in matrices.items():
            ct=torch.tensor(coefs[f],dtype=X.dtype)
            physics.append(((y-X@ct)/scale[f]).square().mean())
        lpde=torch.stack(physics).mean();loss=ldata+.01*lpde
        if not torch.isfinite(loss):raise FloatingPointError('PINN loss diverged')
        loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),10);optimizer.step()
        if step==0 or (step+1)%25==0:
            coefs=refresh()
            with torch.no_grad():vl=float((((model(qt[val])-yt[val])/model.std)**2).mean())
            derivative_error=0.
            if validation_observation is not None:
                from runtime import design
                tr=validation_observation['trajectory'];mask=tr['fit_mask'].ravel()
                for field,rhs in zip(system.fields,system.rhs):
                    X,y=design(rhs,tr,field)
                    derivative_error+=float(np.mean((y[mask]-X[mask]@np.asarray(coefs[field]))**2)/max(np.mean(y[mask]**2),1e-24))/len(system.fields)
            selection=vl+.01*derivative_error
            if coefficient_validation is not None:selection=coefficient_validation(coefs)
            if np.isfinite(selection) and selection<best:
                best_coefficients={f:list(coefs[f]) for f in system.fields}
                best=selection;best_step=step+1;best_state={k:v.detach().clone() for k,v in model.state_dict().items()}
            row=dict(step=step+1,data_loss=float(ldata.detach()),pde_loss=float(lpde.detach()),total_loss=float(loss.detach()),validation_data_loss=vl,coefficients=coefs)
            row.update(validation_derivative_error=derivative_error,checkpoint_selection_loss=selection if np.isfinite(selection) else None,rollout_validation_passed=bool(np.isfinite(selection)))
            history.append(row);print('PINN',step+1,row['data_loss'],row['pde_loss'],flush=True)
    # Re-estimate only after the last neural update, on allowed observation points.
    if best_state is None:
        failure={'status':'FAILED','reason':'No PINN checkpoint passed visible rollout validation','history':history,'initial_coefficients_provided':initial_coefficients is not None,'future_frames_used':0}
        (out/'failure.json').write_text(json.dumps(failure,indent=2,allow_nan=False))
        raise ValueError('No PINN checkpoint passed visible rollout validation; see pinn/failure.json')
    model.load_state_dict(best_state)
    coefficients=best_coefficients if best_coefficients is not None else refresh()
    torch.save(dict(state=model.state_dict(),low=low.tolist(),high=high.tolist(),mean=mean.tolist(),std=std.tolist()),out/'surrogate.pt')
    report=dict(status='COMPLETE',selection_source='validated_search_initialization' if best_step==0 else 'pinn_update',pinn_update_accepted=bool(best_step is not None and best_step>0),method='EqGPT-style PINN with column-scaled TLS, fixed-cohort refresh and constrained diffusion projection',
                reference='eqgpt_original/code/PINN_optimization.py:get_coefficients and training loop',
                objective='field/derivative-scale-normalized Ldata+0.01*LPDE; scales use only observed input frames',
                coefficients=coefficients,history=history,warm_steps=warm_steps,physics_steps=physics_steps,
                fit_points=len(train),validation_points=len(val),future_frames_used=0,
                selected_step=best_step,best_validation_loss=best,coefficient_cohort_points=len(cohort),diffusion_projection_count=projection_count,
                adaptations='two output fields;dimensionless TLS columns;fixed2048-point training cohort;25-step coefficient refresh;best checkpoint from allowed validation;nonnegative pure self-diffusion for Cylinder')
    (out/'result.json').write_text(json.dumps(report,indent=2,allow_nan=False));return coefficients,report
