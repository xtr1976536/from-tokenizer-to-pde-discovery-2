import unittest
import numpy as np
from scipy.linalg import expm
from stage2_main_v1.tests.test_implicit_backend import manufactured
from stage2_main_v1.implicit_backend import ImplicitBackend
from stage2_main_v1.scoring import reward,penalty
from stage2_main_v1.data import Window


class BackendScoringTests(unittest.TestCase):
    def test_fit_only_reward_does_not_read_future_or_reward_holdout(self):
        visible,mask,A,mode=manufactured();backend=ImplicitBackend();times=np.arange(20,40)*.01
        amplitudes=np.array([expm(A*s)@np.array([1.,.5]) for s in times])
        truth=np.stack([amplitudes[:,0,None,None]*mode,amplitudes[:,1,None,None]*mode,amplitudes.sum(axis=1)[:,None,None]*mode],-1)
        class Data:
            def training_mean(self):return np.zeros(3)
            roles={'reward_holdout':[Window('reward',0)]}
            access=[]
            def visible(self,w,role):
                self.access.append((role,'visible'));return visible,times,mask
            def target(self,w,role):
                raise AssertionError('Fit-only search reward must never read future target')
                self.access.append((role,'target'));return truth,mask
        data=Data();system=backend.parse(r'u_t=\Delta(u)+p\\v_t=\Delta(v)-u\\p=u+v')
        result=reward(system,backend,data,[Window('train',0)],np.ones(3),1.,.2)
        self.assertGreater(result['r_fit'],.999)
        self.assertAlmostEqual(result['reward'],penalty((3,3,3))*result['r_fit'])
        self.assertEqual(data.access,[('train_fit','visible')])
        self.assertNotIn('r_pred',result)
        self.assertLessEqual(result['reward'],penalty((3,3,3))+1e-8)
        self.assertFalse(any(role=='test' for role,_ in data.access))


if __name__=='__main__':unittest.main()
