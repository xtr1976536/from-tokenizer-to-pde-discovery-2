import unittest
from leakage_guard import reasons
from structure_latex import normalize_system
class LeakageTests(unittest.TestCase):
 def test_target_and_tracer_subsystem_quarantined(self):
  n=normalize_system([r'\partial_t(u)+u\cdot\partial_x(u)+v\cdot\partial_y(u)+\partial_x(p)-a\cdot\Delta(u)=0',r'\partial_t(v)+u\cdot\partial_x(v)+v\cdot\partial_y(v)+\partial_y(p)-a\cdot\Delta(v)=0',r'\partial_x(u)+\partial_y(v)=0'],['u','v','p'])
  self.assertTrue(reasons(n['residual_support_ast'],n['fields']))
 def test_different_fluid_closure_not_blanket_banned(self):
  n=normalize_system([r'\partial_t(u)+u\cdot\partial_x(u)+v\cdot\partial_y(u)+\partial_x(p)=0',r'\partial_t(v)+u\cdot\partial_x(v)+v\cdot\partial_y(v)+\partial_y(p)=0',r'\partial_t(p)+\partial_x(u\cdot p)+\partial_y(v\cdot p)=0'],['u','v','p'])
  self.assertFalse(reasons(n['residual_support_ast'],n['fields']))
 def test_single_streamfunction_target_quarantined(self):
  n=normalize_system([r'\Delta(u_t)+u_y\partial_x(\Delta(u))-u_x\partial_y(\Delta(u))=a\Delta^2(u)'],['u'])
  self.assertTrue(reasons(n['residual_support_ast'],n['fields']))
 def test_dispersive_fluid_model_not_blanket_banned(self):
  n=normalize_system([r'u_{xt}+\partial_x(u u_x)+u_{xxxx}+u_{yy}=0'],['u'])
  self.assertFalse(reasons(n['residual_support_ast'],n['fields']))
if __name__=='__main__':unittest.main()
