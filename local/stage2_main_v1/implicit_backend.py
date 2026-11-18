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
from scipy.interpolate import interp1d
from .contracts import InvalidCandidate
from .sparse_steps import newton_direction,regularized_direction
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
def derivative_matrix(coordinates,order,bias=0):
    values=np.asarray(coordinates,float);size=len(values)
    width=3 if order<=2 else 5
    if size<width:raise InvalidCandidate('Insufficient grid points for spatial stencil')
    spacing=np.diff(values)
    if not np.allclose(spacing,spacing[0],rtol=1e-5,atol=1e-12):raise InvalidCandidate('Spatial stencils require uniform Cartesian coordinates')
    rows=[];columns=[];weights=[]
    for i in range(size):
        start=min(max(0,i-width//2+(bias if order==1 else 0)),size-width);indices=np.arange(start,start+width)
        offsets=indices-i;matrix=np.asarray([offsets.astype(float)**k for k in range(width)])
        target=np.zeros(width);target[order]=float(__import__('math').factorial(order))
        w=np.linalg.solve(matrix,target)/spacing[0]**order
        rows.extend([i]*width);columns.extend(indices);weights.extend(w)
    return coo_matrix((weights,(rows,columns)),shape=(size,size)).tocsr()


def spatial_derivative(array,axis,coordinates,order,bias=0):
    if not order:return array
    values=np.asarray(coordinates,dtype=float)
    if order>4:raise InvalidCandidate('Spatial jet order exceeds4')
    matrix=derivative_matrix(tuple(values),order,bias)
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
                 analytic_jacobian=True,fit_cache_mb=128,linear_fast_path=True,
                 nonlinear_solver='hybrid',linear_maxiter=1000,newton_maxiter=20,
                 diagnostic_approximate_rollout=False,accept_unconverged_steps=True,spatial_scheme='centered',
                 newton_linear_solver='direct',regularized_fallback=False,temporal_substeps=1):
        self.max_fit_points=max_fit_points;self.max_nfev=max_nfev;self.max_calls=max_calls
        self.max_seconds=max_seconds;self.residual_tolerance=residual_tolerance;self.last_diagnostics={}
        self.analytic_jacobian=analytic_jacobian;self.fit_cache_mb=fit_cache_mb
        self.linear_fast_path=linear_fast_path
        if nonlinear_solver not in ('hybrid','trf'):raise ValueError('Unknown nonlinear solver')
        self.nonlinear_solver=nonlinear_solver;self.linear_maxiter=linear_maxiter
        self.newton_maxiter=int(newton_maxiter)
        self.diagnostic_approximate_rollout=bool(diagnostic_approximate_rollout)
        self.accept_unconverged_steps=bool(accept_unconverged_steps)
        if spatial_scheme not in ('centered','paired_biased'):raise ValueError('Unknown spatial scheme')
        self.spatial_scheme=spatial_scheme
        if newton_linear_solver not in ('direct','ilu_gmres'):raise ValueError('Unknown Newton linear solver')
        self.newton_linear_solver=newton_linear_solver;self.regularized_fallback=bool(regularized_fallback)
        if int(temporal_substeps)!=temporal_substeps or not 1<=temporal_substeps<=8:
            raise ValueError('temporal_substeps must be an integer in 1..8')
        self.temporal_substeps=int(temporal_substeps)
        self._fit_cache=OrderedDict();self._fit_cache_bytes=0
    def derivative_bias(self,field):
        return (1 if field=='p' else -1) if self.spatial_scheme=='paired_biased' else 0
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
                    value=spatial_derivative(value,2 if axis=='x' else 1,x if axis=='x' else y,axes.count(axis),self.derivative_bias(field))
                for _ in range(axes.count('t')):value=np.gradient(value,tt,axis=0,edge_order=2)
            cache[key]=value
            if persistent is not None and value.nbytes<=self.fit_cache_mb*1024**2:
                self._fit_cache[persistent]=value;self._fit_cache_bytes+=value.nbytes
                while self._fit_cache_bytes>self.fit_cache_mb*1024**2:
                    _,old=self._fit_cache.popitem(last=False);self._fit_cache_bytes-=old.nbytes
            return value
        radius=max(spatial_radius(system),2 if self.spatial_scheme=='paired_biased' else 1)
        fit_active=closed_active(active,radius)
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
    def forecast(self,system,coefficients,visible,future_times,mask,boundary_model=None):
        if self.temporal_substeps>1:
            return self._forecast_substeps(system,coefficients,visible,future_times,mask,boundary_model)
        return self._forecast_steps(system,coefficients,visible,future_times,mask,boundary_model)

    def _forecast_substeps(self,system,coefficients,visible,future_times,mask,boundary_model):
        """Refine integration only, using observed past for startup history.

        No future fields or boundary targets are used. Coefficients are not
        refit on interpolated data. The last observed state is preserved.
        """
        old=np.asarray(visible['t'],float);future=np.asarray(future_times,float);count=self.temporal_substeps
        if len(old)<5 or future.ndim!=1 or not len(future):raise InvalidCandidate('Insufficient substep history/times')
        dt=float(old[-1]-old[-2]);steps=np.diff(np.r_[old[-2:],future])
        if dt<=0 or not np.allclose(steps,dt,rtol=1e-5,atol=1e-10):
            raise InvalidCandidate('Substeps require uniform observed and forecast times')
        small=dt/count;past=old[-1]+np.arange(-4,1)*small
        if past[0]<old[0]:raise InvalidCandidate('Substep startup extends beyond visible history')
        def resample(array):
            array=np.asarray(array)
            result=interp1d(old[-5:],array[-5:],kind='quadratic',axis=0,
                            bounds_error=True,assume_sorted=True)(past)
            result[-1]=array[-1]
            return result
        refined=dict(visible,t=past)
        for f in FIELDS:refined[f]=resample(visible[f])
        if 'halo' in visible:refined['halo']={f:resample(visible['halo'][f]) for f in FIELDS}
        refined.pop('_cache_key',None)
        times=old[-1]+np.arange(1,len(future)*count+1)*small
        try:result=self._forecast_steps(system,coefficients,refined,times,mask,boundary_model)
        except InvalidCandidate:
            step=self.last_diagnostics.get('failed_step',self.last_diagnostics.get('current_step'))
            self.last_diagnostics.update(temporal_substeps=count,internal_dt=small,
                failed_output_frame=int(np.ceil(step/count)) if step is not None else None,
                coefficients_refitted=False)
            raise
        self.last_diagnostics.update(temporal_substeps=count,internal_steps=len(times),
            output_frames=len(future),startup='quadratic interpolation of last five visible frames; last frame exact',
            coefficients_refitted=False)
        return result[count-1::count]

    def _forecast_steps(self,system,coefficients,visible,future_times,mask,boundary_model=None):
        start=time.monotonic()
        fields,tt,x,y,active,crop=context(visible,mask);future=np.asarray(future_times,float)
        radius=max(spatial_radius(system),2 if self.spatial_scheme=='paired_biased' else 1)
        active=closed_active(active,radius)
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
                        if field not in FIELDS or (field,axes) in operators:continue
                        dx=derivative_matrix(tuple(x),axes.count('x'),self.derivative_bias(field)) if 'x' in axes else eye(len(x),format='csr')
                        dy=derivative_matrix(tuple(y),axes.count('y'),self.derivative_bias(field)) if 'y' in axes else eye(len(y),format='csr')
                        op=kron(dy,dx,format='csr')[free][:,free]
                        operators[field,axes]=op*(dt**(-axes.count('t')))
        history={f:[a[-2].copy(),a[-1].copy()] for f,a in fields.items()};fixed={f:a[-1].copy() for f,a in fields.items()}
        calls=0;jac_calls=0;predictions=[];diagnostics=[]
        original_scale=max(max(float(np.max(np.abs(a))) for a in fields.values()),1.)
        linear=analytic and self.linear_fast_path and all(term.affine for row in system.rows for term in row)
        constant_jac=linear and not any(('coordinate','t') in term.arguments for row in system.rows for term in row)
        factor=None;linear_jac=None
        for step_index,now in enumerate(future):
            if boundary_model is not None:
                supplied=boundary_model(x,y,float(now))
                fixed={f:np.asarray(supplied[f],float).copy() for f in FIELDS}
                if any(a.shape!=shape or not np.isfinite(a).all() for a in fixed.values()):
                    raise InvalidCandidate('Invalid declared boundary model')
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
                        for axis in ('x','y'):value=spatial_derivative(value,1 if axis=='x' else 0,x if axis=='x' else y,axes.count(axis),self.derivative_bias(field))
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
                            part=diags(value,format='csr')@operators[field,axes];k=FIELDS.index(field)
                            block[k]=part if block[k] is None else block[k]+part
                    blocks.append([coo_matrix((n,n)).tocsr() if part is None else part for part in block])
                return bmat(blocks,format='csr')
            initial=np.concatenate([history[f][-1][active] for f in FIELDS])
            inspector=getattr(self,'inspect_initial_step',None)
            if inspector is not None and step_index==0:
                inspector(residual,jacobian if analytic else None,initial,active)
            trace=[]
            def norm_of(value):return float(np.sqrt(np.mean(value**2)))
            initial_residual=residual(initial)
            initial_residual_by_equation=np.sqrt(np.mean(initial_residual.reshape(3,n)**2,axis=1)).tolist()
            self.last_diagnostics=dict(status='solving',current_step=step_index+1,time=float(now),
                completed_steps=diagnostics,current_trace=trace,
                initial_residual_by_equation=initial_residual_by_equation,future_fields_read=False)
            if linear:
                if factor is None or not constant_jac:
                    linear_jac=jacobian(initial)
                    try:factor=splu(linear_jac.tocsc())
                    except RuntimeError as error:raise InvalidCandidate('Singular affine implicit system') from error
                updated=initial-factor.solve(residual(initial))
                solved=OptimizeResult(x=updated,success=True,status=1,nfev=1,jac=linear_jac)
            else:
                guess=initial.copy();newton_success=False
                if analytic and self.nonlinear_solver=='hybrid':
                    # Square implicit equations: equilibrated damped Newton
                    # avoids inaccurate, unpreconditioned LSMR inner solves.
                    for iteration in range(min(self.max_nfev,self.newton_maxiter)):
                        value=residual(guess);norm=norm_of(value)
                        trace.append(dict(method='damped_newton',iteration=iteration,residual=norm))
                        if norm<=min(self.residual_tolerance*.01,1e-9):
                            newton_success=True;break
                        matrix=jacobian(guess)
                        try:
                            direction,linear_info=newton_direction(matrix,value,self.newton_linear_solver,check_budget)
                            linear_info['linear_method']=linear_info.pop('method')
                            trace[-1].update(linear_info)
                        except RuntimeError:
                            if not self.regularized_fallback:
                                trace[-1]['reason']='singular_newton_matrix';break
                            direction,linear_info=regularized_direction(matrix,value,1e-2,check_budget)
                            linear_info['linear_method']=linear_info.pop('method')
                            trace[-1].update(linear_info)
                            trace[-1]['reason']='singular_newton_regularized'
                        linear_error=np.linalg.norm(matrix@direction+value)/max(np.linalg.norm(value),1e-30)
                        trace[-1]['linear_relative_residual']=float(linear_error)
                        if not np.isfinite(direction).all():break
                        if linear_error>1e-5 and trace[-1].get('linear_method')!='regularized_lsmr':break
                        accepted=False
                        for damping in (1.,.5,.25,.125,.0625,.03125,.015625):
                            trial=guess+damping*direction
                            try:trial_norm=norm_of(residual(trial))
                            except InvalidCandidate as error:
                                if 'Unstable' not in str(error) and 'Term evaluation' not in str(error):raise
                                continue
                            if trial_norm<norm*(1-1e-4*damping):
                                guess=trial;accepted=True;trace[-1]['damping']=damping;break
                        if not accepted:
                            if self.regularized_fallback:
                                # Newton solves a root equation, which need not
                                # decrease least-squares cost for inconsistent
                                # constraints. Try regularized descent before TRF.
                                for damping in (1e-4,1e-2,1.,100.):
                                    direction,info=regularized_direction(matrix,value,damping,check_budget)
                                    try:trial_norm=norm_of(residual(guess+direction))
                                    except InvalidCandidate as error:
                                        if 'Unstable' not in str(error) and 'Term evaluation' not in str(error):raise
                                        continue
                                    if trial_norm<norm*(1-1e-5):
                                        guess+=direction;accepted=True;info['linear_method']=info.pop('method');trace[-1].update(info);break
                            if not accepted:
                                trace[-1]['reason']='line_search_stagnation';break
                if newton_success:
                    solved=OptimizeResult(x=guess,success=True,status=1,nfev=len(trace),jac=jacobian(guess))
                else:
                    def monitored(flat):
                        value=residual(flat)
                        trace.append(dict(method='trf',residual=norm_of(value)))
                        return value
                    solved=least_squares(monitored,guess,jac=jacobian if analytic else '2-point',jac_sparsity=sparsity,method='trf',tr_solver='lsmr',max_nfev=self.max_nfev,
                                         x_scale='jac',tr_options=dict(atol=1e-8,btol=1e-8,maxiter=self.linear_maxiter),
                                         bounds=(-100*original_scale,100*original_scale),
                                         ftol=1e-8,xtol=1e-8,gtol=1e-8)
            norm=float(np.sqrt(np.mean(residual(solved.x)**2)))
            if not np.isfinite(norm) or not np.isfinite(solved.x).all():
                raise InvalidCandidate('Nonfinite approximate implicit state')
            # nfev exhaustion alone does not invalidate an already accurate root.
            meets_tolerance=bool(norm<=self.residual_tolerance)
            if not meets_tolerance and not self.diagnostic_approximate_rollout and not self.accept_unconverged_steps:
                self.last_diagnostics=dict(status='not_converged',failed_step=step_index+1,time=float(now),
                    normalized_residual=norm,optimizer_status=int(solved.status),trace=trace,
                    residual_by_equation=np.sqrt(np.mean(residual(solved.x).reshape(3,n)**2,axis=1)).tolist(),
                    optimizer_message=str(solved.get('message','')),optimality=float(solved.get('optimality',0.)),
                    residual_calls=calls,jacobian_calls=jac_calls,seconds=time.monotonic()-start,
                    completed_steps=diagnostics,future_fields_read=False)
                raise InvalidCandidate(f'Implicit step failed: step={step_index+1}, status={solved.status}, normalized residual={norm:.3g}')
            # In approximate diagnostic mode retain finite optimizer states
            # even without a well-conditioned unique root. Do not label them
            # as accepted PDE solutions or use them in formal selection.
            if self.diagnostic_approximate_rollout:
                conditioning=dict(method='not_enforced_in_approximate_diagnostic',unique_solution_verified=False)
            if not diagnostics and not self.diagnostic_approximate_rollout:
                jac=solved.jac.tocsr().copy()
                # Rank diagnostics must not mistake differing physical units
                # for missing dependencies. Equilibrate before thresholding.
                column=1/np.maximum(np.sqrt(np.asarray(jac.power(2).sum(axis=0)).ravel()),1e-12)
                jac=jac@diags(column)
                row_scale=1/np.maximum(np.sqrt(np.asarray(jac.power(2).sum(axis=1)).ravel()),1e-12)
                jac=(diags(row_scale)@jac).tocsr()
                threshold=max(float(np.max(np.abs(jac.data))),1.)*1e-12
                jac.data[np.abs(jac.data)<threshold]=0.;jac.eliminate_zeros()
                if structural_rank(jac)<3*n:raise InvalidCandidate('Structurally underdetermined implicit step')
                if 3*n<=500:
                    singular=np.linalg.svd(jac.toarray(),compute_uv=False)
                    if singular[-1]<1e-10*singular[0]:raise InvalidCandidate('Rank-deficient implicit step')
                    conditioning=dict(method='dense Jacobian SVD',condition=float(singular[0]/singular[-1]))
                else:
                    probe=np.random.default_rng(525).normal(size=3*n)
                    try:probe_factor=splu(jac.tocsc())
                    except RuntimeError as error:raise InvalidCandidate('Singular implicit Jacobian factorization') from error
                    answer=probe_factor.solve(probe)
                    relative=float(np.linalg.norm(jac@answer-probe)/np.linalg.norm(probe))
                    if not np.isfinite(answer).all() or relative>1e-7:
                        raise InvalidCandidate('Unreliable implicit Jacobian direct solve')
                    conditioning=dict(method='equilibrated sparse LU and linear residual probe',relative_residual=relative)
            jumps=np.sqrt(np.mean((solved.x-initial).reshape(3,n)**2,axis=1)).tolist()
            state={f:fixed[f].copy() for f in FIELDS}
            for k,f in enumerate(FIELDS):state[f][active]=solved.x[k*n:(k+1)*n];history[f].append(state[f]);history[f]=history[f][-2:]
            predictions.append(np.stack([state[f][crop] for f in FIELDS],-1));diagnostics.append(dict(time=float(now),normalized_residual=norm,nfev=solved.nfev,trace=trace,
                optimizer_success=bool(solved.success),meets_original_tolerance=meets_tolerance))
            diagnostics[-1].update(initial_residual_by_equation=initial_residual_by_equation,
                final_residual_by_equation=np.sqrt(np.mean(residual(solved.x).reshape(3,n)**2,axis=1)).tolist(),
                field_jump_rmse=jumps)
        self.last_diagnostics=dict(method='affine implicit sparse LU' if linear else 'generic implicit residual / sparse least squares',boundary='non-active context and required outer/interface collar frozen at last visible values',boundary_collar_cells=radius,
            temporal='backward first difference / second difference',residual_calls=calls,jacobian_calls=jac_calls,jacobian='analytic_sparse' if analytic else 'finite_difference',seconds=time.monotonic()-start,steps=diagnostics,jacobian_check=conditioning,
            imposed_physical_template=False,future_fields_read=False)
        self.last_diagnostics['approximate_diagnostic']=self.diagnostic_approximate_rollout
        self.last_diagnostics['unconverged_steps_accepted']=self.accept_unconverged_steps
        self.last_diagnostics['spatial_scheme']=self.spatial_scheme
        self.last_diagnostics['boundary_source']='declared_boundary_model' if boundary_model is not None else 'last_visible_frozen'
        self.last_diagnostics['all_steps_meet_tolerance']=all(step['meets_original_tolerance'] for step in diagnostics)
        return np.asarray(predictions)
