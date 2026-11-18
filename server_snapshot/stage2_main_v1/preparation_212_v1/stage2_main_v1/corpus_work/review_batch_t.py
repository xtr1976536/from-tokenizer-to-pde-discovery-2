"""Explicit three-field biological systems and source-permitted derivative branches."""
from curation import reviewed_model


def build():
    rows=[]
    for m in (1,2):
        for dynamic in (False,True):
            for logistic in (False,True):
                flux=r'\Delta(u)' if m==1 else r'\nabla\cdot((1+u)\nabla(u))'
                first='u_t='+flux+r'-\chi\nabla\cdot(u\nabla(v))-\xi\nabla\cdot(u\nabla(p))'
                if logistic:first+=r'+\mu u(1-u-p)'
                rows.append(reviewed_model('1903.11318','S1.E3',f'haptotaxis-m{m}-tau{int(dynamic)}-growth{int(logistic)}',
                    [first,(r'v_t=' if dynamic else '0=')+r'\Delta(v)-v+u',r'p_t=-vp'],
                    ['u','v','p'],['cancer cell density','matrix-degrading enzyme','extracellular matrix'],
                    'chemotaxis_haptotaxis',r'\Omega\subset\mathbb{R}^{N}(N\geq 1)',
                    'Physical domain explicitly has spatial N>=1; select N=2','N',
                    supporting_quotes=(r'\mu\geq 0,\tau\in\{0,1\}',r'D\equiv D(u)=C_{D}(u+1)^{m-1}'),
                    power={'values':{'m':m},'source_range_verified':True,'range_statement':'m in R; use only m=1 and m=2 across all derivative branches'},
                    note='Source explicitly permits tau=0/1 and mu=0/nonzero, and gives the (1+u)^(m-1) diffusivity prototype. Only these named structural branches and two total power assignments are retained. Nonzero chi/xi and all three physical fields remain.'))
    for exponent in (2,3):
        for diffusive in (False,True):
            rows.append(reviewed_model('2010.05641','S1.EGx3' if diffusive else 'S0.EGx2',
                f'indirect-logistic-theta{exponent}-diffusion{int(diffusive)}',
                ['u_t='+ (r'\epsilon\Delta(u)-' if diffusive else '-')+r'\nabla\cdot(u\nabla(v))+ru-\mu u^'+str(exponent),
                 r'0=d_1\Delta(v)-\beta v+\alpha p',r'0=d_2\Delta(p)-\delta p+\gamma u'],
                ['u','v','p'],['cell density','indirect signal','precursor'],
                'indirect_signalling',r'\Omega\subset\mathbb{R}^{n}',
                'Original models explicitly allow bounded spatial domains n>=1; select n=2',
                supporting_quotes=(r'\theta>1',),original_model_key='indirect-logistic-original-and-vanishing-viscosity',
                power={'values':{'theta':exponent},'source_range_verified':True,'range_statement':'theta>1 in model definition; select theta=2 or 3, without claiming blow-up theorem for theta=3'},
                note='The source separately writes the parabolic and hyperbolic cell equations with two elliptic signals. The source theorem restriction theta<=2 for a particular blow-up result is not confused with the model definition theta>1.'))
    for exponent in (2,3):
        rows.append(reviewed_model('2609.03128','S0.Ex1',f'indirect-allee-exponential-motility-theta{exponent}',
            [fr'u_t=\Delta(\exp(-v)u)+\mu u(1-u^{exponent})(u-A)',r'v_t=\Delta(v)-v+p',r'p_t=-\delta p+u'],
            ['u','v','p'],['cell density','motility signal','immobile intermediate'],
            'density_suppressed_motility',r'\Omega\subset\mathbb{R}^{d}(d\geq 2)',
            'Original system on a physical d>=2 domain; choose d=2','d',
            supporting_quotes=(r'\gamma(s)=e^{-s}',r'\theta\geq 1'),
            scalar_parameters=('A',),
            power={'values':{'theta':exponent,'beta':1},'source_range_verified':True,'range_statement':'theta>=1,beta>0; beta=1,theta=2 or 3'},
            note='Use the explicit exp(-s) motility prototype and beta=1; gamma is not invented or left undefined. A is an outer reaction coefficient after polynomial expansion. The source Allee model is distinguished from the introductory formula with a typesetting error.'))
    rows.append(reviewed_model('2512.22946','S1.E1','predator-prey-produced-signal-no-logistic',
        [r'u_t=d_1\Delta(u)-\chi\nabla\cdot(u\nabla(p))-auv',r'v_t=d_2\Delta(v)+buv-cv',r'p_t=d_3\Delta(p)+du-ep'],
        ['u','v','p'],['prey density','predator density','prey-produced signal'],
        'predator_prey_chemotaxis',r'\Omega\subset\mathbb{R}^{n}',
        'The source reaction-cross-diffusion problem defines physical n in N; take n=2',
        model_dimension_link='predator-prey',
        note='Complete source introduction model (1.1), distinct from the generic many-species framework. All three equations, signal production and predation are retained.'))
    for chemotaxis in (False,True):
        reaction=r'P(p-v)' if not chemotaxis else r'P(p+\chi(1-u)-v)'
        rows.append(reviewed_model('2311.10457','S1.EGx1','viscous-cahn-hilliard-nutrient-'+('chemotaxis' if chemotaxis else 'no-chemotaxis'),
            ['u_t=\Delta(v)+'+reaction,
             r'v=\tau u_t-\Delta(u)+u^3-u'+(r'-\chi p' if chemotaxis else ''),
             r'p_t=\Delta(p)'+(r'-\chi\Delta(u)' if chemotaxis else '')+'-'+reaction],
            ['u','v','p'],['phase fraction difference','chemical potential','nutrient concentration'],
            'tumor_phase_field',r'd=2,3',
            'Source local state problem is explicitly defined on physical spatial d=2,3; choose d=2','d',
            model_dimension_link='local problem',supporting_anchors=('S1.EGx2','S1.E6'),scalar_parameters=('P',),
            note='Source-permitted constant positive mobilities, P0=P1 constant proliferation, zero external controls, explicit quartic double-well potential. Use only chi=0 and chi>0 branches explicitly allowed by chi>=0. Retain tau>0 viscosity. Different nonzero scalar magnitudes do not generate extra entries.'))
    # A nonzero diffusion difference vs the explicitly discussed equal-diffusivity case.
    domain=r'\Omega=(0,L_{1})\times(0,L_{2})\times\cdots\times(0,L_{n})\subseteq\mathbb{R}^{n}'
    rows.append(reviewed_model('1707.04043','S3.EGx5','enzyme-total-enzyme-equal-diffusivity',
        [r'u_t=d_1\Delta(u)-k_1u(p-v)+k_2v',r'v_t=d_2\Delta(v)+k_1u(p-v)-(k_2+k_3)v',r'p_t=d_2\Delta(p)'],
        ['u','v','p'],['substrate','complex','total enzyme'],'enzyme_reaction_diffusion',domain,
        'Original PDE region and explicitly described n-dimensional rectangular case; take n=2',
        model_dimension_link='irreversible case',supporting_quotes=(r'\delta_{e}=\delta_{c}',),
        note='Exact equal enzyme/complex diffusivity branch explicitly discussed by the source; this removes the cross-Laplacian in the total-enzyme row. No arbitrary diffusion term is suppressed.'))
    # Clear the common strictly-positive source denominator; preserve every term.
    rows.append(reviewed_model('1707.04043','S3.EGx11','enzyme-reversible-qss-shared-enzyme',
        [r'(a u+b p+c)(u_t-d_1\Delta(u))=-(e u-fp)v',r'v_t=d_2\Delta(v)',
         r'(a u+b p+c)(p_t-d_3\Delta(p))=(e u-fp)v'],
        ['u','v','p'],['substrate','total enzyme','product'],'enzyme_reaction_diffusion',domain,
        'Original spatial region includes n-dimensional rectangles; take n=2',
        model_dimension_link='reversible case',scalar_parameters=('a','b','c'),
        note='Exact source QSS model (3.14): multiply substrate and product rows by positive D=k1*s+k-2*p+k-1+k2 before removing coefficients. a=k1,b=k-2,c=k-1+k2,e=k1*k2,f=k-1*k-2. This is an equivalent implicit polynomial structural representation; no internal parameter is arbitrarily set to one. Evolution tau is renamed t.'))
    for growth in (False,True):
        rows.append(reviewed_model('2005.09915','S1.E1','oncolytic-virotherapy-'+('logistic' if growth else 'no-growth'),
            [r'u_t=\Delta(u)-\nabla\cdot(u\nabla(v))-uw'+(r'+\mu u(1-u)' if growth else ''),
             r'v_t=-(u+p)v',r'p_t=D_1\Delta(p)-p+uw',r'w_t=D_2\Delta(w)-w-uw+\beta p'],
            ['u','v','p','w'],['uninfected tumor','normal tissue','infected tumor','virus'],
            'oncolytic_virotherapy',r'\Omega\subset\mathbb{R}^{2}',
            'Original complete model explicitly defines the planar physical domain',kind='native_2d',
            supporting_quotes=(r'\mu=0',),
            note='Source explicitly discusses both the positive logistic rate and previously proved zero-growth model. All four fields retained; only this source-stated zero/nonzero growth distinction is counted.'))
    return rows
