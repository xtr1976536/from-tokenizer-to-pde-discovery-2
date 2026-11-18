"""Fast preparation regressions, independent of the large downloaded data."""
import sys,tempfile,json,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from index_policy import seen_windows,QUOTAS
from stage2_main_v1.prepared_data import reconstruct_context
from stage2_main_v1.data import valid_region,assert_isolation,Window

class PreparationTests(unittest.TestCase):
 def test_seen_all_trajectories_and_strict_windows(self):
  ids=[f'{1781+i*94}.h5' for i in range(92)];lengths={sid:3990 for sid in ids}
  rows,blocks=seen_windows(lengths)
  self.assertEqual([len(v) for v in rows.values()],[5060,460,460,460,920])
  total=sum(map(len,rows.values()));self.assertEqual((len(rows['train_fit'])+len(rows['reward_holdout']))/total,.75)
  self.assertEqual((len(rows['validation_select'])+len(rows['validation_stop']))/total,.125)
  self.assertEqual(len(rows['test'])/total,.125)
  self.assertEqual((rows,blocks),seen_windows(dict(reversed(list(lengths.items())))))
  for role,ws in rows.items():self.assertEqual({w['trajectory'] for w in ws},set(ids))
  assert_isolation({r:[Window(w['trajectory'],w['start']) for w in v] for r,v in rows.items()})
  for sid in ids:
   used=set()
   for ws in rows.values():
    for w in ws:
     if w['trajectory']==sid:
      frames=set(range(w['start'],w['start']+40));self.assertFalse(used&frames);used|=frames
   self.assertEqual(len(used),3200)
 def test_overlap_and_gap_rejected(self):
  roles={r:[Window(r,0)] for r in ('train_fit','reward_holdout','validation_select','validation_stop','test')}
  roles['train_fit'].append(Window('train_fit',20))
  with self.assertRaises(ValueError):assert_isolation(roles)
  roles['train_fit'].pop();roles['test']=[Window('train_fit',79)]
  with self.assertRaises(ValueError):assert_isolation(roles)
 def test_halo_roundtrip_and_no_future(self):
  original=np.arange(40*64*128,dtype=np.float32).reshape(40,64,128)
  v={f:original[:20,1:-1,1:-1].copy() for f in ('u','v','p')}
  halo=np.concatenate([original[:20,0,:],original[:20,-1,:],original[:20,1:-1,0],original[:20,1:-1,-1]],1)
  v.update(halo={f:halo for f in ('u','v','p')},t=np.arange(20),context_x=np.zeros((64,128)),context_y=np.zeros((64,128)))
  reconstructed=reconstruct_context(v)
  self.assertTrue(np.array_equal(reconstructed['p'],original[:20]))
  self.assertEqual(reconstructed['u'].shape,(20,64,128))
 def test_mask_no_second_outer_crop(self):
  solid=np.zeros((64,128),bool);solid[30:34,30:34]=True
  full=valid_region(solid,1,1);cropped=full[1:-1,1:-1]
  self.assertEqual(cropped.shape,(62,126));self.assertTrue(cropped[0].all());self.assertTrue(cropped[-1].all())

if __name__=='__main__':unittest.main()
