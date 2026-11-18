"""Direct LaTeX/AST fitted-term structure normalization; no GRE representation.
Original coefficients/signs remain in provenance, not structural training strings.
"""
from pathlib import Path
import sys,itertools,hashlib,json
import sympy as sp
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]/'legacy_eqgpt/layout'
sys.path[:0]=[str(ROOT/'ast_bpe_multifield_v1'),str(ROOT/'ast_bpe_multifield_v2')]
from latex_render import latex
from direct_parser import parse
CANONICAL=('u','v','p','w')

def nodes(n):
 yield n
 for c in n[1:]:
  if isinstance(c,tuple):yield from nodes(c)
def scalar(n,params):
 if n[0]=='n':return sp.Rational(str(n[1]))
 if n[0]=='v' and n[1] in params:return sp.Symbol(n[1])
 if n[0]=='neg':
  a=scalar(n[1],params);return -a if a is not None else None
 if n[0] in ('add','mul','div','pow'):
  cs=[scalar(c,params) for c in n[1:]]
  if any(c is None for c in cs):return None
  if n[0]=='add':return sum(cs)
  if n[0]=='mul':return sp.prod(cs)
  if n[0]=='div':return cs[0]/cs[1]
  return cs[0]**cs[1]
 return None

def canon(n):
 if not isinstance(n,tuple):return n
 kind=n[0];cs=[canon(c) if isinstance(c,tuple) else c for c in n[1:]]
 if kind=='n':return ('n',int(n[1]) if n[1]==int(n[1]) else float(n[1]))
 if kind=='pow' and cs[1]==('n',1):return cs[0]
 if kind=='pow' and cs[1]==('n',0):return ('n',1)
 if kind in ('add','mul'):
  flat=[]
  for c in cs:flat.extend(c[1:] if isinstance(c,tuple) and c[0]==kind else [c])
  if kind=='mul':
   if ('n',0) in flat:return ('n',0)
   flat=[c for c in flat if c!=('n',1)]
  else:flat=[c for c in flat if c!=('n',0)]
  if not flat:return ('n',1 if kind=='mul' else 0)
  cs=sorted(flat,key=repr)
  if kind=='mul':
   counts=Counter()
   for factor in cs:
    if factor[0]=='pow' and factor[2][0]=='n' and isinstance(factor[2][1],int) and factor[2][1]>0:
     counts[factor[1]]+=factor[2][1]
    else:counts[factor]+=1
   cs=sorted([factor if count==1 else ('pow',factor,('n',count)) for factor,count in counts.items()],key=repr)
  if len(cs)==1:return cs[0]
 if kind=='d':cs[1]=''.join(sorted(cs[1],key='xyt'.index))
 return (kind,*cs)

def distributed(n,params):
 """Return signed symbolic scalar x nonlinear core; distribute only valid linearities."""
 c=scalar(n,params)
 if c is not None:return [(c,('n',1))]
 k=n[0]
 if k=='add':return [v for child in n[1:] for v in distributed(child,params)]
 if k=='neg':return [(-c,a) for c,a in distributed(n[1],params)]
 if k=='pow' and n[2][0]=='n' and n[2][1]==0:return [(sp.Integer(1),('n',1))]
 if k=='pow' and n[2][0]=='n' and n[2][1]==1:return distributed(n[1],params)
 if k=='pow' and n[2][0]=='n' and n[2][1]==int(n[2][1]) and 1<=n[2][1]<=8:
  if any(v[0]=='v' and v[1] in params for v in nodes(n[1])):
   # Exact finite polynomial expansion, never assignment of an inner parameter.
   return distributed(('mul',*(n[1] for _ in range(int(n[2][1])))),params)
 if k=='mul':
  products=[(sp.Integer(1),[])]
  for child in n[1:]:
   products=[(a*c,parts+([] if core==('n',1) else [core])) for a,parts in products for c,core in distributed(child,params)]
  return [(c,('n',1) if not parts else parts[0] if len(parts)==1 else ('mul',*parts)) for c,parts in products]
 if k=='div':
  denominator=scalar(n[2],params)
  if denominator is not None:
   if sp.simplify(denominator)==0:raise ValueError('Zero denominator')
   return [(c/denominator,core) for c,core in distributed(n[1],params)]
  # A scalar multiplying the whole numerator remains an outer coefficient.
  # A parameter inside (1+a*u), however, cannot be stripped from that sum.
  if not any(v[0]=='v' and v[1] in params for v in nodes(n[2])):
   return [(c,('div',core,n[2])) for c,core in distributed(n[1],params)]
 if k in ('d','lap','grad','divergence'):
  # Differentiation, Laplace, gradient and divergence are linear over scalar constants.
  return [(c,(k,core,*n[2:])) for c,core in distributed(n[1],params) if core!=('n',1)]
 if any(v[0]=='v' and v[1] in params for v in nodes(n)):
  raise ValueError('Parameter inside nonlinear core cannot be removed as an outer fitted coefficient')
 return [(sp.Integer(1),n)]

def remap(n,mapping):
 if n[0]=='v':return ('v',mapping.get(n[1],n[1]))
 return (n[0],*(remap(c,mapping) if isinstance(c,tuple) else c for c in n[1:]))

def normalize_system(equations,source_fields,scalar_parameters=()):
 if not 1<=len(source_fields)<=4 or len(set(source_fields))!=len(source_fields):raise ValueError('Need1..4 distinct scalar fields')
 mapping=dict(zip(source_fields,CANONICAL));result=[];asts=[]
 for text in equations:
  if text.count('=')!=1:raise ValueError('One equality per source row')
  left,right=text.split('=');a,pa=parse(left,tuple(source_fields),scalar_parameters);b,pb=parse(right,tuple(source_fields),scalar_parameters);params=set(pa)|set(pb)
  if any('(' in parameter for parameter in params):
   raise ValueError('Space/time-dependent coefficient functions require explicit structural treatment')
  # Source coordinates are explicit Cartesian x/y/t; no radial/third-axis rewrite.
  if any(n[0]=='d' and set(n[2])-set('xyt') for tree in (a,b) for n in nodes(tree)):
   raise ValueError('Non-x/y/t derivative coordinates require explicit source axis mapping')
  groups={}
  for c,core in distributed(('add',a,('neg',b)),params):
   core=canon(remap(core,mapping));groups[core]=groups.get(core,sp.Integer(0))+c
  terms=sorted([core for core,c in groups.items() if sp.simplify(c)!=0],key=repr)
  if not terms:raise ValueError('Identity equation has no learnable structure')
  for core in terms:
   for n in nodes(core):
    if n[0]=='v' and n[1] not in set(CANONICAL[:len(source_fields)])|set('xyt'):raise ValueError('Unmapped symbol remains')
  tree=terms[0] if len(terms)==1 else ('add',*terms)
  asts.append(tree);result.append(latex(tree)+'=0')
 return {'fields':list(CANONICAL[:len(source_fields)]),'equations':result,'text':(chr(92)*2).join(result),
         'residual_support_ast':asts,'field_map':mapping,'coefficient_policy':'unsigned fitted outer-term support; powers/orders/nonlinear internal structure retained; original expression preserved separately'}

def structure_key(asts,fields):
 keys=[]
 for permutation in itertools.permutations(fields):
  mapping=dict(zip(fields,permutation))
  for swap in (False,True):
   def change(n):
    n=remap(n,mapping)
    def axes(v):
     if v[0]=='v' and v[1] in 'xy':return ('v',{'x':'y','y':'x'}[v[1]])
     if v[0]=='d':return ('d',axes(v[1]),v[2].translate(str.maketrans('xy','yx')))
     return (v[0],*(axes(c) if isinstance(c,tuple) else c for c in v[1:]))
    return canon(axes(n) if swap else n)
   keys.append(repr(sorted([change(n) for n in asts],key=repr)))
 return hashlib.sha256(min(keys).encode()).hexdigest()
