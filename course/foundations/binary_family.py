"""Original synthetic binary: ideal branches I1/I2 and regular branch R1.

Contract: binary_family_contract.md. Fixed p=100000 Pa;
T=600..1800 K; x is B mole fraction of atoms. All outputs are molar,
GM/HM in J/mol and SM in J/(mol K). No real-material applicability.
Reject invalid conditions; never clip compositions or evaluate log(0).
"""
from typing import Any
import numpy as np
from numpy.typing import NDArray
from scipy.special import xlogy

R = 8.3145  # Declared rounded value, matched to pinned pycalphad.
DELTA = 12000.0


def _temperature(T: Any) -> float:
    """Require one finite scalar temperature within the contract interval."""
    t = np.asarray(T, dtype=float)
    if t.ndim != 0 or not np.isfinite(t) or not 600 <= t <= 1800:
        raise ValueError('T must be a finite scalar in [600, 1800] K')
    return float(t)


def _composition(x: Any) -> NDArray[np.float64]:
    """Accept a scalar or nonempty 1D composition array without changing it."""
    value = np.asarray(x, dtype=float)
    if value.ndim > 1 or value.size == 0 or not np.all(np.isfinite(value)):
        raise ValueError('x must be a nonempty finite scalar or 1D array')
    if np.any((value < 0) | (value > 1)):
        raise ValueError('x must lie in [0, 1]; no clipping is permitted')
    return value


def ideal_properties(T: Any, x: Any, phase: str = 'ALPHA') -> dict[str, NDArray[np.float64]]:
    """Evaluate a homogeneous ideal branch, including exact pure limits.

    The ideal mixing reference is this same phase's weighted pure endmembers
    at the same T,p. HM_mix=0 does not imply HM=0. This is property evaluation,
    not an equilibrium solver. Returned arrays have x's shape (0D for scalar).
    xlogy uses the continuous zero limit; see scipy.special.xlogy documentation.
    """
    t, value = _temperature(T), _composition(x)
    if phase not in ('ALPHA', 'BETA'):
        raise ValueError('phase must be ALPHA or BETA')
    h_reference = 1000.0 + DELTA * (value if phase == 'ALPHA' else 1-value)
    g_reference = h_reference - 10.0*t
    q = xlogy(value, value) + xlogy(1-value, 1-value)
    s_mix = -R*q
    g_mix = -t*s_mix
    return {key: np.asarray(val) for key, val in {
        'GM': g_reference+g_mix, 'HM': h_reference, 'SM': 10.0+s_mix,
        'GM_reference': g_reference, 'GM_mix': g_mix,
        'HM_mix': np.zeros_like(value), 'SM_mix': s_mix,
    }.items()}


# Lesson 5: discrete feasible search and a separately derived I2 equilibrium oracle.
from scipy.optimize import linprog


def _scalar_composition(x: Any) -> float:
    value = _composition(x)
    if value.ndim != 0:
        raise ValueError('one scalar composition is required')
    return float(value)


def lever_fraction(z: Any, left: Any, right: Any) -> float:
    """Return amount fraction on the right for supplied distinct compositions.

    Requires 0<=left<=z<=right<=1 and left<right. This is balance only,
    not a claim of equilibrium; coincident compositions cannot determine f.
    """
    z, left, right = map(_scalar_composition, (z, left, right))
    if not left < right or not left <= z <= right:
        raise ValueError('distinct ordered endpoints must bracket z')
    return (z-left)/(right-left)


def ideal_equilibrium(T: Any, z: Any) -> dict[str, Any]:
    """Continuous I2 solution from strict convexity and a common supporting line.

    See the contract's analytical controls. Only positive-amount regions are reported;
    no composition is claimed for absent phases. GM is per mole of all atoms.
    """
    t, z = _temperature(T), _scalar_composition(z)
    left = 1.0/(1.0+np.exp(DELTA/(R*t)))
    right = 1.0-left
    if z <= left:
        regions = [{'phase':'ALPHA','x':z,'f':1.0}]
    elif z >= right:
        regions = [{'phase':'BETA','x':z,'f':1.0}]
    else:
        fb = lever_fraction(z,left,right)
        regions = [{'phase':'ALPHA','x':left,'f':1-fb},
                   {'phase':'BETA','x':right,'f':fb}]
    energy = sum(r['f']*float(ideal_properties(t,r['x'],r['phase'])['GM']) for r in regions)
    return {'GM':energy,'regions':regions}


def ideal_grid(T: Any, z: Any, points: int = 21) -> dict[str, Any]:
    """Minimize I2 over a finite uniform composition grid in each phase.

    Linear weights obey total and B constraints; these imply A balance.
    Result is a feasible upper bound to continuous equilibrium, not exact
    coexistence. Audit both balances and reject failed/nonfinite/infeasible
    solver output. A mocked failure in tests is not a second numerical solver.
    """
    t, z = _temperature(T), _scalar_composition(z)
    if isinstance(points,bool) or not isinstance(points,(int,np.integer)) or points<2:
        raise ValueError('points must be an integer >= 2')
    grid = np.linspace(0,1,points)
    x = np.tile(grid,2)
    energies = np.concatenate([ideal_properties(t,grid,p)['GM'] for p in ('ALPHA','BETA')])
    result = linprog(energies,A_eq=np.array([np.ones_like(x),x]),b_eq=[1,z],
                     bounds=(0,None),method='highs')
    if not result.success:
        raise RuntimeError('discrete search failed: '+str(result.message))
    weights = np.asarray(result.x)
    if (not np.all(np.isfinite(weights)) or np.any(weights<0)
        or abs(weights.sum()-1)>1e-10 or abs(weights@x-z)>1e-10
        or abs(weights@(1-x)-(1-z))>1e-10):
        raise RuntimeError('discrete search returned invalid or unbalanced amounts')
    regions = [{'phase':'ALPHA' if i<points else 'BETA','x':float(x[i]),'f':float(w)}
               for i,w in enumerate(weights) if w>0]
    return {'GM':float(weights@energies),'regions':regions,'points_per_phase':int(points)}


def ideal_derivatives(T: Any, x: Any, phase: str = 'ALPHA') -> dict[str, NDArray[np.float64]]:
    """I1/I2 slopes, curvature and addition chemical potentials, interior only.

    mu_A and mu_B are derivatives of total G at fixed other-component amount;
    slope=mu_B-mu_A is fixed-total exchange. Units J/mol (x dimensionless).
    Reject endpoints and nonfinite outputs, including curvature overflow at
    extremely dilute representable x. No epsilon substitution or clipping.
    """
    t, value = _temperature(T), _composition(x)
    if phase not in ('ALPHA','BETA'):
        raise ValueError('phase must be ALPHA or BETA')
    if np.any((value == 0) | (value == 1)):
        raise ValueError('derivatives require strictly interior x')
    ga = 1000-10*t+(DELTA if phase=='BETA' else 0.)
    gb = 1000-10*t+(DELTA if phase=='ALPHA' else 0.)
    with np.errstate(over='ignore',divide='ignore',invalid='ignore'):
        log_a, log_b = np.log1p(-value), np.log(value)
        result = {'slope':gb-ga+R*t*(log_b-log_a),
                  'curvature':R*t*(1/value+1/(1-value)),
                  'mu_A':ga+R*t*log_a,'mu_B':gb+R*t*log_b}
    if not all(np.all(np.isfinite(v)) for v in result.values()):
        raise ValueError('nonfinite derivative output at this composition')
    return {k:np.asarray(v) for k,v in result.items()}


# Lesson 7: R1 uses ALPHA only; two regions are compositions of the same structure.
from scipy.optimize import brentq
OMEGA_R1 = 20000.0
TC_R1 = OMEGA_R1/(2*R)


def _interaction(omega: Any) -> float:
    value = np.asarray(omega,dtype=float)
    if value.ndim != 0 or not np.isfinite(value) or not 0 <= value <= 24000:
        raise ValueError('omega must be a finite scalar in [0, 24000] J/mol')
    return float(value)


def regular_properties(T: Any, x: Any, omega: Any = OMEGA_R1) -> dict[str, NDArray[np.float64]]:
    """Homogeneous ALPHA properties, including unstable states and pure limits.

    Constant omega affects mixing enthalpy/G, not entropy. Trial omega supports
    later homogeneous fitting; R1 coexistence remains fixed at OMEGA_R1.
    """
    interaction = _interaction(omega)
    value = _composition(x)
    result = ideal_properties(T,value,'ALPHA')
    excess = interaction*value*(1-value)
    for key in ('GM','HM','GM_mix','HM_mix'):
        result[key] = np.asarray(result[key]+excess)
    return result


def regular_derivatives(T: Any, x: Any) -> dict[str, NDArray[np.float64]]:
    """Interior derivatives for fixed R1; full g slope includes the DELTA tilt."""
    value = _composition(x)
    result = ideal_derivatives(T,value,'ALPHA')
    result['slope'] = np.asarray(result['slope']+OMEGA_R1*(1-2*value))
    result['curvature'] = np.asarray(result['curvature']-2*OMEGA_R1)
    result['mu_A'] = np.asarray(result['mu_A']+OMEGA_R1*value**2)
    result['mu_B'] = np.asarray(result['mu_B']+OMEGA_R1*(1-value)**2)
    return result


def regular_binodal(T: Any) -> dict[str, Any]:
    """R1 coexistence with an explicit supported near-critical boundary.

    Solve the noncentral root only on (0, left spinodal). The exact central
    root is excluded structurally and checked again before returning. A small
    residual alone never certifies a gap. At/above Tc return single-phase status;
    for Tc*(1-1e-6)<T<Tc reject automatic endpoints, while properties still work.
    """
    t = _temperature(T)
    if t >= TC_R1:
        return {'status':'single_phase','compositions':[],'spinodal':[]}
    if t > TC_R1*(1-1e-6):
        raise ValueError('unqualified near-critical coexistence interval')
    spin_left = (1-np.sqrt(1-2*R*t/OMEGA_R1))/2
    def residual(x: float) -> float:
        return float(R*t*(np.log(x)-np.log1p(-x))+OMEGA_R1*(1-2*x))
    left, result = brentq(residual,np.nextafter(0.,1.),spin_left,
                         xtol=1e-15,rtol=1e-14,maxiter=100,full_output=True,disp=False)
    right = 1-left
    if not result.converged or not 0 < left < spin_left < .5 < right < 1:
        raise RuntimeError('R1 noncentral coexistence root failed qualification')
    if abs(residual(left))>1e-6:
        raise RuntimeError('R1 coexistence residual exceeds contract tolerance')
    return {'status':'two_compositions','compositions':[float(left),float(right)],
            'spinodal':[float(spin_left),float(1-spin_left)]}


def regular_equilibrium(T: Any, z: Any) -> dict[str, Any]:
    """Closed R1 state; repeated ALPHA labels denote composition-separated regions."""
    t, z = _temperature(T), _scalar_composition(z)
    coexistence = regular_binodal(t)
    endpoints = coexistence['compositions']
    if endpoints and endpoints[0] < z < endpoints[1]:
        left,right = endpoints
        f_right = lever_fraction(z,left,right)
        regions = [{'phase':'ALPHA','x':left,'f':1-f_right},
                   {'phase':'ALPHA','x':right,'f':f_right}]
    else:
        regions = [{'phase':'ALPHA','x':z,'f':1.0}]
    energy = sum(r['f']*float(regular_properties(t,r['x'])['GM']) for r in regions)
    return {'GM':energy,'regions':regions}
