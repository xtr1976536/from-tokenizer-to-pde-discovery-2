import unittest,tempfile,json
from pathlib import Path
import torch
from stage2_main_v1.generator import ASTBPEGenerator,cosine_lr
from stage2_main_v1.corpus_work.constrained_sampling import sample_batch

ROOT=Path(__file__).resolve().parents[2]
TOKENIZER=ROOT/'outputs/eqgpt-research/stage2-preparation-2026-11-16/811/upstream/ast-bpe-64.json'
VALID=r'u_t=\Delta(u)+p\\v_t=\Delta(v)+u\\p=u+v'


class GeneratorTests(unittest.TestCase):
    def test_short_cosine_does_not_restart_after_minimum(self):
        self.assertAlmostEqual(cosine_lr(0,2e-4,1e-6,20),2e-4)
        self.assertAlmostEqual(cosine_lr(20,2e-4,1e-6,20),1e-6)
        self.assertEqual(cosine_lr(60,2e-4,1e-6,20),1e-6)
    def test_real_training_sft_and_checkpoint_restore(self):
        torch.set_num_threads(2)
        g=ASTBPEGenerator(TOKENIZER,smoke=True,positions=256,max_tokens=80)
        train=[VALID,r'u_t=\Delta(u)+v\\v_t=\Delta(v)+p\\p=u+v']
        val=[r'u_t=\Delta(u)-p\\v_t=\Delta(v)+u\\p=u+v']
        with tempfile.TemporaryDirectory() as tmp:
            state=g.pretrain(train,val,Path(tmp)/'pretrain',dict(maximum_epochs=2,batch_size=2,token_budget=1024))
            self.assertEqual(len(state['history']),2);self.assertGreater(g.steps,0)
            before={k:v.clone() for k,v in g.model.state_dict().items()}
            sft=g.sft([VALID],dict(epochs=1,learning_rate=1e-5,minimum_learning_rate=1e-7,early_stopping=False,batch_size=1))
            self.assertFalse(sft['early_stopping'])
            self.assertTrue(any(not torch.equal(v,before[k]) for k,v in g.model.state_dict().items()))
            path=Path(tmp)/'online.pt';g.save(path)
            restored=ASTBPEGenerator(TOKENIZER,smoke=True,positions=256,max_tokens=80);restored.load(path)
            for k,v in g.model.state_dict().items():self.assertTrue(torch.equal(v,restored.model.state_dict()[k]))
            self.assertEqual(restored.steps,g.steps)
    def test_merged_or_fragmented_tokens_obey_three_equation_gate(self):
        g=ASTBPEGenerator(TOKENIZER,smoke=True,positions=256,max_tokens=200,random_fraction=0)
        ids=g.adapter.encode(VALID)[1:]
        class Forced(torch.nn.Module):
            def __init__(self):
                super().__init__();self.parameter=torch.nn.Parameter(torch.zeros(()));self.stage2_config={'positions':256}
            def forward(self,prefix):
                logits=torch.full((prefix.shape[0],prefix.shape[1],g.adapter.vocab_size),-1000.)
                logits[:,-1,ids[prefix.shape[1]-1]]=1000.
                return logits,None
        result=sample_batch(Forced(),g.adapter,525,batch=1,max_tokens=200,random_fraction=0)
        self.assertEqual(result,[VALID])
    def test_old_checkpoint_cannot_restore_random_mixture(self):
        g=ASTBPEGenerator(TOKENIZER,smoke=True,positions=256,random_fraction=.2)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'saved.pt';g.save(path)
            restored=ASTBPEGenerator(TOKENIZER,smoke=True,positions=256,random_fraction=0.)
            restored.load(path)
            self.assertEqual(restored.random_fraction,0.)
    def test_interrupted_training_resume_matches_uninterrupted(self):
        torch.set_num_threads(2)
        train=[VALID,r'u_t=\Delta(u)+v\\v_t=\Delta(v)+p\\p=u+v']
        val=[r'u_t=\Delta(u)-p\\v_t=\Delta(v)+u\\p=u+v']
        cfg=dict(maximum_epochs=2,batch_size=2,token_budget=1024)
        with tempfile.TemporaryDirectory() as tmp:
            full=ASTBPEGenerator(TOKENIZER,smoke=True,positions=256)
            full_state=full.pretrain(train,val,Path(tmp)/'full',cfg)
            partial=ASTBPEGenerator(TOKENIZER,smoke=True,positions=256)
            actual_epoch=partial._epoch
            def interrupted(texts,settings,training,epoch):
                if training and epoch==1:raise RuntimeError('simulated interruption')
                return actual_epoch(texts,settings,training,epoch)
            partial._epoch=interrupted
            with self.assertRaisesRegex(RuntimeError,'simulated interruption'):partial.pretrain(train,val,Path(tmp)/'partial',cfg)
            resumed=ASTBPEGenerator(TOKENIZER,smoke=True,positions=256)
            resumed_state=resumed.pretrain(train,val,Path(tmp)/'partial',cfg,resume=True)
            self.assertEqual(full_state['history'],resumed_state['history'])
            for k,v in full.model.state_dict().items():self.assertTrue(torch.equal(v,resumed.model.state_dict()[k]))


if __name__=='__main__':unittest.main()
