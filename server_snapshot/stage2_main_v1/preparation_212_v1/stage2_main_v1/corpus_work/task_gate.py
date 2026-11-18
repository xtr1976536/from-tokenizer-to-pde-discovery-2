"""Task-only admission gate. No Navier-Stokes/evolution-form prior, no GRE."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]/'legacy_eqgpt/layout'
sys.path[:0]=[str(ROOT/'ast_bpe_multifield_v2'),str(ROOT/'ast_bpe_multifield_v1')]
from direct_parser import Parser

FIELDS=('u','v','p');COORDINATES=('x','y','t')

def visit(n):
 yield n
 for c in n[1:]:
  if isinstance(c,tuple):yield from visit(c)

def validate(text):
 if not isinstance(text,str):raise ValueError('Candidate must be LaTeX')
 rows=text.split(chr(92)*2)
 if len(rows)!=3 or any(r.count('=')!=1 for r in rows):raise ValueError('Exactly three equalities required')
 equations=[];fields=set();axes=set()
 for row in rows:
  left,right=row.split('=');kw=dict(fields=FIELDS,coordinates=COORDINATES)
  pair=(Parser(left,**kw).parse(),Parser(right,**kw).parse())
  if pair[0]==pair[1]:raise ValueError('Identically equal sides')
  for expression in pair:
   for node in visit(expression):
    if node[0]=='v':
     if node[1] in FIELDS:fields.add(node[1])
     elif node[1] not in COORDINATES:raise ValueError('Undeclared symbol')
    elif node[0]=='d':axes.update(c for c in node[2] if c!='t')
    elif node[0] in ('lap','grad','divergence'):axes.update(('x','y'))
  equations.append(pair)
 if fields!=set(FIELDS):raise ValueError('System must contain exactly u,v,p')
 if axes!={'x','y'}:raise ValueError('System must be spatially two-dimensional')
 return {'fields':FIELDS,'spatial':('x','y'),'equations':tuple(equations),'text':text,
         'task_restriction_only':True,'physical_equation_form_imposed':False}
