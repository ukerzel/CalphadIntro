# Lesson 9 worksheet — one parameter, fixed observable

Use [reading](lesson_09_fitting.md). Synthetic homogeneous ALPHA,1000 K,100000 Pa,
J/mol of atoms. Paper/calculator is sufficient. Keep held-out predictions separate
from training work, and keep instructor answers hidden before the attempt.

## Meeting 21

**A1 — worked residuals.** Reproduce the x=.1,.3,.5 rows for trial Ω=18000. Label
prediction, observation, residual and squared-residual units. Complete the two
reflected rows and add the squared objective. Why not minimize the residual sum?

**A2 — guided second trial.** Try Ω=16000. Give predictions/residuals at all five
training points and its objective. Compare Ω=18000, 20000, 22000. Do bounds alone
establish the correct parameter?

**A3 — independent-variable diagnostic.** In equilibrium, what varied? In this
fit, what varies and what remains supplied/fixed? Is changing each observation's
composition until its energy decreases a valid parameter fit?

**A4 — independent exit.** Given ∑ai²=.1669 and ∑aihi=3338 J/mol, calculate Ω*. State
its units, whether bounds are active, and what property/reference the residual uses.
Does recovering the known value establish experimental alloy accuracy?

## Meeting 22

**B1 — worked forward-model swap.** At 1000 K, x=.5, a tool gives total homogeneous
H=12000 J/mol for Ω=20000. Subtract the reference and compare to the declared training
observation. Then use the equilibrium-mixture hmix=2810.686236 instead. Quantify
the error and identify the invalid API/observable choice.

**B2 — guided held-out check.** With Ω fixed at 20000 after fitting, predict hmix at
x=.2,.4,.6,.8. Compare with the stored row. What must happen if an error is found?
Can one repeatedly tune Ω using these points and still call them untouched held-out data?

**B3 — guided missing sensitivity.** If the only observations are pure x=0 and 1,
what prediction follows for Ω=0, 12000, 24000? Why is the parameter not identifiable?
For the optional (A+BT)x(1−x) excess G, show why homogeneous H cannot determine B.

**B4 — independent fresh example.** For a separate noiseless homogeneous toy
observation at x=.25, hmix=3750 J/mol, infer Ω from one equation. Predict at x=.4
without fitting again. If a second unknown entropy coefficient B is introduced,
can this enthalpy point determine it? Distinguish recovery, same-model verification
and material validation in one sentence each.
