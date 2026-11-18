import unittest
from constrained_sampling import State,advance,can_end
class MaskTests(unittest.TestCase):
 def test_merged_tokens_and_macro_letters(self):
  text=r'\partial_t(u)=\Delta(v)+p\\\partial_t(v)=\Delta(p)+u\\\partial_t(p)=\Delta(u)+v'
  for n in [1,2,3,7,19,len(text)]:
   s=State()
   for i in range(0,len(text),n):s=advance(s,text[i:i+n].encode());self.assertIsNotNone(s)
   self.assertTrue(can_end(s,text))
 def test_variables_axes_and_fourth_equation_masked(self):
  for text in [b'w',b'z',b'a',b'\\unknown',b'u=v\\\\v=p\\\\p=u\\\\']:
   self.assertIsNone(advance(State(),text))
 def test_incomplete_or_wrong_scope_cannot_end(self):
  for text in ['u=v',r'u=v\\v=p\\p=u',r'\partial_t(u)=\Delta(v)+p\\v=u\\p=']:
   s=advance(State(),text.encode());self.assertFalse(s is not None and can_end(s,text))
 def test_zero_rhs_serialization(self):
  for text in [r'u_t+\Delta(u)+p=0\\v_t+\Delta(v)+u=0\\p+u+v=0']:
   state=State(residual_zero_rhs=True)
   state=advance(state,text.encode())
   self.assertIsNotNone(state)
   self.assertTrue(can_end(state,text))
  for text in ['u=01','u=0+v','u=v','u=0(v)',r'u=0\cdot',r'u=0\partial']:
   self.assertIsNone(advance(State(residual_zero_rhs=True),text.encode()))
if __name__=='__main__':unittest.main()
