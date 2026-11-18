import unittest
import numpy as np
from stage2_main_v1.implicit_backend import ImplicitBackend,CompiledTerm,structural_anchor
from stage2_main_v1.contracts import InvalidCandidate
from stage2_main_v1.tests.test_implicit_backend import manufactured


class AnchorPolicyTests(unittest.TestCase):
    def test_time_priority_is_structural(self):
        backend=ImplicitBackend()
        system=backend.parse(r'u_t=u_{tt}+v_t+u_{xx}\\v_t=v_{yy}+p\\p=u+v')
        self.assertEqual(system.rows[0][system.anchor_indices[0]].temporal_priority,(1,0))
        self.assertEqual(system.rows[1][system.anchor_indices[1]].temporal_priority,(1,1))
        self.assertIsNone(system.rows[2][system.anchor_indices[2]].temporal_priority)

    def test_products_and_mixed_derivatives_are_not_pure_time(self):
        backend=ImplicitBackend()
        system=backend.parse(r'u*u_t=u_{xt}+p\\v_t=v_{yy}+u\\p=u+v')
        self.assertTrue(all(t.temporal_priority is None for t in system.rows[0]))

    def test_anchor_does_not_change_with_window_values(self):
        backend=ImplicitBackend()
        system=backend.parse(r'u_t=\Delta(u)+p\\v_t=\Delta(v)-u\\p=u+v')
        visible,mask,_,_=manufactured()
        one,_=backend.fit(system,visible,mask)
        scaled={k:(value*2 if k in ('u','v','p') else value.copy()) for k,value in visible.items()}
        two,_=backend.fit(system,scaled,mask)
        self.assertEqual(one['anchor_indices'],two['anchor_indices'])
        self.assertEqual(tuple(one['anchor_indices']),system.anchor_indices)
        # Other basis columns still vary; a static u makes the fixed u_t invalid.
        visible['u']=np.broadcast_to(visible['u'][0],visible['u'].shape).copy()
        with self.assertRaises(InvalidCandidate):backend.fit(system,visible,mask)
        self.assertEqual(tuple(one['anchor_indices']),system.anchor_indices)

    def test_canonical_fallback_skips_structural_constants(self):
        constant=CompiledTerm((),lambda:1.)
        field=CompiledTerm((('p',''),),lambda p:p)
        self.assertEqual(structural_anchor((constant,field)),1)
        with self.assertRaises(InvalidCandidate):structural_anchor((constant,))


if __name__=='__main__':unittest.main()
