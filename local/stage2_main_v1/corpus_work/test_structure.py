import unittest
from structure_latex import normalize_system,structure_key
class StructureTests(unittest.TestCase):
 def test_coefficients_removed_but_structure_retained(self):
  r=normalize_system([r'\partial_t(u)=a\cdot\Delta(u)-b\cdot u^{3}+2\cdot u'],['u'])
  self.assertIn('u^{3}',r['text']);self.assertNotIn('a',r['text'].replace('partial','').replace('Delta',''));self.assertNotIn('b',r['text'])
 def test_reaction_expanded_before_coefficient_removal(self):
  r=normalize_system([r'\partial_t(u)=a\cdot u\cdot(1-u-b\cdot v)',r'\partial_t(v)=\Delta(v)'],['u','v'])
  self.assertIn('u\\cdot v',r['text'])
  self.assertIn('u^{2}',r['text'])
 def test_inner_parameter_not_destroyed(self):
  with self.assertRaises(ValueError):normalize_system([r'\partial_t(u)=\frac{u}{1+a\cdot u}'],['u'])
 def test_global_simultaneous_renaming(self):
  r=normalize_system([r'\partial_t(u)=w+p',r'\partial_t(v)=u',r'\partial_t(w)=v',r'\partial_t(p)=w'],['u','v','w','p'])
  self.assertEqual(r['field_map'],{'u':'u','v':'v','w':'p','p':'w'})
 def test_literal_cancel_and_derivative_order(self):
  r=normalize_system([r'\partial_{tt}(u)=\Delta(u)+1-1'],['u'])
  self.assertNotIn('+1',r['text']);self.assertIn('partial_{tt}',r['text'])
 def test_divided_outer_coefficient(self):
  a=normalize_system([r'\partial_t(u)=\frac{b\cdot u}{a}'],['u'])
  b=normalize_system([r'\partial_t(u)=u'],['u'])
  self.assertEqual(a['text'],b['text'])
 def test_rational_outer_coefficient_only(self):
  a=normalize_system([r'\partial_t(u)=\frac{a\cdot u}{1+u}'],['u'])
  self.assertIn('frac',a['text']);self.assertNotIn('a',a['text'].replace('partial','').replace('frac',''))
 def test_variable_coefficient_is_not_constant(self):
  with self.assertRaises(ValueError):normalize_system([r'\partial_t(u)=\beta(x)\cdot u'],['u'])
 def test_repeated_product_and_literal_power_share_key(self):
  a=normalize_system([r'\partial_t(u)=u\cdot u'],['u'])
  b=normalize_system([r'\partial_t(u)=u^{2}'],['u'])
  self.assertEqual(structure_key(a['residual_support_ast'],a['fields']),structure_key(b['residual_support_ast'],b['fields']))
 def test_power_times_base_is_not_a_new_structure(self):
  a=normalize_system([r'u_t=u^2u'],['u'])
  b=normalize_system([r'u_t=u^3'],['u'])
  self.assertEqual(a['text'],b['text'])
 def test_source_z_is_a_field_not_third_coordinate(self):
  a=normalize_system([r'u_t=\Delta(u)+z',r'z_t=\Delta(z)+u'],['u','z'])
  self.assertEqual(a['field_map'],{'u':'u','z':'v'})
 def test_unmapped_third_coordinate_derivative_rejected(self):
  with self.assertRaises(ValueError):normalize_system([r'u_t=\partial_z(u)'],['u'])
 def test_derivative_squared_is_not_second_derivative(self):
  a=normalize_system([r'u_t=u_x^2+u_y^2'],['u'])
  b=normalize_system([r'u_t=(u_x)^2+(u_y)^2'],['u'])
  c=normalize_system([r'u_t=u_{xx}+u_{yy}'],['u'])
  self.assertEqual(a['text'],b['text'])
  self.assertNotEqual(a['text'],c['text'])
 def test_partial_operator_second_order_notation(self):
  a=normalize_system([r'u_t=\partial_x^2(u)'],['u'])
  b=normalize_system([r'u_t=\partial_{xx}(u)'],['u'])
  self.assertEqual(a['text'],b['text'])
 def test_parameter_subscript_does_not_swallow_following_field(self):
  a=normalize_system([r'u_t=\mu_1u(1-u-a_1v)',r'v_t=\Delta(v)'],['u','v'])
  self.assertIn(r'u\cdot v',a['text'])
  self.assertIn('u^{2}',a['text'])
 def test_parameter_subscript_does_not_swallow_product(self):
  a=normalize_system([r'u_t=g_Rpu',r'v_t=\Delta(v)',r'p_t=u'],['u','v','p'])
  self.assertIn(r'p\cdot u',a['text'])
 def test_square_root_uses_a_latex_argument_group(self):
  a=normalize_system([r'u_{xx}+u_{yy}=\sqrt(u)'],['u'])
  self.assertIn(r'\sqrt{u}',a['text'])
  self.assertEqual(normalize_system(a['equations'],['u'])['text'],a['text'])
 def test_zero_power_inside_spatial_flux_is_idempotent(self):
  a=normalize_system([r'\partial_x(x^{-1}u_x)+\partial_y(y^0u_y)=u^3'],['u'])
  self.assertEqual(normalize_system(a['equations'],['u'])['text'],a['text'])
 def test_shifted_polynomial_expands_without_setting_parameter(self):
  a=normalize_system([r'u_t=\partial_x((u+\alpha)^2u_x)+u_{yy}'],['u'])
  b=normalize_system([r'u_t=\partial_x((u^2+2\alpha u+\alpha^2)u_x)+u_{yy}'],['u'])
  self.assertEqual(a['text'],b['text'])
if __name__=='__main__':unittest.main()
