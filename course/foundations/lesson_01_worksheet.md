# Lesson 1 worksheet — predict, calculate, then minimize

Meetings 04–05.
Use the [Lesson-1 reading](lesson_01_one_component.md) and
[setup instructions](README.md#running-the-examples). Bring the Lesson-0 exit
tasks. First explain why fixed temperature and pressure call for Gibbs energy,
and why equal amounts matter. Revisit those ideas before proceeding if needed.
The [instructor guide](../instructor/lesson_01_guide.md) supplies hints and answers.

No installation is required for the paper route: fill the tables, draw the
lines, annotate the supplied calls and compare with the instructor's printed
answer tables. A demonstration or saved answer is not a calculation you ran.

## The model card — keep beside every calculation

One invented component A; closed bulk system; one mole of atoms;
$p=100000$ Pa; $800\le T\le1200$ K. Only SOLID and LIQUID are allowed.
$g$ means molar Gibbs energy in J/mol; $h$ is molar enthalpy in J/mol;
$s$ is molar entropy in J/(mol K).

| Phase | h | s | g=h−Ts |
|---|---:|---:|---|
| SOLID | 1000 | 10 | 1000−10T |
| LIQUID | 7000 | 16 | 7000−16T |

Constant h,s imply zero heat capacity inside each modeled phase. No interfaces,
kinetics, other pressures or real-material predictions are represented.
The [retained contract](one_component_contract.md) fixes domain and checks.

## Meeting 04 — a phase comparison before an optimizer

**D1 — worked recall.** At 900 K, $g_S=1000-900(10)=-8000$ J/mol and
$g_L=7000-900(16)=-7400$ J/mol. Define $\Delta g=g_L-g_S$:
here $\Delta g=+600$ J/mol, so SOLID is lower. The subscripts name the phases.
Predict whether increasing T makes $\Delta g$ increase or decrease.

**D2 — guided table and plot.** Complete the table by hand before running
the first code cell. Include both phase values even when one is higher.

| T, K | gS, J/mol | gL, J/mol | Δg, J/mol | Lower phase, or tie |
|---:|---:|---:|---:|---|
| 800 | … | … | … | … |
| 900 | −8000 | −7400 | 600 | SOLID |
| 1000 | … | … | … | … |
| 1100 | … | … | … | … |
| 1200 | … | … | … | … |

On paper, put T on the horizontal axis and g on the vertical axis. Label their
units. Plot both branches, connect each set of points, and mark the crossing.
Explain what would be hidden by plotting only the lower value.
The [existing figure](figures/one_component_gibbs.png) is available after your
attempt; use its left panel now.

For the computer route, run these Python cells in order in one session from
the repository root. An array is a list of numbers that NumPy can calculate
with together. Multiplication is written as *. The comments record units.

~~~python
import numpy as np

temperatures = np.array([800., 900., 1000., 1100., 1200.])  # K
solid = 1000. - 10.*temperatures                          # J/mol
liquid = 7000. - 16.*temperatures                         # J/mol
gap = liquid - solid                                    # J/mol
table = np.column_stack([temperatures, solid, liquid, gap])
print(table)
~~~

Each row should agree with your hand table. Explain the sign of the last
column in words rather than treating a negative value as an error.

**D3 — a root, not a fit.** A root is where a function becomes zero.
Use $\Delta g=6000-6T$. Check its signs at 800 and 1200 K, solve
$6000-6T=0$ by hand, and only then run:

~~~python
from scipy.optimize import brentq

def difference(T):
    return (7000. - 16.*T) - (1000. - 10.*T)

crossing = brentq(difference, 800., 1200.)
print(crossing)
~~~

The two temperatures bracket a root of this continuous function because its
sign changes. The function returns a difference for a supplied T.
The coefficients 1000, 7000, 10 and 16 are fixed; no measurements are being fitted.
Predict whether the bracket 800–900 K would work before trying it.

**D4 — independent exit.** At 950 K compute both g values and their difference.
State the favored phase, conditions and units; explain why the larger liquid
entropy can reverse the ordering as T increases. Does a crossing tell you how
fast a specimen melts?

## Meeting 05 — make the allowed choices explicit

**E1 — worked mixture.** $f_L$ is the fraction of atoms in liquid and
$f_S=1-f_L$ the fraction in solid. These dimensionless fractions are not
automatically volume or image-area fractions.
Their allowed range is 0–1 and their sum is 1.
For our phase mixture,

$$g_{\mathrm{mix}}=(1-f_L)g_S+f_Lg_L.$$

There is only one component, so this is not compositional mixing of different
elements. Interface energy is omitted.
At 900 K and $f_L=0.25$, $g_{\mathrm{mix}}=-8000+600(0.25)=-7850$ J/mol.
With one mole total, $G_{\mathrm{total}}=1\ \mathrm{mol}\times g_{\mathrm{mix}}$.

**E2 — guided trial fractions.** Fill all three energy columns using the same
two phase equations. Predict whether each column rises, falls or stays flat.

| fL | gmix at 900 K, J/mol | gmix at 1000 K, J/mol | gmix at 1100 K, J/mol |
|---:|---:|---:|---:|
| 0 | … | … | … |
| 0.25 | −7850 | … | … |
| 0.5 | … | … | … |
| 0.75 | … | … | … |
| 1 | … | … | … |

Choose a minimum in each column. State whether that choice is unique.
Consult the existing figure's right panel after explaining your table.

**E3 — annotate an equilibrium call.** An objective is the quantity minimized;
variables are the numbers the solver may choose; constraints limit those choices.
Below the variables are [fS, fL]. On paper circle the two energy coefficients,
underline the amount balance, and box the physical bounds. Explain each before
running the code. It is self-contained apart from the installed SciPy package.

~~~python
from scipy.optimize import linprog

answer = linprog(
    c=[-8000., -7400.],         # coefficients of fS and fL, J/mol
    A_eq=[[1., 1.]],           # fS + fL
    b_eq=[1.],                 # must equal 1
    bounds=[(0., 1.), (0., 1.)],
    method="highs",
)
if not answer.success:
    raise RuntimeError(answer.message)

print(answer.x)                # [fS, fL]
print(answer.fun)              # minimum molar Gibbs energy, J/mol
~~~

Change only the two coefficients to calculate the 1100 K problem.
Check success, each fraction's bounds, their sum and the energy against E2.
At 1000 K use [-9000., -9000.] and explain why different valid fractions
can agree physically. Do not require a particular solver choice there.

**E4 — diagnose a lower number.** Someone substitutes $f_L=-0.2$ at 900 K
and reports −8120 J/mol, lower than the solid. Check the arithmetic and explain
why it is not an equilibrium state. Someone else says that two different
fractions from two solvers at 1000 K establish a disagreement. Name the checks
needed before deciding.

**E5 — independent exit.** At 1050 K calculate both branch energies,
the energy for $f_L=0.4$, and the equilibrium choice.
Write the objective, variables and constraints in words or symbols.
Explain how changing phase amounts differs from fitting h or s.

## Handback

Keep D4 and E5 with your units and explanations. Also explain why every allowed
fraction at 1000 K has the same energy. Revisit unfinished parts before
[Lesson 2](lesson_02_same_model_pycalphad.md), which changes the representation
of this exact model.
The reading's [primary sources](lesson_01_one_component.md#sources) explain
the numerical interfaces and broader CALPHAD method; the model is original.
