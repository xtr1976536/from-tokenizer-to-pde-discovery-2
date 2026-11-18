"""Fit on training histories, score fixed coefficients on validation histories."""
import numpy as np
from runtime import design,solve,terms
from grouped_scoring_snapshot import fit,normalize as groups_of,basis_values
from scipy.optimize import lsq_linear,minimize,LinearConstraint

def constrain_training_fit(system,field,rhs,train,basis,model):
    from pinn import diffusion_bounds
    lo,hi=diffusion_bounds(system,field)
    if not np.isfinite(lo).any() and not np.isfinite(hi).any():return model,False,None
    groups,B=groups_of(train,basis)
    if not np.any((B@model<lo)|(B@model>hi)):return model,False,None
    matrices=[];targets=[];blocks=[]
    for gi,g in enumerate(groups):
        for tr in g['trajectories']:
            X,y=design(rhs,tr,field);mask=np.asarray(tr['fit_mask'],bool).ravel()
            scale=np.sqrt(len(groups)*len(g['trajectories'])*mask.sum()*max(float(np.mean(y[mask]**2)),1e-24))
            matrices.append(np.hstack([b*X[mask] for b in B[gi]])/scale);targets.append(y[mask]/scale);blocks.append((gi,X,y,mask))
    A=np.vstack(matrices);b=np.concatenate(targets);scales=np.linalg.norm(A,axis=0)
    if len(basis)==1:
        result=lsq_linear(A/scales,b,bounds=(lo*scales,hi*scales),tol=1e-10)
        if not result.success:raise ValueError('Constrained score fit failed')
        beta=(result.x/scales).reshape(model.shape)
    else:
        C=[];lower=[];upper=[];k=model.shape[1]
        for parameter_basis in B:
            for term in range(k):
                if not np.isfinite(lo[term]) and not np.isfinite(hi[term]):continue
                row=np.zeros(A.shape[1]);row[np.arange(len(basis))*k+term]=parameter_basis
                row=row/scales;norm=np.linalg.norm(row)
                C.append(row/norm);lower.append(lo[term]/norm);upper.append(hi[term]/norm)
        As=A/scales
        result=minimize(lambda z:.5*np.sum((As@z-b)**2),model.ravel()*scales,jac=lambda z:As.T@(As@z-b),
                        method='SLSQP',constraints=[LinearConstraint(np.asarray(C),lower,upper)],options={'maxiter':300,'ftol':1e-10})
        if not result.success:raise ValueError('Constrained parameter function fit failed')
        beta=(result.x/scales).reshape(model.shape)
    scores=[[] for _ in groups]
    for gi,X,y,mask in blocks:
        denominator=np.sum((y[mask]-y[mask].mean())**2)
        scores[gi].append(1-float(np.sum((y[mask]-X[mask]@(B[gi]@beta))**2))/denominator)
    return beta,True,float(np.mean([np.mean(v) for v in scores]))


def score(system,train,validation,balance=.5,epi=.2,parameter_basis=('1',)):
    fitted=fit(system,train,parameter_basis,design,solve,epi=epi,export=True)
    validation_groups,_=groups_of(validation,('1',))
    fields=[]
    for field,rhs in zip(system.fields,system.rhs):
        group_scores=[]
        beta=np.asarray(fitted['coefficient_models'][field])
        beta,constrained,training_r2=constrain_training_fit(system,field,rhs,train,parameter_basis,beta)
        for group in validation_groups:
            coef=np.asarray(basis_values(group['parameters'],parameter_basis))@beta
            r2=[]
            for tr in group['trajectories']:
                X,y=design(rhs,tr,field);mask=np.asarray(tr.get('score_mask',tr['fit_mask']),bool).ravel()
                if not mask.any():mask=np.asarray(tr['fit_mask'],bool).ravel()
                denom=float(np.sum((y[mask]-y[mask].mean())**2))
                if denom<1e-24:raise ValueError('Constant derivative target')
                r2.append(1-float(np.sum((y[mask]-X[mask]@coef)**2))/denom)
            group_scores.append(float(np.mean(r2)))
        diagnostics=dict(train_r2=training_r2 if constrained else next(r['r2'] for r in fitted['fields'] if r['field']==field),validation_r2=float(np.mean(group_scores)),diffusion_constraint_active=constrained)
        count=len(terms(rhs))+1
        value=(1-epi*np.log10(count))*diagnostics['validation_r2']
        fields.append(dict(field=field,term_columns=count,validation_reward=value,**diagnostics))
    rewards=[r['validation_reward'] for r in fields]
    mean=float(np.mean(rewards));worst=float(np.min(rewards))
    return dict(status='evaluated',reward=(1-balance)*mean+balance*worst,fields=fields,
                validation_mean_reward=mean,validation_worst_reward=worst,balance=balance,
                parameter_basis=list(parameter_basis),
                coefficient_policy='temporary train-only OLS with pure self-diffusion sign constraints; coefficients fixed on validation histories',
                future_test_labels_used=False)
