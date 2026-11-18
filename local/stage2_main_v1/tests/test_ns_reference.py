"""NS reference is a test only: no target template is passed to training."""
import unittest
import numpy as np
from stage2_main_v1.implicit_backend import ImplicitBackend,derivative_matrix
from stage2_main_v1.contracts import InvalidCandidate
TEXT=r'u_t+u*u_x+v*u_y+p_x-\Delta(u)=0\\v_t+u*v_x+v*v_y+p_y-\Delta(v)=0\\u_x+v_y=0'

def coefficients(system,nu):
 return dict(rows=[[-nu if term.arguments and all(f in ('u','v') and a in ('xx','yy') for f,a in term.arguments) else 1. for term in row] for row in system.rows],residual_scales=[1.,1.,1.])

def case(n,steady=False):
 x=np.linspace(0,1,n);y=x.copy();xx,yy=np.meshgrid(x,y);nu=.01;tt=np.arange(20)*.0005;future=np.arange(20,40)*.0005
 def solution(times):
  if steady:return np.array([np.stack([yy*(1-yy),np.zeros_like(xx),-2*nu*xx],-1) for t in times])
  return np.array([np.stack([-np.cos(np.pi*xx)*np.sin(np.pi*yy)*np.exp(-2*nu*np.pi**2*t),np.sin(np.pi*xx)*np.cos(np.pi*yy)*np.exp(-2*nu*np.pi**2*t),-.25*(np.cos(2*np.pi*xx)+np.cos(2*np.pi*yy))*np.exp(-4*nu*np.pi**2*t)],-1) for t in times])
 values=solution(tt);v={f:values[...,i] for i,f in enumerate(('u','v','p'))};v.update(x=x,y=y,t=tt)
 return v,np.ones((n,n),bool),future,solution,nu

class NSReferenceTests(unittest.TestCase):
 def test_paired_ns_jacobian_matches_numerical_direction(self):
  v,m,t,sol,nu=case(13);b=ImplicitBackend(spatial_scheme='paired_biased');s=b.parse(TEXT)
  class Inspected(Exception):pass
  def inspect(res,jac,initial,active):
   direction=np.random.default_rng(525).normal(size=len(initial));direction/=np.linalg.norm(direction)
   eps=1e-6;num=(res(initial+eps*direction)-res(initial-eps*direction))/(2*eps)
   exact=jac(initial)@direction
   self.assertLess(np.linalg.norm(num-exact)/np.linalg.norm(exact),1e-7)
   raise Inspected()
  b.inspect_initial_step=inspect
  with self.assertRaises(Inspected):b.forecast(s,coefficients(s,nu),v,t,m)
 def test_steady_ns_preserved_with_status_zero_and_rank_checked(self):
  v,m,t,sol,nu=case(13,True);b=ImplicitBackend(spatial_scheme='paired_biased',nonlinear_solver='trf',max_nfev=1)
  s=b.parse(TEXT);pred=b.forecast(s,coefficients(s,nu),v,t,m)
  np.testing.assert_allclose(pred,sol(t),atol=1e-10)
  self.assertTrue(b.last_diagnostics['all_steps_meet_tolerance'])
 def test_centered_pressure_defect_remains_visible(self):
  v,m,t,sol,nu=case(13,True);b=ImplicitBackend(spatial_scheme='centered');s=b.parse(TEXT)
  with self.assertRaisesRegex(InvalidCandidate,'Rank-deficient'):b.forecast(s,coefficients(s,nu),v,t,m)
 def test_nonstationary_ns_spatial_refinement(self):
  errors=[]
  for n in [9,13,17]:
   v,m,t,sol,nu=case(n);b=ImplicitBackend(spatial_scheme='paired_biased');s=b.parse(TEXT)
   before={f:v[f].copy() for f in ('u','v','p')}
   pred=b.forecast(s,coefficients(s,nu),v,t,m,boundary_model=lambda x,y,time:{f:sol([time])[0,...,i] for i,f in enumerate(('u','v','p'))})
   a=np.zeros_like(m);a[2:-2,2:-2]=True
   errors.append(np.sqrt(np.mean((pred-sol(t))[:,a]**2,axis=(0,1))))
   self.assertLess(max(step['normalized_residual'] for step in b.last_diagnostics['steps']),1e-8)
   for f in before:np.testing.assert_array_equal(before[f],v[f])
  self.assertTrue(np.all(np.diff(np.array(errors),axis=0)<0))
 def test_pressure_checkerboard_null_is_specific_to_centered_scheme(self):
  from scipy.linalg import svdvals
  _,mask,_,_,_=case(13);active=mask.copy();active[:2]=False;active[-2:]=False;active[:,:2]=False;active[:,-2:]=False;n=int(active.sum())
  for scheme,expect_rank_defect in [('centered',True),('paired_biased',False)]:
   b=ImplicitBackend(spatial_scheme=scheme);s=b.parse(TEXT);coeff=coefficients(s,.01)
   inspector={}
   def inspect(res,jac,initial,active_now):
    matrix=jac(initial).toarray();values=svdvals(matrix);inspector.update(rank=int(np.sum(values>values[0]*1e-10)),unknowns=len(values));raise RuntimeError('matrix captured')
   b.inspect_initial_step=inspect
   try:b.forecast(s,coeff,dict(u=np.zeros((20,13,13)),v=np.zeros((20,13,13)),p=np.zeros((20,13,13)),t=np.arange(20)*.001,x=np.linspace(0,1,13),y=np.linspace(0,1,13)),np.arange(20,40)*.001,mask)
   except RuntimeError as error:self.assertEqual(str(error),'matrix captured')
   self.assertEqual(inspector['rank']<inspector['unknowns'],expect_rank_defect)
 def test_biased_derivative_is_exact_on_quadratics(self):
  x=np.linspace(0,1,13)
  for bias in [-1,1]:np.testing.assert_allclose(derivative_matrix(tuple(x),1,bias)@(x*x),2*x,atol=1e-12)

if __name__=='__main__':unittest.main()
