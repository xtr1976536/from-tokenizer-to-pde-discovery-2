import unittest
import numpy as np
from stage2_main_v1.implicit_backend import ImplicitBackend
from stage2_main_v1.tests.test_implicit_backend import manufactured
from stage2_main_v1.contracts import InvalidCandidate
from scipy.linalg import expm

class SubstepTests(unittest.TestCase):
 def test_refinement_improves_known_solution_without_changing_history(self):
  v,m,A,mode=manufactured();before={k:a.copy() for k,a in v.items()};times=np.arange(20,40)*.01
  text=r'u_t=\Delta(u)+p\\v_t=\Delta(v)-u\\p=u+v';original=ImplicitBackend();system=original.parse(text);coef,_=original.fit(system,v,m)
  reference=np.array([expm(A*t)@np.array([1.,.5]) for t in times])
  truth=np.stack([reference[:,0,None,None]*mode,reference[:,1,None,None]*mode,reference.sum(1)[:,None,None]*mode],-1)
  errors=[]
  for n in [1,2,4]:
   b=ImplicitBackend(temporal_substeps=n);pred=b.forecast(system,coef,v,times,m)
   self.assertEqual(pred.shape,truth.shape);errors.append(np.sqrt(np.mean((pred-truth)**2)))
   for k in before:np.testing.assert_array_equal(before[k],v[k])
  self.assertTrue(np.all(np.diff(errors)<0),errors)
 def test_refinement_rejects_nonuniform_future(self):
  v,m,_,_=manufactured();b=ImplicitBackend(temporal_substeps=2);s=b.parse(r'u_t=\Delta(u)+p\\v_t=\Delta(v)-u\\p=u+v');c,_=b.fit(s,v,m)
  with self.assertRaisesRegex(InvalidCandidate,'uniform'):b.forecast(s,c,v,[.2,.215],m)
 def test_substep_budget_is_not_reset_each_output_frame(self):
  v,m,_,_=manufactured();b=ImplicitBackend(temporal_substeps=4,max_calls=2);s=b.parse(r'u_t=\Delta(u)+p\\v_t=\Delta(v)-u\\p=u+v');c,_=b.fit(s,v,m)
  with self.assertRaisesRegex(InvalidCandidate,'budget'):b.forecast(s,c,v,np.arange(20,40)*.01,m)

if __name__=='__main__':unittest.main()
