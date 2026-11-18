import unittest
import numpy as np
from stage2_main_v1.scoring import prediction_score

class StandardizedRewardTests(unittest.TestCase):
 def compute(self,y,p,mean,scale,mask=None):
  class Data:
   roles={'reward_holdout':[0]}
   def training_mean(self):return mean
   def visible(self,*_):return {},np.arange(len(y)),mask
   def target(self,*_):return y,mask
  class Numerics:
   def fit(self,*_):return {},(0,0,0)
   def forecast(self,*_):return p
  if mask is None:mask=np.ones(y.shape[1:3],bool)
  return prediction_score(None,Numerics(),Data(),'reward_holdout',scale)
 def test_invariant_to_independent_channel_units_and_offsets(self):
  rng=np.random.default_rng(52);y=rng.normal(size=(4,3,3,3));p=y+rng.normal(size=y.shape)*.2
  mean=np.array([.1,.2,.3]);scale=np.array([.2,1.,3.]);a=self.compute(y,p,mean,scale)
  units=np.array([1.,10.,1000.]);offset=np.array([100.,-30.,8.])
  b=self.compute(y*units+offset,p*units+offset,mean*units+offset,scale*units)
  self.assertAlmostEqual(a['prediction_score'],b['prediction_score'],12)
  self.assertAlmostEqual(a['normalized_joint_rmse'],b['normalized_joint_rmse'],12)
  self.assertNotAlmostEqual(a['raw_prediction_score_diagnostic'],b['raw_prediction_score_diagnostic'],3)
 def test_equal_standardized_error_in_any_channel_gets_equal_score(self):
  rng=np.random.default_rng(2);y=rng.normal(size=(4,3,3,3))*np.array([1.,2.,100.]);scale=np.array([1.,2.,100.]);results=[]
  for channel in range(3):
   p=y.copy();p[...,channel]+=.2*scale[channel]
   results.append(self.compute(y,p,np.zeros(3),scale)['prediction_score'])
  np.testing.assert_allclose(results,results[0])
 def test_future_target_does_not_change_frozen_statistics(self):
  y=np.ones((2,3,3,3));mean=np.zeros(3);scale=np.ones(3);m=mean.copy();s=scale.copy()
  self.compute(y*10,y,mean,scale)
  np.testing.assert_array_equal(mean,m);np.testing.assert_array_equal(scale,s)
 def test_masked_points_do_not_affect_score(self):
  y=np.ones((2,3,3,3));p=y.copy();p[:,0]=999;mask=np.ones((3,3),bool);mask[0]=False
  self.assertEqual(self.compute(y,p,np.zeros(3),np.ones(3),mask)['prediction_score'],1.)
if __name__=='__main__':unittest.main()
