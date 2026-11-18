import copy
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
from stage2_main_v1.data import Window, ROLES, assert_isolation, valid_region
from stage2_main_v1.contracts import check_capabilities, InvalidCandidate
from stage2_main_v1.runner import window_batches, candidates, CandidateBudgetIncomplete, run, evaluate_frozen
from stage2_main_v1.scoring import penalty


class FakeData:
    def __init__(self, path):
        self.path=path;self.access=[];self.test_unlocked=False
        self.roles={r:[Window(r,0)] for r in ROLES}
    def training_scale(self):return np.ones(3)
    def training_mean(self):return np.zeros(3)
    def visible(self,w,role):
        if role=='test' and not self.test_unlocked:raise ValueError('locked')
        self.access.append((role,'visible'))
        # Deliberately no target in fitting input.
        return {'u':np.zeros((20,3,3))},np.arange(20,40),np.ones((3,3),bool)
    def target(self,w,role):
        if role=='test' and not self.test_unlocked:raise ValueError('locked')
        self.access.append((role,'target'))
        return np.ones((20,3,3,3)),np.ones((3,3),bool)


class FakeGenerator:
    fields=('u','v','p');equation_count=3;spatial_dimensions=2
    def __init__(self):self.updates=0
    def sample(self,seed):return f'candidate{seed}'
    def sft(self,texts,settings):
        self.updates+=1
        return {'epochs':settings['epochs'],'early_stopping':False,'settings':settings}
    def save(self,path):Path(path).write_text(str(self.updates))
    def load(self,path):self.updates=int(Path(path).read_text())


class FakeNumerics:
    fields=('u','v','p');equation_count=3;spatial_dimensions=2
    term_count_convention='canonical_lhs_plus_rhs_before_stencil_expansion'
    def parse(self,text):return text
    def structure_key(self,s):return s
    def term_counts(self,s):return (2,2,2)
    def fit(self,s,visible,mask):
        assert 'target' not in visible
        return [1,1,1],(.8,.7,.9)
    def forecast(self,s,coef,visible,times,mask):return np.ones((20,3,3,3))*.9


class ProtocolTests(unittest.TestCase):
    def test_full_window_gap_and_duplicates(self):
        roles={r:[Window(r,0)] for r in ROLES};assert_isolation(roles)
        roles['reward_holdout']=[Window('train_fit',39)]
        with self.assertRaises(ValueError):assert_isolation(roles)
        roles['reward_holdout']=[Window('train_fit',79)]
        with self.assertRaises(ValueError):assert_isolation(roles)
        roles['reward_holdout']=[Window('train_fit',80)];assert_isolation(roles)
    def test_mask(self):
        solid=np.zeros((7,7),bool);solid[3,3]=True
        mask=valid_region(solid)
        self.assertEqual(mask.sum(),16)
        self.assertFalse(mask[2:5,2:5].any())
    def test_complete_epoch(self):
        rows=[Window(str(i%3),i*80) for i in range(70)]
        batches=window_batches(rows,32,525)
        self.assertEqual(list(map(len,batches)),[32,32,6])
        self.assertEqual(set(sum(batches,[])),set(rows))
        self.assertEqual(batches,window_batches(rows,32,525))
    def test_old_generator_rejected(self):
        g=FakeGenerator();g.fields=('u','v');g.equation_count=2
        c=json.loads(Path('stage2_main_v1/config.json').read_text())
        with self.assertRaises(ValueError):check_capabilities(g,FakeNumerics(),c)
    def test_failed_candidate_budget_does_not_hang(self):
        class Invalid(FakeGenerator):
            def sample(self,seed):return None
        with self.assertRaises(CandidateBudgetIncomplete) as cm:
            candidates(Invalid(),FakeNumerics(),4,10,0,lambda s:{'reward':1})
        self.assertEqual(cm.exception.stats['attempts'],10)
    def test_system_penalty(self):
        self.assertAlmostEqual(penalty((2,2,2)),1-.2*np.log10(6))
    def test_validation_budget_failure_is_recorded(self):
        class NoPostSFTSamples(FakeGenerator):
            def sample(self,seed):return None if self.updates else 'train_candidate'
        c=json.loads(Path('stage2_main_v1/config.json').read_text())
        c['readiness']={k:True for k in c['readiness']}
        c.update(maximum_outer_epochs=1,successful_candidates_per_batch=1,
                 selection_candidates=1,top_k=1,maximum_sampling_attempts=2)
        with tempfile.TemporaryDirectory() as tmp:
            manifest=Path(tmp)/'manifest.json';manifest.write_text('{}')
            out=Path(tmp)/'out'
            with self.assertRaises(CandidateBudgetIncomplete):
                run(c,FakeData(manifest),NoPostSFTSamples(),FakeNumerics(),out,1.)
            failure=json.loads((out/'failures/epoch1_selection.json').read_text())
            self.assertEqual(failure['attempts'],2)
            self.assertEqual(failure['successful'],0)
            self.assertFalse((out/'frozen_model.json').exists())
    def test_orchestration_and_frozen_test_barrier(self):
        c=json.loads(Path('stage2_main_v1/config.json').read_text())
        c['readiness']={k:True for k in c['readiness']};c['baseline']['checkpoint_selection_audited']=True
        c.update(maximum_outer_epochs=2,successful_candidates_per_batch=3,selection_candidates=2,top_k=2)
        with tempfile.TemporaryDirectory() as tmp:
            manifest=Path(tmp)/'manifest.json';manifest.write_text('{}')
            data=FakeData(manifest);generator=FakeGenerator();out=Path(tmp)/'out'
            state=run(c,data,generator,FakeNumerics(),out,1.)
            self.assertTrue(state['finished']);self.assertEqual(generator.updates,2)
            self.assertFalse(any(role=='test' for role,part in data.access))
            self.assertFalse(any(role=='train_fit' and part=='target' for role,part in data.access))
            self.assertEqual(sum(role=='validation_stop' and part=='target' for role,part in data.access),2)
            # Finished resume restores state without adding an SFT update.
            run(c,data,generator,FakeNumerics(),out,1.,resume=True)
            self.assertEqual(generator.updates,2)
            evaluate_frozen(c,data,FakeNumerics(),out)
            self.assertTrue((out/'test_metrics.json').exists())
            with self.assertRaises(ValueError):evaluate_frozen(c,data,FakeNumerics(),out)

if __name__=='__main__':unittest.main()
