"""Native planar activator-inhibitor systems and source-defined cross diffusion."""
from curation import reviewed_model


def build():
    rows=[]
    rows.append(reviewed_model('1705.08250','S1.E1','gierer-meinhardt-planar-evolution',
        [r'u_t=\varepsilon^2\Delta(u)-u+\frac{u^2}{v}',r'\tau v_t=D\Delta(v)-v+u^2'],
        ['u','v'],['positive activator concentration','positive inhibitor concentration'],
        'gierer_meinhardt','bounded and smooth two-dimensional domain',
        'Source introduces the evolution model on a bounded smooth planar domain',kind='native_2d',
        note='Complete positive-field evolution system (1.1); positivity of v is retained in source evidence and keeps the quotient well-defined. Diffusion/time-scale magnitudes do not create additional records.'))
    rows.append(reviewed_model('1705.08250','S3.E1','gierer-meinhardt-planar-stationary',
        [r'\varepsilon^2\Delta(u)-u+\frac{u^2}{v}=0',r'D\Delta(v)-v+u^2=0'],
        ['u','v'],['stationary activator concentration','stationary inhibitor concentration'],
        'gierer_meinhardt',r'\Omega\subset{\mathbb{R}}^{2}',
        'Author explicitly states the domain of the stationary system (3.1) is a bounded subset of R^2',kind='native_2d',
        note='Source explicitly writes the complete stationary elliptic system (3.1). This is recorded as a stationary structural variant, not a second independent physical mechanism. Rewritten/rescaled spike approximations are not counted.'))
    for model,kinetics in [('schnakenberg','S2.E2'),('brusselator','S2.E3')]:
        reactions = ([r'\gamma(\alpha-u+u^2v)',r'\gamma(\beta-u^2v)'] if model=='schnakenberg'
                     else [r'-(\beta+1)u+u^2v+\alpha',r'\beta u-u^2v'])
        rows.append(reviewed_model('2109.02075','S2.E1',model+'-bidirectional-linear-cross-diffusion',
            [r'u_t=d_u\Delta(u)+d_{vu}\Delta(v)+'+reactions[0],
             r'v_t=d_v\Delta(v)+d_{uv}\Delta(u)+'+reactions[1]],
            ['u','v'],['first chemical concentration','second chemical concentration'],
            'chemical_cross_diffusion',r'\Omega\in\mathbb{R}^{2}',
            'Original model definition (1) explicitly permits both R^2 and R^3; use its R^2 branch',kind='native_2d',
            supporting_anchors=(kinetics,),original_model_key='S2.E1+'+kinetics,
            scalar_parameters=(r'\gamma',),
            note='Substitute the explicitly supplied '+model+' kinetics into the original two/three-dimensional PDE definition (1), retaining both cross-diffusion terms. The numerical demonstration dimension is not used to infer model dimensionality. Different nonzero diffusion coefficients are not separate structures; no 1D equation is padded.'))
    return rows
