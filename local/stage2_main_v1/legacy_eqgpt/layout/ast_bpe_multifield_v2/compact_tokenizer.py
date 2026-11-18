"""Same Hard AST-BPE merges with unused byte IDs removed (stage-one approach).
Declared alphabet must come from training data + explicit task syntax only.
"""
import json,sys
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[1]/'分词器-pde发现/src'
sys.path.insert(0,str(SOURCE))
from math_tokenizer.hard_ast_2026 import HardASTBPE
class CompactASTBPE:
 def __init__(self,internal,alphabet):
  self.internal=internal;self.alphabet=frozenset(alphabet)
  self.reverse=[i for i,b in enumerate(internal.vocab) if len(b)!=1 or b[0] in self.alphabet]
  self.remap={old:new for new,old in enumerate(self.reverse)};self.vocab=[internal.vocab[i] for i in self.reverse]
 def encode(self,text):
  missing=set(text.encode())-self.alphabet
  if missing:raise ValueError('Outside declared compact alphabet: '+str(sorted(missing)))
  return [self.remap[i] for i in self.internal.encode(text)]
 def decode(self,ids):return b''.join(self.vocab[i] for i in ids).decode()
 @classmethod
 def train(cls,texts,total_ids,task_syntax=''):
  if not texts:raise ValueError('Training texts must not be empty')
  alphabet=sorted(set(task_syntax.encode())|set().union(*(set(s.encode()) for s in texts)))
  if total_ids< len(alphabet)+3:raise ValueError('Requested vocabulary smaller than used bytes plus controls')
  internal=HardASTBPE.train(texts,total_ids-3+256-len(alphabet));m=cls(internal,alphabet)
  assert len(m.vocab)+3<=total_ids
  for text in texts:
   assert m.decode(m.encode(text))==text
   assert internal.encode(text)==internal.encode_reference(text)
  return m
 def save(self,path):
  path=Path(path);backend=path.with_suffix('.backend.json');self.internal.save(backend)
  path.write_text(json.dumps(dict(format='stage2-compact-hard-ast-bpe',alphabet=sorted(self.alphabet),backend=backend.name,total_ids=len(self.vocab)+3),indent=2))
 @classmethod
 def load(cls,path):
  path=Path(path);r=json.loads(path.read_text());assert r['format']=='stage2-compact-hard-ast-bpe';m=cls(HardASTBPE.load(path.parent/r['backend']),r['alphabet']);assert len(m.vocab)+3==r['total_ids'];return m
