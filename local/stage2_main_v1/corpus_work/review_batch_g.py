"""Two explicitly planar dissipative-wave PDEs, split into real fields."""
from curation import reviewed_model


def build():
    density='(u^2+v^2)'
    cubic='(u^2+v^2)'
    quintic='(u^2+v^2)^2'
    first=reviewed_model('1803.08439','S0.EGx2','cubic-quintic-complex-ginzburg-landau',
        [fr'u_t=\mu u+\beta_r{cubic}u-\beta_i{cubic}v+\gamma_r{quintic}u-\gamma_i{quintic}v+D_r\Delta(u)-D_i\Delta(v)',
         fr'v_t=\mu v+\beta_r{cubic}v+\beta_i{cubic}u+\gamma_r{quintic}v+\gamma_i{quintic}u+D_r\Delta(v)+D_i\Delta(u)'],
        ['u','v'],['real complex-amplitude component','imaginary complex-amplitude component'],
        'complex_ginzburg_landau','the two-dimensional transverse Laplacian',
        'Two transverse spatial axes x/y; author rewrites propagation evolution in hydrodynamical time form (2)',kind='native_2d',
        note='Exact split A=u+i*v of author equation (2). Cubic and quintic terms are BOTH present in the original model; these are not extra exponent-sweep instances. The two spatial axes are transverse x/y, not a space-time pair.')
    gain=r'(-\gamma_1+\gamma_2(u^2+v^2)-\gamma_3(u^2+v^2)^2)'
    second=reviewed_model('0908.0973','S1.EGx2','dissipative-gap-wave-periodic-lattice',
        [fr'-v_t=-D_0\Delta(u)+{density}u-A(\cos(x)+\cos(y))u-\epsilon{gain}v',
         fr'u_t=-D_0\Delta(v)+{density}v-A(\cos(x)+\cos(y))v+\epsilon{gain}u'],
        ['u','v'],['real complex-wave component','imaginary complex-wave component'],
        'complex_ginzburg_landau','2D transverse grating',
        'Author equation (2) explicitly has two spatial axes x/y; evolution t is propagation distance',kind='native_2d',
        scalar_parameters=('A',),
        note='Exact real/imaginary split of author 2D equation (2), not its 1D precursor (1). Normalize affine coordinates X=2*q_0*(x-L/2), Y=2*q_0*(y-L/2) for the nonzero source lattice wavenumber. Then cos terms become cos(X),cos(Y), and D_0=2*q_0^2 is an outer scalar diffusion coefficient. Relabel X,Y to x,y. Lattice-frequency choices are not counted as separate structures.')
    return [first,second]
