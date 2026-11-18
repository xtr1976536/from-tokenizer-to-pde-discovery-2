"""Three-field residual fitting and implicit finite-difference rollout.

No NS template, pressure equation or own-time-derivative anchor is inserted.
Supported numerical subset: real local systems, spatial jet order <=4 and
temporal order <=2; unsupported candidates are rejected after generation.
"""
from dataclasses import dataclass
from collections import OrderedDict
from functools import lru_cache
from itertools import product
import time
import sys
from pathlib import Path
import numpy as np
import sympy as sp
from scipy.optimize import least_squares,OptimizeResult
from scipy.sparse import coo_matrix,eye,kron,diags,bmat
from scipy.sparse.csgraph import structural_rank
from scipy.sparse.linalg import lsmr,splu
from scipy.ndimage import binary_dilation
from .contracts import InvalidCandidate
sys.path.insert(0,str(Path(__file__).parent/'corpus_work'))
from .corpus_work import structure_latex as structure
from .corpus_work.task_gate import validate
from .corpus_work.equivalence import key as count_key
from .corpus_work.audit_component_expansions import symbolic
from ast_runtime import expand_laplacian

FIELDS=('u','v','p')
X,Y,T=sp.symbols('x y t',real=True)
AXES={X:'x',Y:'y',T:'t'}
FUNCTIONS={f:sp.Function(f,real=True)(X,Y,T) for f in FIELDS}


@dataclass
class CompiledTerm:
    arguments:tuple
    function:object
    temporal_priority:tuple=None
    gradient:object=None
    affine:bool=False


@dataclass
class ResidualSystem:
    text:str
    rows:tuple
    structure_key:str
    term_counts:tuple
    anchor_indices:tuple=()


def structural_anchor(row):
    """Choose once from structure, never from window values or fitted R2."""
    temporal=[(term.temporal_priority,index) for index,term in enumerate(row)
              if term.temporal_priority is not None]
    if temporal:return min(temporal)[1]
    for index,term in enumerate(row):
        if term.arguments:return index
    raise InvalidCandidate('No structurally nonconstant anchor term')


def compile_term(ast):
    # Preserve factorization. Deep global expand can create millions of terms
    # from a short nested expression; it is unnecessary for numerical evaluation.
    expression=symbolic(expand_laplacian(ast,('x','y')),FUNCTIONS).doit()
    if sum(1 for _ in sp.preorder_traversal(expression))>12000:
        raise InvalidCandidate('Compiled expression node budget exceeded')
    _,base=expression.as_coeff_Mul();temporal_priority=None
    if isinstance(base,sp.Derivative) and all(axis==T for axis,_ in base.variable_count):
        order=sum(n for _,n in base.variable_count)
        field=str(base.expr.func)
        if field in FIELDS:temporal_priority=(order,FIELDS.index(field))
    replace={};jets={}
    for derivative in expression.atoms(sp.Derivative):
        field=str(derivative.expr.func)
        if field not in FIELDS:raise InvalidCandidate('Nonlocal or nonsmooth derivative is unsupported')
        axes=''.join(AXES[a]*n for a,n in derivative.variable_count)
        if len(axes.replace('t',''))>4 or axes.count('t')>2:
            raise InvalidCandidate('Numerical subset supports spatial order <=4 and time order <=2')
        symbol=sp.Symbol('jet_'+field+'_'+axes);replace[derivative]=symbol;jets[str(symbol)]=(field,axes)
    for field,fn in FUNCTIONS.items():replace[fn]=sp.Symbol('field_'+field)
    expression=expression.xreplace(replace)
    args=tuple(sorted(expression.free_symbols,key=str));keys=[]
    for arg in args:
        name=str(arg)
        if name in ('x','y','t'):keys.append(('coordinate',name))
        elif name.startswith('field_'):keys.append((name[6:],''))
        elif name in jets:keys.append(jets[name])
        else:raise InvalidCandidate('Undeclared symbol in numerical expression: '+name)
    if expression.has(sp.Derivative,sp.DiracDelta):raise InvalidCandidate('Unsupported unresolved derivative')
    gradients=tuple(sp.diff(expression,arg) if key[0] in FIELDS else sp.Integer(0)
                    for arg,key in zip(args,keys))
    if sum(sum(1 for _ in sp.preorder_traversal(value)) for value in gradients)>24000:
        raise InvalidCandidate('Analytic gradient node budget exceeded')
    unknowns={arg for arg,key in zip(args,keys) if key[0] in FIELDS}
    affine=not any(value.free_symbols&unknowns for value in gradients)
    return CompiledTerm(tuple(keys),sp.lambdify(args,expression,modules='numpy',cse=True,docstring_limit=0),
        temporal_priority,sp.lambdify(args,gradients,modules='numpy',cse=True,docstring_limit=0),affine)


@lru_cache(maxsize=128)
def derivative_matrix(coordinates,order):
    values=np.asarray(coordinates,float);size=len(values)
    width=3 if order<=2 else 5
    if size<width:raise InvalidCandidate('Insufficient grid points for spatial stencil')
    spacing=np.diff(values)
    if not np.allclose(spacing,spacing[0],rtol=1e-5,atol=1e-12):raise InvalidCandidate('Spatial stencils require uniform Cartesian coordinates')
    rows=[];columns=[];weights=[]
    for i in range(size):
        start=min(max(0,i-width//2),size-width);indices=np.arange(start,start+width)
        offsets=indices-i;matrix=np.asarray([offsets.astype(float)**k for k in range(width)])
        target=np.zeros(width);target[order]=float(__import__('math').factorial(order))
        w=np.linalg.solve(matrix,target)/spacing[0]**order
        rows.extend([i]*width);columns.extend(indices);weights.extend(w)
    return coo_matrix((weights,(rows,columns)),shape=(size,size)).tocsr()


def spatial_derivative(array,axis,coordinates,order):
    if not order:return array
    values=np.asarray(coordinates,dtype=float)
    if order>4:raise InvalidCandidate('Spatial jet order exceeds4')
    matrix=derivative_matrix(tuple(values),order)
    moved=np.moveaxis(np.asarray(array),axis,0);shape=moved.shape
    out=matrix.dot(moved.reshape(len(values),-1)).reshape(shape)
    return np.moveaxis(out,0,axis)


def spatial_radius(system):
    return max((max(1 if key[1].count(axis)<=2 else 2 for axis in ('x','y'))
                for row in system.rows for term in row for key in term.arguments
                if key[0] in FIELDS and any(a in key[1] for a in ('x','y'))),default=1)


def closed_active(active,radius):
    result=active.copy()
    if radius>1:
        # Original mask already excludes one outer/interface cell; freeze one
        # additional ring for five-point fourth-order derivative stencils.
        result &= ~binary_dilation(~active,structure=np.ones((3,3)),iterations=radius-1)
    result[:radius]=False;result[-radius:]=False;result[:,:radius]=False;result[:,-radius:]=False
    return result


def context(visible,mask):
    if 'halo' in visible:
        from .prepared_data import reconstruct_context
        obs=reconstruct_context(visible);crop=(slice(1,-1),slice(1,-1));active=np.pad(np.asarray(mask,bool),1)
    else:
        obs={k:visible[k] for k in ('u','v','p','t','x','y')};crop=(slice(None),slice(None));active=np.asarray(mask,bool).copy()
        active[[0,-1],:]=False;active[:,[0,-1]]=False
    fields={f:np.asarray(obs[f],dtype=float) for f in FIELDS};tt=np.asarray(obs['t'],float)
    x=np.asarray(obs['x'],float);y=np.asarray(obs['y'],float)
    if x.ndim==2:
        if not np.allclose(x,x[:1,:]):raise InvalidCandidate('x coordinate must form a Cartesian mesh')
        x=x[0]
    if y.ndim==2:
        if not np.allclose(y,y[:,:1]):raise InvalidCandidate('y coordinate must form a Cartesian mesh')
        y=y[:,0]
    shape=(len(y),len(x))
    if any(a.shape!=(len(tt),)+shape for a in fields.values()):raise InvalidCandidate('Field/coordinate shape mismatch; expected [time,y,x]')
    if len(tt)<5 or not np.all(np.diff(tt)>0) or not active.any():raise InvalidCandidate('Insufficient visible history/domain')
    if any(not np.isfinite(a).all() for a in fields.values()):raise InvalidCandidate('Nonfinite visible context')
    return fields,tt,x,y,active,crop


class ImplicitBackend:
    fields=FIELDS;equation_count=3;spatial_dimensions=2
    term_count_convention='canonical_lhs_plus_rhs_before_stencil_expansion'
    def __init__(self,max_fit_points=20000,max_nfev=60,max_calls=60000,max_seconds=60,residual_tolerance=1e-4,
                 analytic_jacobian=True,fit_cache_mb=128,linear_fast_path=True):
        self.max_fit_points=max_fit_points;self.max_nfev=max_nfev;self.max_calls=max_calls
        self.max_seconds=max_seconds;self.residual_tolerance=residual_tolerance;self.last_diagnostics={}
        self.analytic_jacobian=analytic_jacobian;self.fit_cache_mb=fit_cache_mb
        self.linear_fast_path=linear_fast_path
        self._fit_cache=OrderedDict();self._fit_cache_bytes=0
    def parse(self,text):
        try:
            validate(text)
            normalized=structure.normalize_system(text.split(chr(92)*2),FIELDS)
            asts=normalized['residual_support_ast'];rows=[]
            if len({repr(ast) for ast in asts})!=3:raise InvalidCandidate('Repeated residual equations cannot define an independent system')
            for ast in asts:
                terms=ast[1:] if ast[0]=='add' else (ast,)
                rows.append(tuple(compile_term(term) for term in terms))
            anchors=tuple(structural_anchor(row) for row in rows)
            # The expanded equivalence key remains valid, but is protected by
            # the external parser deadline/memory cap in production.
            return ResidualSystem(text,tuple(rows),count_key(asts,FIELDS),tuple(len(row) for row in rows),anchors)
        except (ValueError,TypeError,IndexError,KeyError,NotImplementedError,RecursionError) as error:
            if isinstance(error,InvalidCandidate):raise
            raise InvalidCandidate('Candidate parse/compile failed: '+str(error)) from error
    def structure_key(self,system):return system.structure_key
    def term_counts(self,system):return system.term_counts
    def _evaluate(self,term,provider,shape,validity=None):
        try:
            with np.errstate(all='ignore'):
                result=np.broadcast_to(term.function(*(provider(*key) for key in term.arguments)),shape)
            used=result if validity is None else result[validity]
            if not np.isfinite(used).all() or np.iscomplexobj(result):raise FloatingPointError('Nonfinite or complex term on valid points')
            return result
        except (FloatingPointError,ZeroDivisionError,OverflowError) as error:raise InvalidCandidate('Term evaluation failed: '+str(error)) from error
    def fit(self,system,visible,mask):
        fields,tt,x,y,active,crop=context(visible,mask);shape=fields['u'].shape;cache={}
        window_key=visible.get('_cache_key')
        def provider(field,axes):
            key=(field,axes)
            if key in cache:return cache[key]
            persistent=(window_key,key) if window_key is not None and axes and field in FIELDS else None
            if persistent is not None and persistent in self._fit_cache:
                self._fit_cache.move_to_end(persistent)
                cache[key]=self._fit_cache[persistent];return cache[key]
            if field=='coordinate':value={'x':x[None,None,:],'y':y[None,:,None],'t':tt[:,None,None]}[axes]
            else:
                value=fields[field]
                for axis in ('x','y'):
                    value=spatial_derivative(value,2 if axis=='x' else 1,x if axis=='x' else y,axes.count(axis))
                for _ in range(axes.count('t')):value=np.gradient(value,tt,axis=0,edge_order=2)
            cache[key]=value
            if persistent is not None and value.nbytes<=self.fit_cache_mb*1024**2:
                self._fit_cache[persistent]=value;self._fit_cache_bytes+=value.nbytes
                while self._fit_cache_bytes>self.fit_cache_mb*1024**2:
                    _,old=self._fit_cache.popitem(last=False);self._fit_cache_bytes-=old.nbytes
            return value
        radius=spatial_radius(system);fit_active=closed_active(active,radius)
        valid=np.broadcast_to(fit_active,shape).copy();valid[:2]=False;valid[-2:]=False
        if not valid.any():raise InvalidCandidate('No interior points remain after derivative collar')
        indices=np.flatnonzero(valid);indices=indices[::max(1,int(np.ceil(len(indices)/self.max_fit_points)))]
        coefficients=[];scores=[];scales=[];anchors=[]
        fixed_anchors=system.anchor_indices or tuple(structural_anchor(row) for row in system.rows)
        for row,anchor in zip(system.rows,fixed_anchors):
            A=np.column_stack([self._evaluate(term,provider,shape,valid).ravel()[indices] for term in row])
            # Scale before squaring, avoiding overflow for finite but huge terms.
            maxima=np.max(np.abs(A),axis=0)
            if np.any(maxima==0):raise InvalidCandidate('Zero fitted basis column')
            rms=maxima*np.sqrt(np.mean((A/maxima)**2,axis=0))
            if not np.isfinite(rms).all() or np.any(rms<1e-14):raise InvalidCandidate('Zero/nonfinite fitted basis scale')
            B=A/rms
            # The anchor is fixed at parse time, including across trajectories.
            # A degenerate window rejects this candidate instead of changing it.
            if np.sqrt(np.var(B[:,anchor]))*rms[anchor]<=1e-10:
                raise InvalidCandidate('Fixed structural anchor has no variation in visible window')
            others=[i for i in range(A.shape[1]) if i!=anchor]
            try:beta,_,rank,_=np.linalg.lstsq(B[:,others],-B[:,anchor],rcond=1e-10)
            except np.linalg.LinAlgError as error:raise InvalidCandidate('Coefficient regression failed') from error
            if rank<B.shape[1]-1:raise InvalidCandidate('Rank-deficient coefficient regression')
            coef=np.empty(A.shape[1]);coef[anchor]=1.;coef[others]=beta*rms[anchor]/rms[others]
            residual=B[:,anchor]+np.sum(B[:,others]*beta,axis=1)
            if not np.isfinite(coef).all():raise InvalidCandidate('Nonfinite fitted coefficients')
            energy=float(np.sum((B[:,anchor]-B[:,anchor].mean())**2))
            if energy<=0:raise InvalidCandidate('R2 undefined for constant first basis term')
            scores.append(1-float(np.sum(residual**2))/energy);coefficients.append(coef.tolist());scales.append(float(rms[anchor]));anchors.append(anchor)
        result=dict(rows=coefficients,residual_scales=scales,fit_points=len(indices),source='visible history only',anchor_indices=anchors,anchor_coefficients=1.,anchor_policy='structural_pure_time_then_canonical_v1')
        self.last_diagnostics=dict(fit_points=len(indices),r2=scores)
        return result,tuple(scores)
    def forecast(self,system,coefficients,visible,future_times,mask):
        start=time.monotonic()
        fields,tt,x,y,active,crop=context(visible,mask);future=np.asarray(future_times,float)
        radius=spatial_radius(system);active=closed_active(active,radius)
        if not active.any():raise InvalidCandidate('No free points after boundary collar')
        if future.ndim!=1 or not len(future) or not np.all(np.diff(np.r_[tt[-1],future])>0):raise InvalidCandidate('Future times must be strictly increasing')
        steps=np.diff(np.r_[tt[-2:],future]);dt=float(steps[0])
        if not np.allclose(steps,dt,rtol=1e-5,atol=1e-10):raise InvalidCandidate('Current backward stepping requires uniform time spacing')
        analytic=self.analytic_jacobian and all(term.gradient is not None for row in system.rows for term in row)
        shape=active.shape;n=int(active.sum());sparsity=None
        if not analytic:
            index=np.full(shape,-1,int);index[active]=np.arange(n);rr=[];cc=[]
            for i,j in zip(*np.nonzero(active)):
                center=index[i,j]
                neighbors=[index[a,b] for a,b in product(range(max(0,i-radius),min(shape[0],i+radius+1)),range(max(0,j-radius),min(shape[1],j+radius+1))) if index[a,b]>=0]
                for equation in range(3):
                    for field in range(3):
                        rr.extend([equation*n+center]*len(neighbors));cc.extend([field*n+v for v in neighbors])
            sparsity=coo_matrix((np.ones(len(rr)),(rr,cc)),shape=(3*n,3*n)).tocsr()
        operators={}
        if analytic:
            free=np.flatnonzero(active.ravel())
            for row in system.rows:
                for term in row:
                    for field,axes in term.arguments:
                        if field not in FIELDS or axes in operators:continue
                        dx=derivative_matrix(tuple(x),axes.count('x')) if 'x' in axes else eye(len(x),format='csr')
                        dy=derivative_matrix(tuple(y),axes.count('y')) if 'y' in axes else eye(len(y),format='csr')
                        op=kron(dy,dx,format='csr')[free][:,free]
                        operators[axes]=op*(dt**(-axes.count('t')))
        history={f:[a[-2].copy(),a[-1].copy()] for f,a in fields.items()};fixed={f:a[-1].copy() for f,a in fields.items()}
        calls=0;jac_calls=0;predictions=[];diagnostics=[]
        original_scale=max(max(float(np.max(np.abs(a))) for a in fields.values()),1.)
        linear=analytic and self.linear_fast_path and all(term.affine for row in system.rows for term in row)
        constant_jac=linear and not any(('coordinate','t') in term.arguments for row in system.rows for term in row)
        factor=None;linear_jac=None
        for now in future:
            last_flat=None;last_provider=None
            def check_budget():
                if calls>self.max_calls:raise InvalidCandidate(f'Implicit rollout residual-call budget exceeded: {calls}>{self.max_calls}')
                if time.monotonic()-start>self.max_seconds:raise InvalidCandidate(f'Implicit rollout time budget exceeded: limit={self.max_seconds}s')
            def provider_for(flat):
                nonlocal last_flat,last_provider
                check_budget()
                if last_flat is not None and np.array_equal(flat,last_flat):return last_provider
                if not np.isfinite(flat).all() or np.max(np.abs(flat))>100*original_scale:raise InvalidCandidate('Unstable implicit state')
                state={f:fixed[f].copy() for f in FIELDS}
                for k,f in enumerate(FIELDS):state[f][active]=flat[k*n:(k+1)*n]
                cache={}
                def provider(field,axes):
                    key=(field,axes)
                    if key in cache:return cache[key]
                    if field=='coordinate':value={'x':x[None,:],'y':y[:,None],'t':now}[axes]
                    else:
                        order=axes.count('t')
                        value=state[field] if order==0 else (state[field]-history[field][-1])/dt if order==1 else (state[field]-2*history[field][-1]+history[field][-2])/dt**2
                        for axis in ('x','y'):value=spatial_derivative(value,1 if axis=='x' else 0,x if axis=='x' else y,axes.count(axis))
                    cache[key]=value;return value
                last_flat=flat.copy();last_provider=provider
                return provider
            def residual(flat):
                nonlocal calls
                calls+=1;provider=provider_for(flat)
                return np.concatenate([sum(float(c)*self._evaluate(term,provider,shape,active)[active] for c,term in zip(coef,row))/max(scale,1e-12)
                    for row,coef,scale in zip(system.rows,coefficients['rows'],coefficients['residual_scales'])])
            def jacobian(flat):
                nonlocal jac_calls
                jac_calls+=1;provider=provider_for(flat);blocks=[]
                for row,coef,scale in zip(system.rows,coefficients['rows'],coefficients['residual_scales']):
                    block=[None,None,None]
                    for c,term in zip(coef,row):
                        with np.errstate(all='ignore'):
                            gradients=term.gradient(*(provider(*key) for key in term.arguments))
                        for key,gradient in zip(term.arguments,gradients):
                            field,axes=key
                            if field not in FIELDS:continue
                            value=np.broadcast_to(gradient,shape)[active]*float(c)/max(scale,1e-12)
                            if not np.isfinite(value).all():raise InvalidCandidate('Nonfinite analytic Jacobian')
                            part=diags(value,format='csr')@operators[axes];k=FIELDS.index(field)
                            block[k]=part if block[k] is None else block[k]+part
                    blocks.append([coo_matrix((n,n)).tocsr() if part is None else part for part in block])
                return bmat(blocks,format='csr')
            initial=np.concatenate([history[f][-1][active] for f in FIELDS])
            if linear:
                if factor is None or not constant_jac:
                    linear_jac=jacobian(initial)
                    try:factor=splu(linear_jac.tocsc())
                    except RuntimeError as error:raise InvalidCandidate('Singular affine implicit system') from error
                updated=initial-factor.solve(residual(initial))
                solved=OptimizeResult(x=updated,success=True,status=1,nfev=1,jac=linear_jac)
            else:
                solved=least_squares(residual,initial,jac=jacobian if analytic else '2-point',jac_sparsity=sparsity,method='trf',tr_solver='lsmr',max_nfev=self.max_nfev,
                                     ftol=1e-8,xtol=1e-8,gtol=1e-8)
            norm=float(np.sqrt(np.mean(residual(solved.x)**2)))
            if not solved.success or norm>self.residual_tolerance:raise InvalidCandidate(f'Implicit step failed: status={solved.status}, normalized residual={norm:.3g}')
            if not diagnostics:
                jac=solved.jac.tocsr().copy()
                threshold=max(float(np.max(np.abs(jac.data))),1.)*1e-12
                jac.data[np.abs(jac.data)<threshold]=0.;jac.eliminate_zeros()
                if structural_rank(jac)<3*n:raise InvalidCandidate('Structurally underdetermined implicit step')
                if 3*n<=500:
                    singular=np.linalg.svd(jac.toarray(),compute_uv=False)
                    if singular[-1]<1e-10*singular[0]:raise InvalidCandidate('Rank-deficient implicit step')
                    conditioning=dict(method='dense Jacobian SVD',condition=float(singular[0]/singular[-1]))
                else:
                    probe=np.random.default_rng(525).normal(size=3*n)
                    answer=lsmr(jac,probe,atol=1e-6,btol=1e-6,maxiter=200)
                    relative=float(np.linalg.norm(jac@answer[0]-probe)/np.linalg.norm(probe))
                    if relative>1e-3:raise InvalidCandidate('Implicit Jacobian solve is unreliable under the probe budget')
                    conditioning=dict(method='sparse structural rank and linear solve probe',relative_residual=relative)
            state={f:fixed[f].copy() for f in FIELDS}
            for k,f in enumerate(FIELDS):state[f][active]=solved.x[k*n:(k+1)*n];history[f].append(state[f]);history[f]=history[f][-2:]
            predictions.append(np.stack([state[f][crop] for f in FIELDS],-1));diagnostics.append(dict(time=float(now),normalized_residual=norm,nfev=solved.nfev))
        self.last_diagnostics=dict(method='affine implicit sparse LU' if linear else 'generic implicit residual / sparse least squares',boundary='non-active context and required outer/interface collar frozen at last visible values',boundary_collar_cells=radius,
            temporal='backward first difference / second difference',residual_calls=calls,jacobian_calls=jac_calls,jacobian='analytic_sparse' if analytic else 'finite_difference',seconds=time.monotonic()-start,steps=diagnostics,jacobian_check=conditioning,
            imposed_physical_template=False,future_fields_read=False)
        return np.asarray(predictions)
