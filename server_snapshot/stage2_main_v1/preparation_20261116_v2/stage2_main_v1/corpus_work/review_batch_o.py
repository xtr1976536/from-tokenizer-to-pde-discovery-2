"""Reviewed legacy Stage2 three-field systems with explicitly allowed n=2."""
from curation import reviewed_model


def build():
    rows=[]
    for logistic in (False,True):
        for dynamic in (False,True):
            first=r'u_t=\Delta(u)-\chi\nabla\cdot(u\nabla(v))+\xi\nabla\cdot(u\nabla(w))'
            if logistic:first+=r'+ru-\mu u^2'
            rows.append(reviewed_model('2509.04850','S1.E5' if logistic else 'S1.E4',
                'legacy-attraction-repulsion-'+('logistic-' if logistic else '')+('parabolic' if dynamic else 'elliptic-signals'),
                [first,(r'v_t=' if dynamic else '0=')+r'\Delta(v)+\alpha u-\beta v',
                 (r'w_t=' if dynamic else '0=')+r'\Delta(w)+\gamma u-\delta w'],
                ['u','v','w'],['cell density','attractant concentration','repellent concentration'],
                'chemotaxis',r'\Omega\subset\mathbb{R}^{n}$ ( $n\geq 2$ )', 'n>=2; choose n=2',
                supporting_quotes=(r'\tau\in\{0,1\}',),
                note='Source explicitly unifies the fully parabolic and parabolic-elliptic cases with tau in {0,1}. Use only these named derivative-structure branches; this is not a sweep of nonzero scalar coefficient magnitudes. Old Stage2 formulas are checked again against original displays.'))
    for dynamic in (False,True):
        rows.append(reviewed_model('1703.08389','S1.EGx1' if dynamic else 'S1.E1',
            'legacy-competing-species-produced-signal-'+('parabolic' if dynamic else 'elliptic'),
            [(r'u_t=\Delta(u)' if dynamic else r'u_t=d_1\Delta(u)')+r'-\chi_1\nabla\cdot(u\nabla(w))+\mu_1u(1-u-a_1v)',
             (r'v_t=\Delta(v)' if dynamic else r'v_t=d_2\Delta(v)')+r'-\chi_2\nabla\cdot(v\nabla(w))+\mu_2v(1-a_2u-v)',
             (r'\tau w_t=\Delta(w)' if dynamic else r'0=d_3\Delta(w)')+r'+\alpha u+\beta v-\gamma w'],
            ['u','v','w'],['first competing population','second competing population','produced chemoattractant'],
            'chemotaxis',r'\mathbb{R}^{n}$ ( $n\geq 2$ )', 'n>=2',
            note='The source separately writes the fully parabolic predecessor and its main parabolic-parabolic-elliptic model. Retain its actual unit diffusion coefficients and tau time scale in the parabolic transcription; the chemical production closure is preserved.'))
    for anchor,name,equations,fields,roles in [
        ('S1.EGx10','legacy-indirect-signal-immobile-precursor',
         [r'n_t=\Delta(n)-\nabla\cdot(n\nabla(c))',r'\varepsilon_1 c_t=\Delta(c)-c+w',r'\varepsilon_2 w_t=-w+n'],
         ['n','c','w'],['cell density','chemical signal','immobile precursor']),
        ('S1.EGx12','legacy-indirect-signal-double-elliptic-limit',
         [r'n_t=\Delta(n)-\nabla\cdot(n\nabla(c))',r'0=\Delta(c)-c+w',r'0=\tau\Delta(w)-w+n'],
         ['n','c','w'],['cell density','instantaneous chemical signal','instantaneous precursor']),
        ('S1.E12','legacy-reversible-cell-phenotype-signal',
         [r'u_t=\Delta(u)-\nabla\cdot(u\nabla(v))-\gamma u+\gamma w',r'v_t=\Delta(v)-v+w',r'w_t=\Delta(w)-\gamma w+\gamma u'],
         ['u','v','w'],['motile cell phenotype','chemical signal','second cell phenotype']),
    ]:
        rows.append(reviewed_model('2508.01436',anchor,name,equations,fields,roles,
            'indirect_signalling',r'\Omega\subset\mathbb{R}^{N}$ , $1\leq N\leq 4', '1<=N<=4','N',
            note='Use only the complete source-written model or limit. Shared domain Omega/Gamma is defined at the beginning for 1<=N<=4; choose N=2. The comparison-error equations involving both the solution and reference solution are not counted.'))
    rows.append(reviewed_model('1812.07707','S1.Ex3','legacy-irreversible-bimolecular-product',
        [r'a_t-d_a\Delta(a)=-kab',r'b_t-d_b\Delta(b)=-kab',r'c_t-d_c\Delta(c)=kab'],
        ['a','b','c'],['first reactant','second reactant','product'],
        'mass_action_reaction_diffusion',r'an open subset of $\mathbb{R}^{d}$',
        'General spatial d in the source model definition; choose d=2','d',
        note='Complete irreversible A+B -> C system explicitly displayed in the general-dimensional reaction-diffusion introduction. No passive product is dropped.'))
    return rows
