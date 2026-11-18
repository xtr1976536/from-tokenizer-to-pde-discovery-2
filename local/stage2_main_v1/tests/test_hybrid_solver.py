import unittest
import numpy as np
from stage2_main_v1.implicit_backend import ImplicitBackend
from stage2_main_v1.tests.test_implicit_backend import manufactured
from stage2_main_v1.contracts import InvalidCandidate


class HybridSolverTests(unittest.TestCase):
    def test_finite_unconverged_steps_are_accepted_but_flagged(self):
        v,m,_,_=manufactured();b=ImplicitBackend(max_nfev=1,newton_maxiter=0,linear_fast_path=False)
        s=b.parse(r'u_t=\Delta(u)+p+u*v\\v_t=\Delta(v)-u\\p=u+v');coef,_=b.fit(s,v,m)
        for i,term in enumerate(s.rows[0]):
            if set(term.arguments)=={('u',''),('v','')}:coef['rows'][0][i]=1.
        pred=b.forecast(s,coef,v,np.arange(20,23)*.01,m)
        self.assertTrue(np.isfinite(pred).all());self.assertEqual(len(pred),3)
        self.assertFalse(b.last_diagnostics['all_steps_meet_tolerance'])
        self.assertTrue(b.last_diagnostics['unconverged_steps_accepted'])
        self.assertNotEqual(b.last_diagnostics['steps'][0]['normalized_residual'],0.)

    def test_approximate_rollout_keeps_finite_unconverged_steps(self):
        v,m,_,_=manufactured();b=ImplicitBackend(max_nfev=1,newton_maxiter=0,linear_fast_path=False,
            diagnostic_approximate_rollout=True)
        s=b.parse(r'u_t=\Delta(u)+p+u*v\\v_t=\Delta(v)-u\\p=u+v');coef,_=b.fit(s,v,m)
        for i,term in enumerate(s.rows[0]):
            if set(term.arguments)=={('u',''),('v','')}:coef['rows'][0][i]=1.
        pred=b.forecast(s,coef,v,np.arange(20,23)*.01,m)
        self.assertTrue(np.isfinite(pred).all());self.assertEqual(len(pred),3)
        self.assertFalse(b.last_diagnostics['all_steps_meet_tolerance'])
        self.assertTrue(b.last_diagnostics['approximate_diagnostic'])
    def test_nonzero_nonlinearity_matches_trf(self):
        text=r'u_t=\Delta(u)+p+u*v\\v_t=\Delta(v)-u\\p=u+v'
        v,m,_,_=manufactured();hybrid=ImplicitBackend(linear_fast_path=False)
        reference=ImplicitBackend(nonlinear_solver='trf',linear_fast_path=False)
        s=hybrid.parse(text);coef,_=hybrid.fit(s,v,m)
        for i,term in enumerate(s.rows[0]):
            if set(term.arguments)=={('u',''),('v','')}:coef['rows'][0][i]=.2
        times=np.arange(20,40)*.01
        a=hybrid.forecast(s,coef,v,times,m);b=reference.forecast(s,coef,v,times,m)
        np.testing.assert_allclose(a,b,rtol=1e-6,atol=1e-8)
        self.assertTrue(any(step['trace'][0]['method']=='damped_newton' for step in hybrid.last_diagnostics['steps']))
        self.assertTrue(all(step['normalized_residual']<=1e-4 for step in hybrid.last_diagnostics['steps']))

    def test_failure_retains_step_and_trace(self):
        v,m,_,_=manufactured();b=ImplicitBackend(max_nfev=1,newton_maxiter=0,linear_fast_path=False,
            accept_unconverged_steps=False)
        s=b.parse(r'u_t=\Delta(u)+p+u*v\\v_t=\Delta(v)-u\\p=u+v');coef,_=b.fit(s,v,m)
        for i,term in enumerate(s.rows[0]):
            if set(term.arguments)=={('u',''),('v','')}:coef['rows'][0][i]=1.
        with self.assertRaises(InvalidCandidate):b.forecast(s,coef,v,np.arange(20,40)*.01,m)
        self.assertEqual(b.last_diagnostics['failed_step'],1)
        self.assertGreater(len(b.last_diagnostics['trace']),0)
        self.assertFalse(b.last_diagnostics['future_fields_read'])

if __name__=='__main__':unittest.main()
