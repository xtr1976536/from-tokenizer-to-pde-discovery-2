import unittest
import numpy as np
from scipy.linalg import expm
from stage2_main_v1.implicit_backend import ImplicitBackend
from stage2_main_v1.contracts import InvalidCandidate


def manufactured():
    x=np.linspace(0,np.pi,9);y=x.copy();t=np.arange(20)*.01
    mode=np.sin(y)[:,None]*np.sin(x)[None,:];A=np.array([[-1.,1.],[-1.,-2.]])
    uv=np.array([expm(A*s)@np.array([1.,.5]) for s in t])
    visible=dict(u=uv[:,0,None,None]*mode,v=uv[:,1,None,None]*mode,p=uv.sum(axis=1)[:,None,None]*mode,t=t,x=x,y=y)
    return visible,np.ones(mode.shape,bool),A,mode


class ImplicitBackendTests(unittest.TestCase):
    def test_masked_singular_values_do_not_reject_valid_domain(self):
        from stage2_main_v1.implicit_backend import CompiledTerm
        backend=ImplicitBackend();a=np.zeros((5,5));a[1:-1,1:-1]=2
        valid=np.zeros((5,5),bool);valid[1:-1,1:-1]=True
        term=CompiledTerm((('u',''),),lambda u:1/u)
        result=backend._evaluate(term,lambda *_:a,a.shape,valid)
        self.assertTrue(np.all(result[valid]==.5))
    def test_algebraic_third_equation_fit_and_forecast(self):
        visible,mask,A,mode=manufactured();backend=ImplicitBackend(max_seconds=30)
        system=backend.parse(r'u_t=\Delta(u)+p\\v_t=\Delta(v)-u\\p=u+v')
        coef,r2=backend.fit(system,visible,mask)
        self.assertGreater(min(r2),.999)
        future=np.arange(20,40)*.01;before={k:v.copy() for k,v in visible.items()}
        prediction=backend.forecast(system,coef,visible,future,mask)
        reference=np.array([expm(A*s)@np.array([1.,.5]) for s in future])
        truth=np.stack([reference[:,0,None,None]*mode,reference[:,1,None,None]*mode,reference.sum(axis=1)[:,None,None]*mode],-1)
        self.assertLess(np.max(np.abs(prediction-truth)),.01)
        self.assertLess(np.max(np.abs(prediction[...,2]-prediction[...,0]-prediction[...,1])),1e-4)
        for k in visible:self.assertTrue(np.array_equal(before[k],visible[k]))
        self.assertFalse(backend.last_diagnostics['future_fields_read'])
    def test_supported_scope_is_separate_from_task_generation(self):
        backend=ImplicitBackend()
        system=backend.parse(r'\Delta(u)=p\\\Delta(v)=u\\p=u+v')
        self.assertEqual(backend.term_counts(system),(2,2,3))
        with self.assertRaises(InvalidCandidate):backend.parse(r'u_t=u_{xxxxx}\\v_t=\Delta(v)\\p=u+v')
        with self.assertRaises(InvalidCandidate):backend.parse(r'u_t=\Delta(v)+p\\u_t=\Delta(v)+p\\p=u+v')
    def test_divergence_product_rule_and_term_count(self):
        backend=ImplicitBackend()
        system=backend.parse(r'u_t=\nabla\cdot(u\nabla(v))+p\\v_t=\Delta(v)+u\\p=u+v')
        self.assertEqual(backend.term_counts(system),(3,3,3))
    def test_fourth_order_polynomial_stencil(self):
        from stage2_main_v1.implicit_backend import spatial_derivative
        x=np.linspace(-1,1,17);z=x**4
        np.testing.assert_allclose(spatial_derivative(z,0,x,4),24,atol=1e-9)
        np.testing.assert_allclose(spatial_derivative(z,0,x,3),24*x,atol=1e-10)
    def test_two_cell_collar_includes_internal_solid_interface(self):
        from stage2_main_v1.implicit_backend import closed_active
        mask=np.ones((13,13),bool);mask[5:8,5:8]=False
        active=closed_active(mask,2)
        self.assertFalse(active[4:9,4:9].any())
        self.assertFalse(active[:2].any());self.assertFalse(active[:,:2].any())
        self.assertTrue(active[3,3])
    def test_fourth_order_forecast_uses_two_cell_frozen_collar(self):
        from scipy.linalg import expm
        x=np.linspace(0,np.pi,9);y=x.copy();t=np.arange(20)*.001
        mode=np.sin(y)[:,None]*np.sin(x)[None,:]
        first=np.exp(-4*t)[:,None,None]*mode
        second=np.exp(-25*t)[:,None,None]*np.sin(y)[None,:,None]*np.sin(2*x)[None,None,:]
        visible=dict(u=first,v=second,p=first+second)
        visible.update(t=t,x=x,y=y)
        backend=ImplicitBackend(max_seconds=30)
        system=backend.parse(r'u_t=-\Delta^2(u)\\v_t=-\Delta^2(v)\\p=u+v')
        coef,r2=backend.fit(system,visible,np.ones((9,9),bool))
        self.assertGreater(min(r2),.999)
        pred=backend.forecast(system,coef,visible,np.arange(20,23)*.001,np.ones((9,9),bool))
        np.testing.assert_allclose(pred[:,0:2,:,0],np.broadcast_to(visible['u'][-1,:2],(3,2,9)))
        self.assertEqual(backend.last_diagnostics['boundary_collar_cells'],2)
    def test_unresolvable_regression_and_budget_reject(self):
        visible,mask,_,_=manufactured();backend=ImplicitBackend(max_calls=1)
        system=backend.parse(r'u_t=\Delta(u)+p\\v_t=\Delta(v)-u\\p=u+v')
        coef,_=backend.fit(system,visible,mask)
        with self.assertRaisesRegex(InvalidCandidate,'residual-call budget exceeded'):
            backend.forecast(system,coef,visible,np.arange(20,40)*.01,mask)
        timed=ImplicitBackend(max_seconds=0)
        with self.assertRaisesRegex(InvalidCandidate,'time budget exceeded'):
            timed.forecast(system,coef,visible,np.arange(20,40)*.01,mask)
    def test_algebraic_constant_does_not_force_undefined_r2(self):
        visible,mask,_,_=manufactured();visible['p']=visible['p']+1
        backend=ImplicitBackend()
        system=backend.parse(r'u_t=\Delta(u)+p-1\\v_t=\Delta(v)-u\\p=u+v+1')
        coef,r2=backend.fit(system,visible,mask)
        self.assertGreater(min(r2),.999)
        self.assertGreater(coef['anchor_indices'][2],0)


if __name__=='__main__':unittest.main()
