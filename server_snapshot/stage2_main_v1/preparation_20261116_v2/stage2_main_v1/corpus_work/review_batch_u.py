"""Additional original-source two-field nonlinear transport structures."""
from curation import reviewed_model


def build():
    rows=[]
    for m1,m2 in [(3,2),(4,3)]:
        rows.append(reviewed_model('1902.09787','S1.E1',f'nonlinear-chemo-diffusion-m{m1}-s{m2}',
            [fr'u_t=\nabla\cdot((u+\alpha)^{m1-1}\nabla(u))-\chi\nabla\cdot(u(u+\alpha)^{{{m2-2}}}\nabla(v))',r'v_t=\Delta(v)-v+u'],
            ['u','v'],['cell density','chemical signal'],'quasilinear_chemotaxis',r'\mathbb{R}^{n}',
            'Original general bounded physical domain in R^n; choose n=2',
            power={'values':{'m1':m1,'m2':m2},'source_range_verified':True,'range_statement':'Source explicitly permits m1,m2 in R; retain two total paired assignments'},
            note='The positive scalar alpha is retained in the original; to avoid arbitrarily erasing an internal shift, expand the integer-power polynomial algebraically before outer-coefficient removal. The source parameter alpha is a scalar, not a coordinate.'))
    for p,q in [(1,1),(2,2)]:
        flux1=fr'\partial_x(\frac{{u^{p}u_x}}{{\sqrt{{u^2+u_x^2+u_y^2}}}})+\partial_y(\frac{{u^{p}u_y}}{{\sqrt{{u^2+u_x^2+u_y^2}}}})'
        flux2=fr'\partial_x(\frac{{u^{q}v_x}}{{\sqrt{{1+v_x^2+v_y^2}}}})+\partial_y(\frac{{u^{q}v_y}}{{\sqrt{{1+v_x^2+v_y^2}}}})'
        rows.append(reviewed_model('1903.00125','S1.EGx2',f'flux-limited-chemotaxis-p{p}-q{q}',
            ['u_t='+flux1+'-\chi('+flux2+')',r'0=\Delta(v)-\mu+u'],
            ['u','v'],['positive cell density','elliptic signal'],'flux_limited_chemotaxis',r'\mathbb{R}^{n}(n\in\mathbb{N})',
            'Original spatial ball permits every positive n; select n=2',scalar_parameters=(r'\chi',),
            power={'values':{'p':p,'q':q},'source_range_verified':True,'range_statement':'p,q>=1; retain only paired (1,1) and (2,2)'},
            note='Exact two-component Cartesian divergence expansion; gradient norms contain both x/y derivatives. mu is the time-independent source-defined spatial average of initial density, an outer scalar constant; no nonlocal dynamic integral is erased.'))
    # The source explicitly gives the w=0 Keller-Segel subsystem. Both tau
    # branches are allowed; take constant D from its displayed model (1.2).
    for dynamic in (False,True):
        rows.append(reviewed_model('1903.11318','S1.E2','keller-segel-logistic-'+('parabolic' if dynamic else 'elliptic'),
            [r'u_t=D\Delta(u)-\chi\nabla\cdot(u\nabla(v))+\mu u(1-u)',
             (r'v_t=' if dynamic else '0=')+r'\Delta(v)-v+u'],
            ['u','v'],['cell density','chemical signal'],'chemotaxis',r'\Omega\subset\mathbb{R}^{N}(N\geq 1)',
            'Original physical spatial N>=1, select N=2','N',
            supporting_quotes=(r'\tau\in\{0,1\}',),
            note='Use the source explicitly written w=0 subsystem; no otherwise coupled field is dropped. Constant diffusion and nonzero logistic growth, with the two allowed derivative branches. Duplicates of existing reviewed sources are removed globally.'))
    return rows
