"""Pinned pycalphad representation of the synthetic binary family.

Original TDB independently spells out the model. Only input validation/constants
are shared with the plain route; property/equilibrium outputs come from pycalphad.
Explicit points avoid replacing homogeneous observables by an equilibrium split.
No near-critical R1 tool comparison or real-material applicability is claimed.
"""
from pathlib import Path
from typing import Any
import numpy as np
from pycalphad import Database,calculate,equilibrium,variables as v
from course.foundations.binary_family import _temperature,_composition,_scalar_composition,_interaction

MODEL_PATH=Path(__file__).with_name('binary_family.tdb')


def homogeneous_properties(T: Any,x: Any,phase: str='ALPHA',omega: Any=0.) -> dict[str,Any]:
    """Fixed homogeneous composition, including unstable/metastable ALPHA.

    GM/HM J/mol atoms; SM J/(mol atoms K). The one-sublattice site order is A,B.
    Record actual returned composition and reject unexpected shifts/nonfinite
    outputs. Exact model pure limits remain separately tested in the plain route.
    """
    t,value,interaction=_temperature(T),_composition(x),_interaction(omega)
    if phase not in ('ALPHA','BETA') or (phase=='BETA' and interaction!=0):
        raise ValueError('use ALPHA with declared omega, or ideal BETA only')
    database=Database(str(MODEL_PATH))
    points=np.column_stack((1-value.ravel(),value.ravel()))
    result={}
    for output in ('GM','HM','SM'):
        dataset=calculate(database,['A','B'],phase,T=t,P=100000,N=1,
                          points=points,output=output,parameters={'LZERO':interaction},fake_points=False)
        actual=np.asarray(dataset.X.sel(component='B')).reshape(value.shape)
        values=np.asarray(dataset[output]).reshape(value.shape)
        if (not np.all(np.isfinite(values)) or not np.all(np.isfinite(actual))
            or not np.allclose(actual,value,atol=1e-14,rtol=0)):
            raise RuntimeError('homogeneous property output is nonfinite or at a different composition')
        result[output]=values
    result['actual_x']=actual
    return result


def binary_equilibrium(T: Any,z: Any,variant: str='I2') -> dict[str,Any]:
    """One-mole closed equilibrium with explicit phases and interaction override.

    Empty output slots are not physical regions. Nonempty zero-amount phases
    have no reported active composition. Audit finite energy/nonnegative amounts
    and both component balances. This audit alone is not a global-optimum proof;
    fixed-contract comparisons provide the stated numerical checks.
    """
    t,z=_temperature(T),_scalar_composition(z)
    if variant not in ('I2','R1'):
        raise ValueError('variant must be I2 or R1')
    phases=['ALPHA','BETA'] if variant=='I2' else ['ALPHA']
    interaction=0. if variant=='I2' else 20000.
    dataset=equilibrium(Database(str(MODEL_PATH)),['A','B'],phases,
        {v.T:t,v.P:100000,v.N:1,v.X('B'):z},parameters={'LZERO':interaction},calc_opts={'pdens':2000})
    energy=float(np.asarray(dataset.GM).squeeze())
    names=np.asarray(dataset.Phase).ravel();fractions=np.asarray(dataset.NP).ravel()
    compositions=np.asarray(dataset.X.sel(component='B')).ravel()
    regions=[]
    for phase,f,x in zip(names,fractions,compositions):
        if not phase:
            continue
        if phase not in phases or not np.isfinite(f) or f<0:
            raise RuntimeError('invalid active phase/amount in equilibrium output')
        if f==0:
            continue
        if not np.isfinite(x) or not 0<=x<=1:
            raise RuntimeError('invalid active equilibrium composition')
        regions.append({'phase':str(phase),'x':float(x),'f':float(f)})
    if (not np.isfinite(energy) or not regions
        or abs(sum(r['f'] for r in regions)-1)>1e-8
        or abs(sum(r['f']*r['x'] for r in regions)-z)>1e-8
        or abs(sum(r['f']*(1-r['x']) for r in regions)-(1-z))>1e-8):
        raise RuntimeError('failed/nonfinite or unbalanced equilibrium output')
    return {'GM':energy,'regions':regions,'variant':variant,'omega_J_per_mol':interaction,
            'allowed_phases':phases,'pdens':2000,'requested_z':z}
