"""Audited simulation manifest and lazy, visible-prefix-only window interface."""
from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import zipfile
import numpy as np

ROLES = ('train_fit', 'reward_holdout', 'validation_select', 'validation_stop', 'test')


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


@dataclass(frozen=True)
class Window:
    trajectory: str
    start: int


def assert_isolation(roles, gap=40):
    """Cross-role disjoint full [start,start+40) windows, plus temporal gap.
    Same trajectories may appear in every role; all full windows are disjoint.
    """
    if set(roles) != set(ROLES) or any(not roles[r] for r in ROLES):
        raise ValueError('All five nonempty data roles are required')
    by_trajectory = {}
    for role, rows in roles.items():
        if len(set(rows)) != len(rows):
            raise ValueError(f'Duplicate windows in {role}')
        for w in rows:
            if w.start < 0:
                raise ValueError('Negative window start')
            by_trajectory.setdefault(w.trajectory, []).append((w.start, w.start + 40, role))
    for trajectory, entries in by_trajectory.items():
        latest = {};previous_end=None
        for start, end, role in sorted(entries):
            if previous_end is not None and start < previous_end:
                raise ValueError(f"Overlapping full windows: {trajectory}")
            previous_end=end
            for other, stop in latest.items():
                if other != role and start < stop + gap:
                    raise ValueError(f'40-frame leakage/isolation gap: {trajectory}, {other}/{role}')
            latest[role] = max(end, latest.get(role, 0))


def valid_region(solid, outer=1, interface=1):
    """8-neighbor interface exclusion; caller supplies audited solid geometry."""
    solid = np.asarray(solid, dtype=bool)
    if solid.ndim != 2 or outer < 0 or interface < 0:
        raise ValueError('Invalid geometry')
    excluded = solid.copy()
    for _ in range(interface):
        padded = np.pad(excluded, 1, constant_values=False)
        excluded = np.logical_or.reduce([padded[i:i+solid.shape[0], j:j+solid.shape[1]]
                                         for i in range(3) for j in range(3)])
    valid = ~excluded
    if outer:
        valid[:outer] = False; valid[-outer:] = False
        valid[:, :outer] = False; valid[:, -outer:] = False
    if not valid.any():
        raise ValueError('Empty effective region')
    return valid


def npz_shape(path, key):
    # Inspect only the array header; do not expose future field values for audits.
    with zipfile.ZipFile(path) as archive, archive.open(key+'.npy') as stream:
        version = np.lib.format.read_magic(stream)
        reader = (np.lib.format.read_array_header_1_0 if version == (1,0)
                  else np.lib.format.read_array_header_2_0)
        shape, _, dtype = reader(stream)
        if dtype.hasobject: raise ValueError('Object arrays forbidden')
        return shape


class NPZSimulationData:
    """NPZ is an interchange contract, not an invented Arrow decoding layout.
    A future audited importer must export aligned t,x,y,u,v,p and solid_mask.
    Coordinates are static 1D vectors or matching 2D meshes; t is strictly increasing.
    Manifest paths are relative to the manifest directory. No implicit downloads.
    """
    def __init__(self, manifest_path, config):
        self.path = Path(manifest_path).resolve()
        self.meta = json.loads(self.path.read_text())
        m = self.meta
        if m['branch'] != 'numerical' or m['revision'] != config['dataset_revision']:
            raise ValueError('Wrong dataset branch/revision')
        for key in ('official_indices_audited', 'geometry_frozen', 'split_policy_frozen',
                    'source_alignment_verified', 'pressure_gauge_frozen'):
            if m.get(key) is not True:
                raise ValueError(f'Data audit incomplete: {key}')
        if m.get('isolation_gap_frames', -1) < 40:
            raise ValueError('Require at least 40-frame cross-role isolation gap')
        self.roles = {r: [Window(str(w['trajectory']), int(w['start'])) for w in m['roles'][r]] for r in ROLES}
        assert_isolation(self.roles, m['isolation_gap_frames'])
        self.trajectories = {}
        self.access = []; self.test_unlocked = False
        for name in sorted({w.trajectory for rows in self.roles.values() for w in rows}):
            entry = m['trajectories'][name]
            path = (self.path.parent / entry['path']).resolve()
            if sha256(path) != entry['sha256']:
                raise ValueError(f'Trajectory hash mismatch: {name}')
            with np.load(path, allow_pickle=False) as z:
                shape = npz_shape(path, 'u')
                if len(shape) != 3 or any(npz_shape(path,f) != shape for f in ('v','p')):
                    raise ValueError('Aligned [T,H,W] u/v/p required')
                if any(not np.isfinite(z[f]).all() for f in ('t','x','y')):
                    raise ValueError('Nonfinite data')
                if z['t'].shape != (shape[0],) or not np.all(np.diff(z['t']) > 0):
                    raise ValueError('Invalid time coordinates')
                if z['solid_mask'].shape != shape[1:]:
                    raise ValueError('Solid mask shape mismatch')
                x, y = z['x'], z['y']
                if not ((x.shape == (shape[2],) and y.shape == (shape[1],)) or
                        (x.shape == shape[1:] and y.shape == shape[1:])):
                    raise ValueError('Invalid x/y grid')
                mask = valid_region(z['solid_mask'], config['region']['outer_cells'], config['region']['solid_interface_cells'])
            self.trajectories[name] = (path, shape, mask)
        for rows in self.roles.values():
            for w in rows:
                if w.start + 40 > self.trajectories[w.trajectory][1][0]:
                    raise ValueError('Incomplete 40-frame window')

    def visible(self, w, role):
        if w not in self.roles[role] or (role == 'test' and not self.test_unlocked):
            raise ValueError('Unauthorized window access')
        path, _, mask = self.trajectories[w.trajectory]
        with np.load(path, allow_pickle=False) as z:
            visible = {f: z[f][w.start:w.start+20].copy() for f in ('u','v','p','t')}
            visible.update({f: z[f].copy() for f in ('x','y')})
            visible['_cache_key']=(str(self.path),w.trajectory,w.start)
            if any(not np.isfinite(visible[f][:,mask]).all() for f in ('u','v','p')):
                raise ValueError('Nonfinite visible field in effective region')
            times = z['t'][w.start+20:w.start+40].copy()
        self.access.append({'role': role, 'part': 'visible', 'trajectory': w.trajectory, 'start': w.start})
        return visible, times, mask

    def target(self, w, role):
        if w not in self.roles[role] or (role == 'test' and not self.test_unlocked):
            raise ValueError('Test targets locked or role mismatch')
        path, _, mask = self.trajectories[w.trajectory]
        with np.load(path, allow_pickle=False) as z:
            target = np.stack([z[f][w.start+20:w.start+40] for f in ('u','v','p')], -1)
        if not np.isfinite(target[:,mask,:]).all(): raise ValueError('Nonfinite target')
        self.access.append({'role': role, 'part': 'target', 'trajectory': w.trajectory, 'start': w.start})
        return target, mask

    def training_scale(self):
        """Train-fit visible frames only; count each stored frame once."""
        return self.training_statistics()[1]

    def training_mean(self):
        return self.training_statistics()[0]

    def training_statistics(self):
        if hasattr(self,'_training_statistics'):return self._training_statistics
        total = np.zeros(3); squares = np.zeros(3); count = 0; seen = set()
        for w in self.roles['train_fit']:
            path, _, mask = self.trajectories[w.trajectory]
            ids = [i for i in range(w.start, w.start+20) if (w.trajectory,i) not in seen]
            if not ids: continue
            with np.load(path, allow_pickle=False) as z:
                a = np.stack([z[f][ids][:, mask] for f in ('u','v','p')], -1).reshape(-1,3)
            seen.update((w.trajectory,i) for i in ids)
            total += a.sum(0); squares += (a*a).sum(0); count += len(a)
        variance = squares/count - (total/count)**2
        if np.any(variance <= 0): raise ValueError('Degenerate training scale')
        self._training_statistics=(total/count,np.sqrt(variance))
        return self._training_statistics


class SimulationData:
    """Dispatch the original NPZ interchange and audited mmap directory formats."""
    def __new__(cls, manifest_path, config):
        meta=json.loads(Path(manifest_path).read_text())
        if meta.get('format')=='npy_directory_v1':
            from .prepared_data import PreparedSimulationData
            return PreparedSimulationData(manifest_path,config)
        return NPZSimulationData(manifest_path,config)
