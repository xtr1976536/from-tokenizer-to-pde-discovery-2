"""Restricted order2 extension: explicit evolution plus linear constant mixed-time terms."""
import numpy as np
import re
from scipy.sparse import eye,kron,bmat,csc_matrix
from scipy.sparse.linalg import splu
from scipy.integrate import solve_ivp
from runtime import System,terms,expand_laplacian,evaluate,Parser,derivative_order,temporal
from grid import GridBackend

def time_atom(node):
    sign=1
    while node[0]=='neg':sign=-sign;node=node[1]
    if node[0]!='d' or node[1][0]!='v' or node[2].count('t')!=1 or not 1<=len(node[2])<=2:
        raise ValueError('Time terms must be linear derivatives of one field, total order<=2')
    return sign,node[1][1],node[2].replace('t','')

def parse_system(text,fields=('u','v'),spatial=('y','x')):
    if re.search(r'(?<![A-Za-z\\])[uvxy]{2,}(?![A-Za-z])',re.sub(r'\\partial_\{[txy]+\}', '',text)):raise ValueError('Implicit adjacent field/coordinate symbols forbidden')
    pieces=text.split(r'\\')
    if len(pieces)!=2:raise ValueError('Exactly two evolution equations required')
    rhs=[]
    for field,piece in zip(fields,pieces):
        if piece.count('=')!=1:raise ValueError('Explicit equality required')
        left,right=piece.split('=');args=dict(fields=fields,coordinates=('t',)+spatial)
        parts=terms(Parser(left,**args).parse());target=('d',('v',field),'t')
        if parts.count(target)!=1:raise ValueError('Unit own time derivative anchor required')
        rest=list(parts);rest.remove(target);node=Parser(right,**args).parse()
        node=('add',node,*(('neg',a) for a in rest)) if rest else node
        def check(n):
            if n[0] in ('div','fn'):raise ValueError('Rational/transcendental terms remain disabled')
            if derivative_order(n)>2:raise ValueError('Maximum total derivative order is2')
            if n[0]=='d' and 't' in n[2]:
                time_atom(n)
            for ch in n[1:]:
                if isinstance(ch,tuple):check(ch)
        check(node)
        for atom in terms(node):
            expanded=expand_laplacian(atom,spatial)
            if derivative_order(expanded)>2:raise ValueError('Expanded derivative order exceeds2')
            if temporal(atom):
                _,source,axes=time_atom(atom)
                if not axes:raise ValueError('Additional pure time derivatives remain disabled; use mixed xt/yt only')
        rhs.append(node)
    return System(tuple(fields),tuple(rhs),text,tuple(spatial))

def forecast(system,coefficients,observation,steps=20,rtol=1e-4,atol=1e-7,max_rhs_calls=50000,max_seconds=None,max_state_factor=100,max_step_fraction=.25,boundary_mode="freeze"):
    import time
    if steps<1 or not 0<max_step_fraction<=1:raise ValueError('Invalid integration settings')
    if boundary_mode not in ('freeze','linear_visible'):raise ValueError('Unknown boundary mode')
    start=time.monotonic();coords=observation['coordinates'];shape=tuple(map(len,coords.values()));n=int(np.prod(shape));dt=observation['dt'];t0=float(observation['t'][-1])
    # Frozen2-cell boundary collar supplies a declared closure for order2 stencils.
    edge=np.ones(shape,bool);edge[2:-2,2:-2]=False
    if not (~edge).any():raise ValueError('Order2 rollout needs grid dimensions>=5')
    interior=(~edge).ravel().astype(float)
    from scipy.sparse import diags
    P=diags(interior);I=eye(n,format='csc');zero=csc_matrix((n,n))
    ds={}
    for axis,(name,values) in enumerate(coords.items()):
        D=csc_matrix(np.gradient(np.eye(len(values)),values,axis=0,edge_order=2))
        ds[name]=kron(D,eye(shape[1]),format='csc') if axis==0 else kron(eye(shape[0]),D,format='csc')
    blocks=[[I.copy(),zero.copy()],[zero.copy(),I.copy()]];ordinary={};all_terms={}
    for i,(f,rhs) in enumerate(zip(system.fields,system.rhs)):
        ordinary[f]=[];all_terms[f]=terms(rhs)
        if len(coefficients[f])!=len(all_terms[f]):raise ValueError('Coefficient count mismatch')
        for c,a in zip(coefficients[f],all_terms[f]):
            if temporal(a):
                sign,source,axes=time_atom(a);D=I
                for axis in axes:D=ds[axis]@D
                j=system.fields.index(source);blocks[i][j]=blocks[i][j]-float(c)*sign*(P@D)
            else:ordinary[f].append((float(c),expand_laplacian(a,system.spatial)))
    M=bmat(blocks,format='csc');factor=splu(M)
    probe=np.ones(2*n);z=factor.solve(probe)
    if not np.isfinite(z).all() or np.linalg.norm(M@z-probe)>1e-7*np.linalg.norm(probe):raise ValueError('Unreliable evolution operator')
    initial={f:observation['fields'][f][-1].copy() for f in system.fields}
    slopes={f:np.zeros(shape) for f in system.fields}
    if boundary_mode=='linear_visible':
        tt=np.asarray(observation['t'][-6:]);center=tt-tt.mean()
        slopes={f:np.sum(center[:,None,None]*observation['fields'][f][-6:],axis=0)/np.sum(center**2) for f in system.fields}
    y0=np.concatenate([initial[f].ravel() for f in system.fields]);calls=0
    def fun(t,flat):
        nonlocal calls
        calls+=1
        if max_rhs_calls and calls>max_rhs_calls:raise RuntimeError('RHS budget exceeded')
        if max_seconds and time.monotonic()-start>max_seconds:raise RuntimeError('Rollout time budget exceeded')
        if max_state_factor and np.max(np.abs(flat))>max_state_factor*max(np.max(np.abs(y0)),1e-6):raise FloatingPointError('State growth bound exceeded')
        state={f:flat[i*n:(i+1)*n].reshape(shape).copy() for i,f in enumerate(system.fields)}
        for f in state:state[f][edge]=(initial[f]+(t-t0)*slopes[f])[edge]
        backend=GridBackend(coords,state);backend.values['t']=t;result=[]
        for f in system.fields:
            v=np.zeros(shape)
            for c,a in ordinary[f]:v+=c*np.broadcast_to(evaluate(a,backend.values,backend.derivative),shape)
            v[edge]=slopes[f][edge];result.append(v.ravel())
        out=factor.solve(np.concatenate(result))
        if not np.isfinite(out).all():raise FloatingPointError('Nonfinite derivative')
        return out
    # Mixed-time inverse is nonlocal: do not supply the old local Jacobian sparsity.
    # Explicit adaptive RK avoids dense finite-difference Jacobians for mixed systems.
    grid=t0+dt*np.arange(1,steps+1)
    sol=solve_ivp(fun,(t0,grid[-1]),y0,t_eval=grid,method='RK45',rtol=rtol,atol=atol,max_step=dt*max_step_fraction)
    if not sol.success or sol.y.shape[1]!=steps or not np.isfinite(sol.y).all():raise RuntimeError('Extended rollout failed')
    pred=np.stack([sol.y[i*n:(i+1)*n].T.reshape((steps,)+shape) for i in range(2)],axis=-1)
    return pred,dict(method='order2 finite differences; sparse constant mass LU; adaptive RK45',rhs_calls=calls,seconds=time.monotonic()-start,boundary='2cell collar '+boundary_mode+' using visible-only trend',steps=steps,success=True)
