"""Stage1 compact-ID adapter, isolated from its unused GRE/author imports.

The merge trainer, byte alphabet and ID remapping are unchanged. This module
lets the Stage2 direct-LaTeX preparation run without loading the old generator,
GRE dictionary or torch. Existing vocabulary files remain byte-compatible.
"""
import json
import subprocess
from pathlib import Path
from math_tokenizer.hard_ast_2026 import HardASTBPE as Stage1HardASTBPE


class HardASTBPE(Stage1HardASTBPE):
    """Use the inherited reference encoder if Python development headers lack.

    The source-tree frontend remains identical. All saved merge rules and IDs
    are unchanged, and cross-platform sequence digests are checked separately.
    """
    def __init__(self,*args,**kwargs):
        try:super().__init__(*args,**kwargs)
        except subprocess.CalledProcessError as error:
            detail=(error.stderr or b'').decode(errors='replace')
            if 'Python.h' not in detail or 'No such file' not in detail:raise
            self.backend=None
    def encode(self,text):
        if self.backend is None:return self.encode_reference(text)
        return super().encode(text)

NUMERIC_BYTES=b'0123456789.+-eE'


def derive_alphabet(texts):
    return sorted(set(NUMERIC_BYTES).union(*(set(text.encode()) for text in texts)))


class CompactAlphabet:
    def __init__(self,method,alphabet,internal):
        self.method=method;self.alphabet=frozenset(alphabet);self.internal=internal
        kept=[i for i,payload in enumerate(internal.vocab) if len(payload)!=1 or payload[0] in self.alphabet]
        self.vocab=[internal.vocab[i] for i in kept]
        self.remap={old:new for new,old in enumerate(kept)};self.reverse=kept;self.capacity=len(self.vocab)
    def encode(self,text):
        missing=set(text.encode())-self.alphabet
        if missing:raise ValueError('Input outside compact alphabet: '+','.join(hex(x) for x in sorted(missing)))
        return [self.remap[i] for i in self.internal.encode(text)]
    def decode(self,ids):return b''.join(self.vocab[i] for i in ids).decode()
    def save(self,path):
        path=Path(path);backend=path.with_name(path.stem+'.backend.json');self.internal.save(backend)
        path.write_text(json.dumps(dict(format='compact-alphabet-ast-bpe-v1',method=self.method,alphabet=sorted(self.alphabet),
            content_ids=len(self.vocab),total_ids=len(self.vocab)+3,backend=backend.name,unsupported_input='explicit ValueError; no silent UNK'),indent=2)+'\n')
    @classmethod
    def load(cls,path):
        path=Path(path);config=json.loads(path.read_text())
        if config['format']!='compact-alphabet-ast-bpe-v1' or config['method']!='ast_bpe':raise ValueError('Unsupported tokenizer format')
        model=cls(config['method'],config['alphabet'],HardASTBPE.load(path.parent/config['backend']))
        if len(model.vocab)!=config['content_ids']:raise ValueError('Compact vocabulary size mismatch')
        return model


def train_compact(method,texts,total_ids,alphabet):
    if method!='ast_bpe':raise ValueError(method)
    observed=set().union(*(set(text.encode()) for text in texts))
    if not observed<=set(alphabet):raise ValueError('Training data outside alphabet')
    internal=HardASTBPE.train(texts,total_ids+256-len(alphabet)-3)
    result=CompactAlphabet(method,alphabet,internal)
    if len(result.vocab)+3!=total_ids:raise ValueError('Requested vocabulary could not be filled')
    return result
