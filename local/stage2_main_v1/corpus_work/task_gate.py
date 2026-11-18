"""Task-only admission gate. No Navier-Stokes/evolution-form prior, no GRE."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]/'legacy_eqgpt/layout'
sys.path[:0]=[str(ROOT/'ast_bpe_multifield_v2'),str(ROOT/'ast_bpe_multifield_v1')]
from direct_parser import Parser
from ast_runtime import expand_laplacian

FIELDS=('u','v','p');COORDINATES=('x','y','t')

def visit(n):
 yield n
 for c in n[1:]:
  if isinstance(c,tuple):yield from visit(c)

def bounded_tree(node):
 """Cheap structural limits before Laplacian/vector expansion, including EOS checks."""
 pending=[(node,0)];count=0
 while pending:
  n,depth=pending.pop();count+=1
  if count>1024 or depth>32:raise ValueError('Formula AST size/depth resource limit exceeded')
  if n[0]=='lap' and n[2]>8:raise ValueError('Laplacian AST expansion resource limit exceeded')
  for child in n[1:]:
   if isinstance(child,tuple):pending.append((child,depth+1))
 def expanded_size(n):
  size=1+sum(expanded_size(c) for c in n[1:] if isinstance(c,tuple))
  if n[0]=='lap':size=(size+3)*(2**n[2])
  elif n[0]=='divergence':size*=8
  if size>20000:raise ValueError('Predicted AST expansion resource limit exceeded')
  return size
 expanded_size(node)

def validate(text):
 if not isinstance(text,str):raise ValueError('Candidate must be LaTeX')
 rows=text.split(chr(92)*2)
 if len(rows)!=3 or any(r.count('=')!=1 for r in rows):raise ValueError('Exactly three equalities required')
 equations=[];fields=set();axes=set()
 for row in rows:
  left,right=row.split('=');kw=dict(fields=FIELDS,coordinates=COORDINATES)
  pair=(Parser(left,**kw).parse(),Parser(right,**kw).parse())
  if pair[0]==pair[1]:raise ValueError('Identically equal sides')
  local_fields=set()
  for expression in pair:
   bounded_tree(expression)
   expand_laplacian(expression,('x','y'))  # every governing row must be scalar
   for node in visit(expression):
    if node[0]=='v':
     if node[1] in FIELDS:fields.add(node[1]);local_fields.add(node[1])
     elif node[1] not in COORDINATES:raise ValueError('Undeclared symbol')
    elif node[0]=='d':axes.update(c for c in node[2] if c!='t')
    elif node[0] in ('lap','grad','divergence'):axes.update(('x','y'))
  if not local_fields:raise ValueError('Every governing equation must involve a dependent field')
  equations.append(pair)
 if fields!=set(FIELDS):raise ValueError('System must contain exactly u,v,p')
 if axes!={'x','y'}:raise ValueError('System must be spatially two-dimensional')
 return {'fields':FIELDS,'spatial':('x','y'),'equations':tuple(equations),'text':text,
         'task_restriction_only':True,'physical_equation_form_imposed':False}
