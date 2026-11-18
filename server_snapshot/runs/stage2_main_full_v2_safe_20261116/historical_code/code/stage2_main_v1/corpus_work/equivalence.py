"""Conservative differential-support deduplication across explicit/compact notation.

Expand each fitted basis term separately, so unknown coefficients never cause
cancellation between two independent basis columns. Do not claim equivalence
under arbitrary coordinate transforms or source side conditions.
"""
from hashlib import sha256
from itertools import permutations
import sympy as sp
from sympy.core.function import AppliedUndef
from ast_runtime import expand_laplacian
from structure_latex import structure_key

X,Y,T=sp.symbols('x y t',real=True)
AXES={'x':X,'y':Y,'t':T}


def expanded_rows(asts,fields):
    functions={name:sp.Function(name,real=True)(X,Y,T) for name in fields}
    def expression(node):
        kind=node[0]
        if kind=='v':return functions[node[1]] if node[1] in functions else AXES[node[1]]
        if kind=='n':return sp.Rational(str(node[1]))
        if kind=='neg':return -expression(node[1])
        if kind=='add':return sum(expression(c) for c in node[1:])
        if kind=='mul':return sp.prod(expression(c) for c in node[1:])
        if kind=='div':return expression(node[1])/expression(node[2])
        if kind=='pow':return expression(node[1])**expression(node[2])
        if kind=='d':return sp.diff(expression(node[1]),*[AXES[a] for a in node[2]])
        if kind=='fn':
            function={'abs':sp.Abs,'ln':sp.log}.get(node[1],getattr(sp,node[1],None))
            if function is None:raise ValueError('Unsupported function in equivalence key')
            return function(expression(node[2]))
        raise ValueError('Unexpanded scalar operator '+kind)
    result=[]
    for ast in asts:
        cores=ast[1:] if ast[0]=='add' else (ast,)
        terms=set()
        for core in cores:
            value=sp.expand(expression(expand_laplacian(core,('x','y'))).doit())
            for term in sp.Add.make_args(value):
                if term==0:continue
                coefficient,remainder=term.as_coeff_Mul(rational=True)
                if coefficient==0:continue
                terms.add(sp.powsimp(remainder))
                if len(terms)>2048:raise ValueError('Expansion budget exceeded')
        result.append(terms)
    return result,functions


def key(asts,fields):
    try:
        rows,functions=expanded_rows(asts,fields)
        derivatives=set().union(*(term.atoms(sp.Derivative) for row in rows for term in row))
        variants=[]
        for order in permutations(fields):
            names=dict(zip(fields,order))
            for swap in (False,True):
                convert={function:sp.Symbol('F_'+names[name]) for name,function in functions.items()}
                convert.update({X:sp.Symbol('C_y' if swap else 'C_x'),Y:sp.Symbol('C_x' if swap else 'C_y'),T:sp.Symbol('C_t')})
                for derivative in derivatives:
                    if not isinstance(derivative.expr,AppliedUndef):raise ValueError('Non-jet derivative remains')
                    name=str(derivative.expr.func)
                    axes=''.join(str(a)*n for a,n in derivative.variable_count)
                    if swap:axes=axes.translate(str.maketrans('xy','yx'))
                    axes=''.join(sorted(axes,key='xyt'.index))
                    convert[derivative]=sp.Symbol('J_'+names[name]+'_'+axes)
                encoded=sorted(tuple(sorted(sp.srepr(term.xreplace(convert)) for term in row)) for row in rows)
                variants.append(repr(encoded))
        return 'expanded-v1:'+sha256(min(variants).encode()).hexdigest()
    except (ValueError,KeyError,TypeError,NotImplementedError,RecursionError):
        return 'syntax-v1:'+structure_key(asts,fields)
