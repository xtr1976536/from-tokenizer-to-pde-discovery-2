"""Explicit local-sensing and noninteracting spatial epidemic models."""
from curation import reviewed_model


def build():
    rows=[]
    rows.append(reviewed_model('2608.09491','S1.E2','local-sensing-exponential-motility-nutrient',
        [r'u_t=\Delta(u\exp(-v))+\alpha um',
         r'v_t=\Delta(v)-v+\chi\theta_1u',r'm_t=\Delta(m)-um'],
        ['u','v','m'],['cell density','rescaled chemoattractant concentration','nutrient concentration'],
        'local_sensing_chemotaxis',r'\Omega\subset\mathbb{R}^{2}',
        'Source defining domain is a bounded subset of R^2',kind='native_2d',
        supporting_quotes=(r'\phi(v)=e^{-\chi v}',),
        note='Use the source explicitly discussed motility phi(v)=exp(-chi*v), chi>0, in source system (1.2). Make the exact field-unit change v_new=chi*v_source: the motility is exp(-v_new) and the signal production coefficient becomes chi*theta_1. All other factors remain outer scalar coefficients. The unspecified dual-dependent gamma(v,m) in (1.1) is NOT arbitrarily filled in.'))
    rows.append(reviewed_model('2003.13967','S2.EGx3','sir-independent-self-diffusion',
        [r'S_t=D_S\Delta(S)-cSI',r'I_t=D_I\Delta(I)+cSI-wI',r'R_t=D_R\Delta(R)+wI'],
        ['S','I','R'],['susceptible density','infected density','recovered density'],
        'epidemic_reaction_diffusion','number of spatial dimensions $d$',
        'The DDFT formulation explicitly defines a general spatial dimension d; specialize to d=2','d',
        supporting_anchors=('S2.E6',),
        supporting_quotes=(r'C_{\mathrm{si}}=C_{\mathrm{sd}}=0',),
        note='The author explicitly compares the no-interaction case, called the usual SIR model with diffusion, against the interacting model. Set only those source-specified interaction coefficients C_si=C_sd=0 in (7)-(9). The ideal-gas free-energy constitutive law gives D_i*Delta on the source general-d domain; d=2 is an allowed model specialization, independent of the dimension used in a particular simulation. No convolution kernel is invented or silently removed from an interacting model.'))
    return rows
