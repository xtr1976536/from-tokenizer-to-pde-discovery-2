import unittest
import numpy as np
from scipy.sparse import diags
from stage2_main_v1.sparse_steps import newton_direction,regularized_direction
from stage2_main_v1.implicit_backend import ImplicitBackend
from stage2_main_v1.tests.test_implicit_backend import manufactured

class SparseStepTests(unittest.TestCase):
 def test_preconditioned_and_direct_solutions_match(self):
  n=200;a=diags([-np.ones(n-1),4*np.ones(n),-.8*np.ones(n-1)],[-1,0,1]).tocsr();r=np.random.default_rng(525).normal(size=n)
  direct,_=newton_direction(a,r);pre,info=newton_direction(a,r,'ilu_gmres')
  np.testing.assert_allclose(pre,direct,rtol=1e-7,atol=1e-9)
  self.assertLess(info['linear_relative_residual'],1e-7)
 def test_regularized_step_reduces_original_residual(self):
  a=diags([1e-5,1.,100.]).tocsr();r=np.array([1.,2.,3.]);delta,info=regularized_direction(a,r,.01)
  self.assertLess(np.linalg.norm(a@delta+r),np.linalg.norm(r))
 def test_deadline_is_checked(self):
  class Budget(Exception):pass
  def stop():raise Budget()
  with self.assertRaises(Budget):newton_direction(diags([1.,1.]),np.ones(2),'ilu_gmres',stop)
 def test_preconditioned_nonlinear_full_rollout_matches_direct(self):
  v,m,_,_=manufactured();text=r'u_t=\Delta(u)+p+u*v\\v_t=\Delta(v)-u\\p=u+v'
  direct=ImplicitBackend(newton_linear_solver='direct',linear_fast_path=False)
  iterative=ImplicitBackend(newton_linear_solver='ilu_gmres',linear_fast_path=False)
  s=direct.parse(text);coef,_=direct.fit(s,v,m)
  for i,term in enumerate(s.rows[0]):
   if set(term.arguments)=={('u',''),('v','')}:coef['rows'][0][i]=.2
  times=np.arange(20,40)*.01
  one=direct.forecast(s,coef,v,times,m);two=iterative.forecast(s,coef,v,times,m)
  np.testing.assert_allclose(one,two,rtol=1e-6,atol=1e-8)
  self.assertTrue(iterative.last_diagnostics['all_steps_meet_tolerance'])

if __name__=='__main__':unittest.main()
