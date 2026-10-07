# Lesson 14 — two compatible synthetic boundary states

Meetings 32–33. Use the [two-state contract](boundary_two_state_contract.md), [Lesson 13's closed inventory](lesson_13_finite_reservoir.md), [worksheet](lesson_14_worksheet.md) and [instructor guide](../instructor/lesson_14_guide.md). All structures and parameters here are invented.

**Exit goal:** minimize each structural state's energy at the **same fixed cell inventory**, compare compatible total energies, locate and test a model ordering switch, and explain why this does not establish a real interface phase transition.

## 14A — align what is compared

Keep 8000 bulk sites and two equivalent boundaries of 100 sites and 20 nm² **each**, all at 1000 K and 100000 Pa. For every chosen starting bulk fraction $x_0$, initially put $\theta_0=0.25$ on both boundaries. The closed cell then contains $B_{\rm tot}=8000x_0+50$ B atoms. State I and State II are alternative structures for **both** equivalent boundaries at that same total B. They need not end at the same boundary occupancy or final bulk $x_b$, because each structure can redistribute B while keeping the total fixed.

Both states use the same [binary-family ideal ALPHA](binary_family_contract.md) bulk and site entropy, number of sites, hydrostatic conditions, and energy zero. Their boundary-site energies differ only through an invented baseline $\eta_i$ and B preference $\delta_i$:

$$g_{s,i}(\theta)=g_b(\theta)+\eta_i+\delta_i\theta.$$

| State | Baseline $\eta_i$ | B preference $\delta_i$ |
|---|---:|---:|
| I | 0 J/mol boundary sites | −5000 J/mol boundary sites |
| II | +2000 J/mol boundary sites | −10000 J/mol boundary sites |

State II pays a structural baseline but favors B more strongly. Neither parameter is fitted or measured. A baseline in J/mol **boundary sites** adds $200\eta_i/8200$ J/mol **all cell sites** to the closed objective, or $200\eta_i/N_{\rm Av}$ J to this cell. The baseline is included on the same reference before comparing states. If it were omitted, the low-B ordering would reverse and II would wrongly be selected.

For each state, use the [closed-cell constrained total energy](boundary_closed_contract.md), with $x_b=(B_{\rm tot}-200\theta)/8000$, and find that state's minimum. Call the minimized energies $\bar g_I^*$ and $\bar g_{II}^*$ in J/mol of all cell sites. Compare $D=\bar g_{II}^*-\bar g_I^*$ **only at one $x_0$ at a time**. Positive $D$ favors I among these two uniform-state candidates; negative $D$ favors II. Changing $x_0$ changes total B, so values at two different $x_0$ are separate closed cells.

### Worked comparison

At $x_0=0.10$, both states use total B=850. State I minimizes near $\theta_I=0.17160752$, $x_{b,I}=0.10195981$, $\bar g_I^*=-10541.72679$ J/mol all sites. State II minimizes near $\theta_{II}=0.26898261$, $x_{b,II}=0.09952543$, $\bar g_{II}^*=-10519.50695$ in the **same** basis, including its +2000 J/mol-boundary-site baseline. Thus $D\approx+22.21984$ J/mol all sites and I is lower. For I, bulk B$\approx815.6785$ and boundary B$\approx34.3215$; for II, bulk B$\approx796.2035$ and boundary B$\approx53.7965$. Each pair sums to 850. Holding a common final $x_b$ for both would break at least one balance.

At $x_0=0.25$, each state has total B=2050. State I has $\theta_I\approx0.37428127$ and $\bar g_I^*\approx-10713.32958$; State II has $\theta_{II}\approx0.51703770$ and $\bar g_{II}^*\approx-10718.80845$ J/mol all sites. Now $D\approx-5.47887$, so II is lower among the two alternatives. Comparing both at the **unminimized** starting $\theta=0.25$ would give the wrong ordering here. The [small code route](boundary_two_state.py) reuses Lesson 13's direct minimum and exchange-root check for both states.

## 14B — locate, challenge and limit the switch

Since $D(0.10)>0$ and $D(0.25)<0$, a crossing lies between those starting bulk fractions. The bracketed result is $x_0\approx0.21618678$, where $D$ is numerically zero. The two state occupancies remain distinct: $\theta_I\approx0.332074$ and $\theta_{II}\approx0.470497$. Equality of two **constrained uniform-state branch energies** does not make occupancies equal, and this calculation supplies no mixed-boundary domain energy or kinetic path.

The crossing is unique within the declared $x_0\in[0.10,0.90]$ model. State II's more negative preference selects higher $\theta$ at any fixed total B, so its final bulk fraction is lower than State I's. The ideal bulk exchange slope rises with bulk B fraction. By the envelope derivative, increasing total B therefore lowers $D$ strictly. A 17-point scan checks the ordering numerically; the derivative argument explains why there is at most one switch in this model. A scan alone would not prove uniqueness between samples.

Probe one invented uncertainty: change **only** State II's baseline by $\pm100$ J/mol boundary sites. At a fixed $x_0$, $D$ shifts exactly by $200(\pm100)/8200=\pm2.43902$ J/mol all sites, while each state's optimum occupancy stays unchanged. The crossing moves to $x_0\approx0.20187111$ for $\eta_{II}=1900$ and $x_0\approx0.23094775$ for $\eta_{II}=2100$. The bracket still holds. This is sensitivity to a chosen model number, not a confidence interval for a material.

## Paper route and optional code check

For a paper route, use the **supplied minimized** state values above and in the worksheet. Verify the common B total, convert the baseline to the all-site basis, subtract energies with units, and bracket the sign change. Derive the direction of the baseline sensitivity and the monotonicity argument without running a solver. Those are the scientific decisions the code must respect. For an optional exact check in this project's Poetry environment:

```python
from course.foundations.boundary_two_state import compare_states, crossing

for x_initial in (0.10, 0.25, 0.50):
    pair = compare_states(x_initial)
    print(x_initial, pair["difference_J_per_mol_sites"])
for eta_II in (1900, 2000, 2100):
    print(eta_II, crossing(eta_II)["x_initial"])
```

The model has no atomistic structure, measured excess, interface junction or evidence of coexisting real boundary phases. The [Frolov–Mishin interface-phase theory](https://arxiv.org/abs/1506.08890) treats physical excesses and coexistence conditions that are outside this toy branch comparison.
