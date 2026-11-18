"""Pretraining-only target-family quarantine, NEVER a generated-PDE ban.
Narrow policy: signatures for direct velocity-pressure/continuity systems,
pressure-Poisson closures and vorticity/streamfunction equivalents. Other fluid
families require equation-level review rather than blanket title bans.
"""
from itertools import permutations
try:from .structure_latex import nodes,canon
except ImportError:from structure_latex import nodes,canon

def field(n,name):return n==('v',name)
def d(name,axis):return ('d',('v',name),axis)
def flattened(n):
 if n[0]=='add':return [t for c in n[1:] for t in flattened(c)]
 if n[0]=='lap' and n[1][0]=='v' and n[2]==1:return [d(n[1][1],'xx'),d(n[1][1],'yy')]
 return [canon(n)]
def reasons(asts,fields):
 support=[set(flattened(n)) for n in asts];found=[]
 for a,b,p in permutations(fields,3):
  continuity={d(a,'x'),d(b,'y')}
  if not any(row==continuity for row in support):continue
  first=[r for r in support if {d(a,'t'),d(p,'x')}<=r]
  second=[r for r in support if {d(b,'t'),d(p,'y')}<=r]
  if first and second:
   found.append('Cylinder-like momentum+pressure-gradient+incompressibility subsystem; includes coefficient/viscous-limit/forcing variants')
 for a,b in permutations(fields,2):
  elliptic={('v',a),d(b,'xx'),d(b,'yy')}
  if not any(row==elliptic for row in support):continue
  for row in support:
   if d(a,'t') not in row:continue
   cross1=canon(('mul',d(b,'y'),d(a,'x')));cross2=canon(('mul',d(b,'x'),d(a,'y')))
   if {cross1,cross2}<=row:found.append('Vorticity-streamfunction form of2D incompressible target/near variant')
 for a,b,p in permutations(fields,3):
  if not any({d(a,'t'),d(p,'x')}<=r for r in support) or not any({d(b,'t'),d(p,'y')}<=r for r in support):continue
  for row in support:
   if {d(p,'xx'),d(p,'yy')}<=row and any(t[0] in ('mul','pow') for t in row):found.append('Velocity-pressure momentum plus pressure-Poisson closure; source equivalence review required')
 # A single streamfunction equation can encode the entire incompressible
 # target, even when there are no explicitly named velocity/pressure fields.
 try:
  import sympy as sp
  from equivalence import expanded_rows, X, Y, T
  expanded,functions=expanded_rows(asts,fields)
  for function in functions.values():
   advective={sp.diff(function,Y)*sp.diff(function,X,3),
              sp.diff(function,Y)*sp.diff(function,X,Y,2),
              sp.diff(function,X)*sp.diff(function,X,2,Y),
              sp.diff(function,X)*sp.diff(function,Y,3)}
   time={sp.diff(function,X,2,T),sp.diff(function,Y,2,T)}
   viscosity={sp.diff(function,X,4),sp.diff(function,X,2,Y,2),sp.diff(function,Y,4)}
   if any(advective<=row and (time<=row or viscosity<=row) for row in expanded):
    found.append('Single-streamfunction vorticity equation equivalent or close to the 2D incompressible target')
 except (ValueError,KeyError,TypeError,NotImplementedError,RecursionError):
  pass
 return sorted(set(found))
