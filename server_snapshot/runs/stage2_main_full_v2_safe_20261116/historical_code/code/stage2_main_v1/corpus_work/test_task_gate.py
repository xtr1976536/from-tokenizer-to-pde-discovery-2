import unittest
from task_gate import validate
class GateTests(unittest.TestCase):
 def test_three_field_evolution(self):
  r=validate(r'\partial_t(u)=\Delta(u)+v\\\partial_t(v)=\Delta(v)+p\\\partial_t(p)=\Delta(p)+u')
  self.assertEqual(len(r['equations']),3)
 def test_constraint_allowed_without_p_time_anchor(self):
  validate(r'\partial_t(u)=\partial_x(p)+v\\\partial_t(v)=\partial_y(p)+u\\\partial_x(u)+\partial_y(v)=0')
 def test_wrong_scope_rejected(self):
  for s in [r'u=v\\v=p',r'\partial_t(u)=w\\v=\Delta(p)\\p=u',r'\partial_t(u)=\partial_x(u)\\\partial_t(v)=u\\\partial_t(p)=v',r'u=\partial_z(v)\\v=p\\p=\Delta(u)']:
   with self.assertRaises(ValueError):validate(s)
 def test_bare_vector_gradient_is_not_a_scalar_equation(self):
  with self.assertRaises(ValueError):validate(r'u_t=\nabla(v)+p\\v_t=\Delta(v)+u\\p=u+v')
 def test_coordinate_only_row_is_not_a_governing_equation(self):
  with self.assertRaises(ValueError):validate(r'u_t=\Delta(u)+p\\v_t=\Delta(v)+u\\x+y=0')
if __name__=='__main__':unittest.main()
