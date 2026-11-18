"""Native 2D epidemic systems from arXiv and original publisher HTML."""
from curation import reviewed_model

PUBLISHER='https://www.cambridge.org/core/journals/european-journal-of-applied-mathematics/article/spatiotemporal-behaviour-of-sir-models-with-crossdiffusion-and-vital-dynamics/F33014FE3C7FC7F75F5608E66030C421'


def build():
    rows=[]
    rows.append(reviewed_model('2605.19886','S2.E1','seir-direct-exposed-pathways-vital-dynamics',
        [r'S_t=\lambda\Delta(S)+\Lambda-\beta SI-\mu S',
         r'E_t=\lambda\Delta(E)+\beta pSI-(\delta+\eta+\mu)E',
         r'I_t=\lambda\Delta(I)+\beta(1-p)SI+\delta E-(\gamma+\mu)I',
         r'R_t=\lambda\Delta(R)+\eta E+\gamma I-\mu R'],
        ['S','E','I','R'],['susceptible density','exposed density','infected density','recovered density'],
        'epidemic_reaction_diffusion',r'\Omega\subset\mathbb{R}^{d}$ $(d=1,2)$',
        'Source d=1,2; choose the explicitly allowed spatial d=2 case','d',
        note='Complete four-compartment source (2.1). Keep both source infection pathways for generic 0<p<1. Source probability p is a scalar coefficient and is removed before the infected field I is renamed to canonical p; no symbol-role collision.'))
    common=dict(source_url=PUBLISHER,source_group='doi:10.1017/S095679252400086X',kind='native_2d')
    rows.append(reviewed_model('cambridge-S095679252400086X','disp4','sir-commuting-cross-diffusion',
        [r'S_t=-D\beta S\Delta(I)-\beta SI',
         r'I_t=D\beta S\Delta(I)+\beta SI-\gamma I',r'R_t=\gamma I'],
        ['S','I','R'],['susceptible density','infected density','recovered density'],
        'epidemic_cross_diffusion','derive the two-dimensional PDE model',
        'Author derives the explicit Cartesian I_xx+I_yy system (2.1)',
        note='Use the original publisher equation (2.1), which explicitly contains I_xx+I_yy. Do not pad the preceding 1D equation (1.1). The unusual S*Delta(I) cross-diffusion is preserved exactly.',**common))
    rows.append(reviewed_model('cambridge-S095679252400086X','disp2','sir-commuting-cross-diffusion-vital-dynamics',
        [r'S_t=-D\beta S\Delta(I)-\beta SI+rS-\mu S-\frac{r}{K}S^2',
         r'I_t=D\beta S\Delta(I)+\beta SI-mI',r'R_t=\gamma I-\mu R'],
        ['S','I','R'],['susceptible density','infected density','recovered density'],
        'epidemic_cross_diffusion','derivation of a general two-dimensional PDE model',
        'The original author explicitly introduces (1.2) as the 2D model with vital dynamics',
        supporting_anchors=('disp4',),
        note='Complete original two-dimensional system (1.2), including logistic growth, natural mortality, and infected removal. Source m=mu+gamma+omega is a removal coefficient; it is not a fourth population.',**common))
    return rows
