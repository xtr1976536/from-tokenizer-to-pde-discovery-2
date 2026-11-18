"""Independent signed checks for new vector reductions and nonlinear closures."""
import json
from hashlib import sha256
import sympy as sp
from curation import OUT
from audit_component_expansions import U,V,P,W,x,y,t,lap,symbolic,real_jets
from direct_parser import parse
from ast_runtime import expand_laplacian


def main():
    rows={r['id']:r for r in map(json.loads,(OUT/'reviewed-unique-structures.jsonl').read_text().splitlines())}
    E,a,b,c,d=sp.symbols('varepsilon a b c d',real=True)
    dt=lambda z:sp.diff(z,t)
    expected={}
    patterns={'generic':(1,1,1,1),'kdv-kdv':(1,0,1,0),'schrodinger-d':(1,0,1,1),'schrodinger-b':(1,1,1,0),
              'bbm-bbm':(0,1,0,1),'original-velocity-bbm':(0,0,0,1),'original-height-bbm':(0,1,0,0)}
    for name,(aa,bb,cc,dd) in patterns.items():
        velocity=sp.Matrix([V,P]);axes=(x,y)
        mass=dt(U)+sum(sp.diff(velocity[i],axis) for i,axis in enumerate(axes))
        mass+=E*sum(sp.diff(U*velocity[i]+aa*a*lap(velocity[i]),axis) for i,axis in enumerate(axes))-E*bb*b*lap(dt(U))
        momentum=[dt(velocity[i])+sp.diff(U,axis)+E*sp.diff((velocity.dot(velocity))/2+cc*c*lap(U),axis)-E*dd*d*lap(dt(velocity[i])) for i,axis in enumerate(axes)]
        expected['planar-abcd-boussinesq-'+name]=[mass]+momentum
    eps,mu=sp.symbols('epsilon mu',real=True)
    expected['maxwell-planar-tm-polarization']=[eps*dt(U)-sp.diff(P,x)+sp.diff(V,y),mu*dt(V)+sp.diff(U,y),mu*dt(P)-sp.diff(U,x)]
    d1,d2,d3,k1,k2,k3=sp.symbols('d_1 d_2 d_3 k_1 k_2 k_3',real=True)
    enzyme=[dt(U)-d1*lap(U)+k1*U*(P-V)-k2*V,dt(V)-d2*lap(V)-k1*U*(P-V)+(k2+k3)*V]
    expected['enzyme-irreversible-total-enzyme-system']=enzyme+[dt(P)-d2*lap(V)-d3*(lap(P)-lap(V))]
    expected['enzyme-total-enzyme-equal-diffusivity']=enzyme+[dt(P)-d2*lap(P)]
    f,e=sp.symbols('f e',real=True)
    D=a*U+b*P+c;reaction=(e*U-f*P)*V/D
    expected['enzyme-reversible-qss-shared-enzyme']=[D*(dt(U)-d1*lap(U)+reaction),dt(V)-d2*lap(V),D*(dt(P)-d3*lap(P)-reaction)]
    chi,xi=sp.symbols('chi xi',real=True)
    for m in (1,2):
        for dynamic in (False,True):
            for growth in (False,True):
                divergence=lambda z,q:sum(sp.diff(z*sp.diff(q,axis),axis) for axis in (x,y))
                mass=dt(U)-sum(sp.diff((1+U)**(m-1)*sp.diff(U,axis),axis) for axis in (x,y))+chi*divergence(U,V)+xi*divergence(U,P)
                if growth:mass-=mu*U*(1-U-P)
                expected[f'haptotaxis-m{m}-tau{int(dynamic)}-growth{int(growth)}']=[mass,(dt(V) if dynamic else 0)-lap(V)+V-U,dt(P)+V*P]
    D1,D2,beta=sp.symbols('D_1 D_2 beta',real=True)
    expected['oncolytic-virotherapy-no-growth']=[dt(U)-lap(U)+sum(sp.diff(U*sp.diff(V,axis),axis) for axis in (x,y))+U*W,
        dt(V)+(U+P)*V,dt(P)-D1*lap(P)+P-U*W,dt(W)-D2*lap(W)+W+U*W-beta*P]
    tau,rate=sp.symbols('tau P',real=True)
    for taxis in (False,True):
        R=rate*(P+(chi*(1-U) if taxis else 0)-V)
        expected['viscous-cahn-hilliard-nutrient-'+('chemotaxis' if taxis else 'no-chemotaxis')]=[
            dt(U)-lap(V)-R,V-tau*dt(U)+lap(U)-U**3+U+(chi*P if taxis else 0),
            dt(P)-lap(P)+(chi*lap(U) if taxis else 0)+R]
    for p,q in [(1,1),(2,2)]:
        gradnorm=lambda z:sum(sp.diff(z,axis)**2 for axis in (x,y))
        diffusion=sum(sp.diff(U**p*sp.diff(U,axis)/sp.sqrt(U**2+gradnorm(U)),axis) for axis in (x,y))
        taxis=sum(sp.diff(U**q*sp.diff(V,axis)/sp.sqrt(1+gradnorm(V)),axis) for axis in (x,y))
        expected[f'flux-limited-chemotaxis-p{p}-q{q}']=[dt(U)-diffusion+chi*taxis,-lap(V)+mu-U]
    A=sp.Symbol('A',real=True)
    expected['liouville-planar-stationary-combustion']=[lap(U)-A*sp.exp(U)]
    checked=[]
    for name,reference in expected.items():
        row=rows[name]
        for eq,ref in zip(row['reviewed_transcription'],reference):
            lhs,rhs=eq.split('=')
            left,_=parse(lhs,tuple(row['source_fields']),row['explicit_scalar_parameters'])
            right,_=parse(rhs,tuple(row['source_fields']),row['explicit_scalar_parameters'])
            fields={'u':U,'v':V,'p':P,'w':W}
            actual=symbolic(expand_laplacian(left,('x','y')),fields)-symbolic(expand_laplacian(right,('x','y')),fields)
            delta=real_jets(actual-ref)
            assert sp.cancel(delta)==0,(name,delta)
        assert len(reference)==len(row['reviewed_transcription'])
        checked.append(name)
    report=dict(status='PASS',systems_checked=len(checked),scalar_equations_checked=sum(len(expected[n]) for n in checked),
                ids=checked,input_corpus_sha256=sha256((OUT/'reviewed-unique-structures.jsonl').read_bytes()).hexdigest(),
                method='Independent signed SymPy vector/divergence/curl/constitutive expressions before coefficient stripping; exact positive-denominator clearing')
    (OUT/'new-component-expansion-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='ids'},ensure_ascii=False))


if __name__=='__main__':main()
