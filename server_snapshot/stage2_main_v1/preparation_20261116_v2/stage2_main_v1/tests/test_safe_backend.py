import json,time,unittest,sys
from pathlib import Path
import numpy as np
from stage2_main_v1.contracts import InvalidCandidate
from stage2_main_v1.safe_backend import SafeBackend
from stage2_main_v1.implicit_backend import ImplicitBackend
from stage2_main_v1.tests.test_implicit_backend import manufactured

VALID=r'u_t=\Delta(u)+p\\v_t=\Delta(v)-u\\p=u+v'


class SafeBackendTests(unittest.TestCase):
    def test_worker_roundtrip_and_exit(self):
        b=SafeBackend()
        events=[];b.on_progress=events.append
        try:
            s=b.parse(VALID);visible,mask,_,_=manufactured()
            coef,r2=b.fit(s,visible,mask)
            pred=b.forecast(s,coef,visible,np.arange(20,40)*.01,mask)
            self.assertEqual(pred.shape,(20,9,9,3));self.assertGreater(min(r2),.999)
            if sys.platform.startswith('linux'):
                self.assertEqual(b.last_diagnostics['isolation']['kernel_address_space_limit_mb'],4096)
            process=b.process
        finally:b.close()
        self.assertIsNotNone(process.poll())
        self.assertEqual(events[-1]['phase'],'complete')
        self.assertEqual(events[-1]['action'],'forecast')

    def test_parent_deadline_and_worker_recovery(self):
        b=SafeBackend(compile_seconds=.000001)
        try:
            with self.assertRaisesRegex(InvalidCandidate,'deadline'):b.parse(VALID)
            self.assertIsNone(b.process)
            b.limits['compile_seconds']=15
            b.parse(VALID);b.process.kill();b.process.wait()
            self.assertEqual(b.parse(VALID).term_counts,(3,3,3))
        finally:b.close()

    def test_both_incident_formulas_are_bounded_and_next_candidate_works(self):
        b=SafeBackend(compile_seconds=3)
        try:
            for name in ['stalled-806.json','stalled-1615.json']:
                text=json.loads((Path(__file__).parent/'fixtures'/name).read_text())['text']
                start=time.monotonic()
                try:b.parse(text)
                except InvalidCandidate:pass
                self.assertLess(time.monotonic()-start,5)
            b.limits['compile_seconds']=15
            self.assertEqual(b.parse(VALID).term_counts,(3,3,3))
        finally:b.close()

    def test_analytic_and_finite_difference_nonlinear_forecasts_agree(self):
        text=r'u_t=\Delta(u)+p+u*v\\v_t=\Delta(v)-u\\p=u+v'
        analytic=ImplicitBackend(linear_fast_path=False)
        finite=ImplicitBackend(analytic_jacobian=False,linear_fast_path=False)
        visible,mask,_,_=manufactured();system=analytic.parse(text)
        coef,_=analytic.fit(system,visible,mask)
        for index,term in enumerate(system.rows[0]):
            if set(term.arguments)=={('u',''),('v','')}:coef['rows'][0][index]=.2
        times=np.arange(20,25)*.01
        one=analytic.forecast(system,coef,visible,times,mask)
        two=finite.forecast(system,coef,visible,times,mask)
        np.testing.assert_allclose(one,two,rtol=1e-6,atol=1e-8)
        self.assertLess(analytic.last_diagnostics['residual_calls'],finite.last_diagnostics['residual_calls'])

    def test_derivative_cache_bounded_and_same_result(self):
        b=ImplicitBackend(fit_cache_mb=1);visible,mask,_,_=manufactured()
        system=b.parse(VALID);before=b.fit(system,visible,mask)
        visible['_cache_key']=('fixture',0)
        for _ in range(2):
            after=b.fit(system,visible,mask)
            np.testing.assert_allclose(before[1],after[1],atol=1e-12)
        self.assertLessEqual(b._fit_cache_bytes,1024**2)

    def test_generation_gate_rejects_exponential_nested_laplacian_expansion(self):
        from stage2_main_v1.corpus_work.task_gate import bounded_tree
        tree=('v','u')
        for _ in range(4):tree=('lap',tree,8)
        with self.assertRaisesRegex(ValueError,'expansion resource limit'):bounded_tree(tree)


if __name__=='__main__':unittest.main()
