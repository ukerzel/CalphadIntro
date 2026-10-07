"""Visible unary Gibbs comparison: NumPy arithmetic and SciPy optimization.

Synthetic one-mole bulk model at 100000 Pa, 800–1200 K only. See
one_component_contract.md and Lesson 0. Numerical methods:
https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html
https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.brentq.html
"""

from pathlib import Path

import numpy as np
from scipy.optimize import brentq, linprog


def checked_temperatures(temperature: float | list[float] | np.ndarray) -> np.ndarray:
    """Accept a finite scalar or nonempty 1-D array in the teaching interval."""
    t = np.asarray(temperature, dtype=float)
    if t.ndim > 1 or t.size == 0 or not np.all(np.isfinite(t) & (t >= 800) & (t <= 1200)):
        raise ValueError('use finite temperatures from 800 to 1200 K, scalar or 1-D array')
    return t


def gibbs(temperature: float | list[float] | np.ndarray) -> np.ndarray:
    """Return [g_SOLID, g_LIQUID] in J/mol for each input temperature in K."""
    t = checked_temperatures(temperature)
    solid = 1000.0 - 10.0 * t
    liquid = 7000.0 - 16.0 * t
    return np.stack([solid, liquid], axis=-1)


def transition_temperature() -> float:
    """Find the crossing by a bracketed root; these fixed lines change sign."""
    return brentq(lambda t: gibbs(t)[1] - gibbs(t)[0], 800, 1200, xtol=1e-10)


def equilibrium_at(temperature: float) -> dict:
    """Minimize total molar G over nonnegative balanced phase fractions.

    At the crossing, the returned fractions are one arbitrary minimizer.
    Reject arrays and report solver failure instead of reading failed outputs.
    """
    energies = gibbs(temperature)
    if energies.ndim != 1:
        raise ValueError('equilibrium_at needs one scalar temperature')
    solution = linprog(energies, A_eq=[[1, 1]], b_eq=[1],
                      bounds=[(0, 1), (0, 1)], method='highs')
    if not solution.success:
        raise RuntimeError(solution.message)
    return {'GM': float(solution.fun),
            'fractions': {'SOLID': float(solution.x[0]), 'LIQUID': float(solution.x[1])}}


def save_figure(path: Path) -> None:
    """Plot the declared model and fraction objective; save an original SVG."""
    import matplotlib.pyplot as plt

    with plt.rc_context({'svg.hashsalt': 'unary-course', 'svg.fonttype': 'none'}):
        fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), layout='constrained')
        t = np.linspace(800, 1200, 201)
        values = gibbs(t)
        axes[0].plot(t, values[:, 0], label='SOLID: 1000 − 10T')
        axes[0].plot(t, values[:, 1], label='LIQUID: 7000 − 16T')
        axes[0].axvline(1000, color='0.5', linestyle=':')
        axes[0].scatter([1000], [-9000], color='black', zorder=3)
        axes[0].set(xlabel='Temperature (K)', ylabel='Molar Gibbs energy (J/mol)',
                    title='1. Compare the two phases')
        f = np.linspace(0, 1, 101)
        for temperature in [900, 1000, 1100]:
            solid, liquid = gibbs(temperature)
            axes[1].plot(f, (1-f)*solid+f*liquid, label=f'{temperature} K')
        axes[1].set(xlabel='Liquid mole fraction fL', ylabel='Mixture Gibbs energy (J/mol)',
                    title='2. Vary the phase amounts')
        for ax in axes:
            ax.legend(fontsize=9)
            ax.grid(alpha=0.2)
        fig.suptitle('Invented one-component model · p = 100000 Pa · no material prediction')
        fig.savefig(path, metadata={'Date': None})
        plt.close(fig)


def main() -> None:
    """Print the visible comparison; no database or CALPHAD library is used."""
    print('T(K)   g_SOLID   g_LIQUID   g_equilibrium  (all energies J/mol)')
    for t in [800, 900, 1000, 1100, 1200]:
        solid, liquid = gibbs(t)
        print(f'{t:4d} {solid:9.1f} {liquid:10.1f} {equilibrium_at(t)["GM"]:15.1f}')
    print(f'Crossing temperature = {transition_temperature():.6f} K')
    print('At 1000 K the phase fractions are not uniquely determined.')


if __name__ == '__main__':
    main()
