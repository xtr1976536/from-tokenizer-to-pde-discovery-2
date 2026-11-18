import unittest
import numpy as np
from stage2_main_v1.scoring import qualified_fit,reward
from stage2_main_v1.contracts import InvalidCandidate
from stage2_main_v1.runner import candidates,CandidateBudgetIncomplete
class GateTests(unittest.TestCase):
 def check(self,rows,threshold=.3):
  class Data:
   def visible(self,w,role):return w,None,None
  class Numerics:
   def fit(self,s,w,m):return None,rows[w]
  return qualified_fit(None,Numerics(),Data(),list(range(len(rows))),threshold)
 def test_threshold_is_strict_and_per_equation(self):
  for rows in [[(.3,.9,.9)],[(.99,.01,.99)],[(.9,float('nan'),.9)]]:
   with self.assertRaises(InvalidCandidate):self.check(rows)
 def test_mean_over_windows_not_minimum_window(self):
  r=self.check([(.3,.9,.8),(.9,.8,.9)])
  np.testing.assert_allclose(r['r2_per_equation'],[.6,.85,.85])
 def test_relaxed_gate_accepts_between_point_three_and_point_five(self):
  self.check([(.31,.4,.49)])
 def test_coarse_gate_remains_strict_with_negative_threshold(self):
  self.check([(-.004,.2,.3)],threshold=-.005)
  for value in [-.005,-.006]:
   with self.assertRaises(InvalidCandidate):
    self.check([(value,.9,.9)],threshold=-.005)
 def test_invalid_windows_not_dropped(self):
  with self.assertRaises(InvalidCandidate):self.check([(.9,.9,.9),(.9,float('inf'),.9)])
 def test_rejected_do_not_count_as_success(self):
  class G:
   def sample(self,seed):return 'text'
  class N:
   def parse(self,text):return text
  def fail(_):raise InvalidCandidate('quality gate')
  with self.assertRaises(CandidateBudgetIncomplete) as cm:candidates(G(),N(),2,3,525,fail)
  self.assertEqual(cm.exception.stats['successful'],0)
  self.assertEqual(cm.exception.stats['rejections'],{'quality gate':3})
if __name__=='__main__':unittest.main()
