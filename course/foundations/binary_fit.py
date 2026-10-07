"""Lesson 9: one homogeneous ALPHA mixing-enthalpy parameter at fixed 1000 K.

The same declared observable/reference is used for plain and tool routes.
Bounds/data interpretation follow binary_family_contract.md. No equilibrium
property, held-out data, noise inference or material assessment is implicit.
"""
from typing import Any
import numpy as np
from scipy.optimize import least_squares
from course.foundations.binary_family import _composition,_interaction,regular_properties
from course.foundations.binary_family_tools import homogeneous_properties


def predict_hmix(omega: Any,x: Any,route: str='plain') -> np.ndarray:
    """Homogeneous HM minus the same-phase weighted pure HM, in J/mol atoms."""
    interaction,value=_interaction(omega),_composition(x)
    if route=='plain':
        hm=regular_properties(1000,value,interaction)['HM']
    elif route=='tool':
        hm=homogeneous_properties(1000,value,'ALPHA',interaction)['HM']
    else:
        raise ValueError('route must be plain or tool')
    return np.asarray(hm-(1000+12000*value))


def fit_interaction(x: Any,h_mix: Any,route: str='plain') -> dict[str,Any]:
    """Unweighted bounded least squares using supplied training data only.

    One-dimensional equally sized finite arrays are required, with at least
    one interior composition to identify omega. Returned residuals/objective
    must still be checked; optimizer success does not establish a good model.
    Held-out values are intentionally absent from this interface.
    """
    value=_composition(x);observed=np.asarray(h_mix,dtype=float)
    if value.ndim!=1 or observed.shape!=value.shape or not np.all(np.isfinite(observed)):
        raise ValueError('training x and h_mix must be equal nonempty finite 1D arrays')
    if not np.any((value>0)&(value<1)):
        raise ValueError('endmember-only data have zero sensitivity to omega')
    if route not in ('plain','tool'):
        raise ValueError('route must be plain or tool')
    result=least_squares(lambda p:predict_hmix(p[0],value,route)-observed,[12000.],
                         bounds=([0.],[24000.]),xtol=1e-12,ftol=1e-12,gtol=1e-12,max_nfev=100)
    if not result.success:
        raise RuntimeError('interaction fit failed: '+str(result.message))
    omega=_interaction(result.x[0])
    predictions=predict_hmix(omega,value,route);residuals=predictions-observed
    with np.errstate(over='ignore',invalid='ignore'):
        sse=float(residuals@residuals)
    if not np.isfinite(sse):
        raise RuntimeError('nonfinite fit objective')
    return {'omega':omega,'route':route,'T_K':1000.,'training_x':value.tolist(),
            'observed_H_mix':observed.tolist(),'predicted_H_mix':predictions.tolist(),
            'residuals_J_per_mol':residuals.tolist(),'sse':sse,'sse_units':'(J/mol)^2',
            'nfev':int(result.nfev),'solver_status':int(result.status)}
