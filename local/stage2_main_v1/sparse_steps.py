"""Scaled, bounded sparse nonlinear steps; no PDE-specific assumptions."""
import time
import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import spilu,gmres,LinearOperator,splu,lsmr


def newton_direction(matrix,value,method='direct',check=lambda:None):
    start=time.monotonic();check()
    column=1/np.maximum(np.sqrt(np.asarray(matrix.power(2).sum(axis=0)).ravel()),1e-12)
    scaled=matrix@diags(column)
    rows=1/np.maximum(np.sqrt(np.asarray(scaled.power(2).sum(axis=1)).ravel()),1e-12)
    a=(diags(rows)@scaled).tocsc();rhs=-rows*value;iterations=[]
    if method=='ilu_gmres':
        try:
            ilu=spilu(a,drop_tol=1e-4,fill_factor=8)
            pre=LinearOperator(a.shape,matvec=ilu.solve)
            def progress(norm):check();iterations.append(float(norm))
            answer,info=gmres(a,rhs,M=pre,rtol=1e-8,atol=1e-12,restart=40,maxiter=5,
                              callback=progress,callback_type='pr_norm')
            if info!=0:raise RuntimeError('GMRES budget incomplete')
            used='ilu_gmres'
        except RuntimeError:
            check();answer=splu(a).solve(rhs);used='direct_fallback'
    else:answer=splu(a).solve(rhs);used='direct'
    direction=column*answer
    error=float(np.linalg.norm(matrix@direction+value)/max(np.linalg.norm(value),1e-30))
    check()
    return direction,dict(method=used,linear_relative_residual=error,
                         linear_iterations=len(iterations),linear_seconds=time.monotonic()-start)


def regularized_direction(matrix,value,damping,check=lambda:None):
    """Right-scaled LM step; minimizes original, not row-reweighted, residual."""
    check();column=1/np.maximum(np.sqrt(np.asarray(matrix.power(2).sum(axis=0)).ravel()),1e-12)
    a=(matrix@diags(column)).tocsr()
    # Augmented LSMR avoids forming J^T J and its squared condition number.
    answer=lsmr(a,-value,damp=np.sqrt(damping),atol=1e-7,btol=1e-7,maxiter=250)
    check();return column*answer[0],dict(method='regularized_lsmr',linear_iterations=int(answer[2]),
                                      damping=float(damping),linear_stop=int(answer[1]))
