"""Visible-only fits; prediction reward uses frozen train-fit channel z scores."""
import math
import numpy as np
from .contracts import InvalidCandidate


def penalty(counts, alpha=.2):
    if len(counts) != 3 or any(not isinstance(n, (int, np.integer)) or n < 1 for n in counts):
        raise InvalidCandidate('Need positive canonical term counts for three equations')
    return 1 - alpha * math.log10(sum(counts))


def fit_details(system, numerics, data, windows):
    scores = []
    for w in windows:
        visible, _, mask = data.visible(w, 'train_fit')
        _, r2 = numerics.fit(system, visible, mask)
        if len(r2) != 3 or not np.isfinite(r2).all():
            raise InvalidCandidate('Invalid three-equation R2')
        scores.append(r2)
    # Equal window weights within each equation, then equal equation weights.
    if not scores:raise InvalidCandidate('Empty fit window batch')
    per_equation=np.asarray(scores).mean(axis=0)
    return {'r_fit':float(per_equation.mean()),'r2_per_equation':per_equation.tolist(),'fit_windows':len(scores)}


def fit_score(system, numerics, data, windows):
    return fit_details(system,numerics,data,windows)['r_fit']


def qualified_fit(system,numerics,data,windows,threshold=-.0035):
    details=fit_details(system,numerics,data,windows)
    if any(value<=threshold for value in details['r2_per_equation']):
        raise InvalidCandidate('Fit quality gate: each batch-mean equation R2 must be strictly > '+str(threshold))
    return details


def prediction_score(system, numerics, data, role, scale):
    sums = np.zeros(3); n = 0; energy = 0.
    scale=np.asarray(scale,dtype=float);mean=np.asarray(data.training_mean(),dtype=float)
    if scale.shape!=(3,) or mean.shape!=(3,) or not np.isfinite(scale).all() or not np.isfinite(mean).all() or (scale<=0).any():
        raise ValueError('Frozen train-fit mean and positive channel scales required')
    standardized_energy=np.zeros(3)
    for w in data.roles[role]:
        visible, times, mask = data.visible(w, role)
        coefficients, _ = numerics.fit(system, visible, mask)
        prediction = np.asarray(numerics.forecast(system, coefficients, visible, times, mask))
        # Future fields are obtained only AFTER the prediction is produced.
        target, target_mask = data.target(w, role)
        if not np.array_equal(mask, target_mask) or prediction.shape != target.shape:
            raise InvalidCandidate('Forecast shape/mask mismatch')
        p = prediction[:, mask, :]; y = target[:, mask, :]
        if not np.isfinite(p).all(): raise InvalidCandidate('Nonfinite rollout')
        sums += ((p-y)**2).sum(axis=(0,1)); n += y.shape[0]*y.shape[1]
        energy += float((y*y).sum())
        standardized_energy+=(((y-mean)/scale)**2).sum(axis=(0,1))
    if not n or standardized_energy.sum()<=0:raise InvalidCandidate('Empty/zero-standardized-energy forecast target')
    rmse = np.sqrt(sums/n)
    return {'prediction_score': 1/(1+float(np.sum(sums/scale**2))/float(standardized_energy.sum())),
            'prediction_score_version':'train_fit_zscore_energy_v2',
            'standardized_sse_by_channel':(sums/scale**2).tolist(),
            'standardized_target_energy_by_channel':standardized_energy.tolist(),
            'normalization_mean':mean.tolist(),'normalization_scale':scale.tolist(),
            'raw_prediction_score_diagnostic':1/(1+float(sums.sum())/energy) if energy>0 else None,
            'rmse_by_channel': rmse.tolist(),
            'normalized_rmse_by_channel': (rmse/scale).tolist(),
            'normalized_joint_rmse': float(np.sqrt(np.mean(sums/n/scale**2))),
            'sse_by_channel': sums.tolist(), 'target_energy': energy,
            'points_per_channel': n, 'windows': len(data.roles[role])}


def reward(system, numerics, data, windows, scale, weight, alpha,minimum_equation_r2=-.0035):
    if weight!=1.:
        raise ValueError('Stage1 reward is fit-only; prediction mixture weights are retired')
    details=qualified_fit(system,numerics,data,windows,minimum_equation_r2)
    rfit=details['r_fit']
    counts = numerics.term_counts(system); p = penalty(counts, alpha)
    return {'reward': p*rfit,'reward_version':'stage1_fit_sparse_v1',
            **details,
            'term_counts': list(counts), 'penalty': p}
