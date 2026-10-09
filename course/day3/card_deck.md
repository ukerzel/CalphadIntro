# Advanced steps 07–18: the card deck

Short answers to “hang on, what was this?”. Cards marked “Core” are the ones most steps need. Cut along the rules.

---

### Core · Hang on: what was the lever rule?

*both decks · needed for steps 03, 07, 10, LP*

A split must keep every atom. If a sample at overall B fraction $z$ splits into a state at $x_1$ and one at $x_2$, the amounts obey $f_1+f_2=1$ and $f_1x_1+f_2x_2=z$. Solving gives $f_2=(z-x_1)/(x_2-x_1)$: the state nearer to $z$ gets more. On the step 10 menu, SOLID at 0.5 and LIQUID at 0.3 make $z=0.40$ with 0.5 each, because $z$ lies halfway between them.

Where you met it: step 03 part A.

*You don't need more than this to continue.*

---

### Core · What is a common tangent?

*both decks · needed for steps 03, 07, 09, 12*

A straight line that touches two curves, or the same curve twice, without crossing either. Where it touches, the two states have the same $\mu_A$ and $\mu_B$ (its end heights), so they can coexist. Between the touching points the line is the lowest energy any mixture can reach. On the lens at 1400 K it touches LIQUID at 0.312 and SOLID at 0.441, with $\mu_A=-19760.0$ and $\Delta\mu=-1782.8$ J/mol atoms.

Where you met it: step 03 part A (or the printable two-phase sheet).

*You don't need more than this to continue.*

---

### What is a parallel tangent?

*both decks · needed for steps 04, 07, 14*

Take the line at your sample's composition and slide it down, keeping its tilt, until it just touches another curve (or another part of the same curve). That touching line is the parallel tangent. The vertical distance between the two lines is the largest bulk driving force for forming that other state. Step 14 uses the same move for the floor: the line slid down by the deepest dip.

Where you met it: step 04, where the reservoir line and the boundary curve meet the same way.

*You don't need more than this to continue.*

---

### Core · What is a driving force?

*both decks · needed for steps 12, 15, 17*

For a phase model, the driving force is how far its deepest point lies below the current line: minus the lowest value of its gap curve (in optimisation words, minus the reduced cost). Positive means a state of that phase would lower the energy if it formed (when only one line fits the used dots; step 15). Some programs divide it by $RT$. It is a bulk quantity: it says which composition gains most per mole, not the composition of a critical nucleus, which also depends on interface and elastic energy.

*You don't need more than this to continue.*

---

### Core · Which model am I in?

*both decks · needed for steps 10, 15*

The advanced steps use two invented models, both from step 03.

- Steps 10–14: the melting lens at 1400 K, $z=0.40$. Ideal SOLID and LIQUID; A from step 01 and an invented B (solid $2000-10T$, liquid $20000-20T$ J/mol).
- Steps 15–17: the regular solution at 800 K, $z=0.15$. Step 02's ALPHA with its own B ($13000-10T$) plus $\Omega x(1-x)$, $\Omega=20000$ J/mol.

The two B components are different elements. Temperatures so far: step 01 800–1200 K, step 02 1000 K, then 1400 K and 800 K here; A's lines are used beyond 1200 K as a declared extension.

Where you met it: step 03 part C and part B.

*You don't need more than this to continue.*

---

### Is f the same as pycalphad's NP?

*both decks · needed for steps 05, 06, 10*

Almost. $f$ is a state's amount in moles of atoms per mole of sample; pycalphad's NP is the same kind of number for one phase (one vertex). In step 05 the two FCC_A1 vertices each have their own NP, and the NP values add to 1. On a grid (step 10) two neighbouring dots of one phase model can share one phase's amount: their two $f$ values then add up to that phase's NP. The amounts add to 1, and $\sum f x=z$.

*You don't need more than this to continue.*

---

### Why is the line from a grid not a floor for the whole curve?

*both decks · needed for steps 12, 14*

The master's line lies on or below every dot of the menu, so it is a floor for mixtures of those dots only. Between the dots the continuous curve can dip below the line: on the lens, SOLID near $x=0.4489$ lies 61.2 J/mol atoms under the step 10 line. To get a floor for every state, slide the line down by the deepest dip of the whole curve.

*You don't need more than this to continue.*

---

### Does my CALPHAD code do this too?

*both decks · needed for step 13*

Yes, in three stages. pycalphad 0.11.2 first samples states of every phase and solves a linear programme over them: the menu and line of steps 10–11. Then a Newton-type solver moves the compositions of the phases in use off the grid and returns new chemical potentials. Then it checks every sampled state against the new line and adds the phase with the largest driving force, for up to ten rounds: column generation with the grid as the search set. With many elements the grid gets sparse, so a valley between sampled points can be missed; a denser grid costs more energy evaluations.

*You don't need more than this to continue.*

---

### What are objective, variables and constraints?

*maths and optimisation · needed for steps 01, 03, 10, LP*

An optimisation problem has three parts. The variables are what you may choose: here the amounts $f$ of each dot on the menu. The objective is what you make as small as possible: the total energy $\sum f g$. The constraints, written after "subject to", are rules every choice must obey: no amount is negative, the amounts add to 1, and the B atoms add to $z$. A choice that obeys every constraint is feasible; any feasible choice with the lowest objective is optimal, and there can be more than one. The optional LP primer works through one example.

*You don't need more than this to continue.*

---

### What does Σ mean?

*maths and optimisation · needed for steps 05, 06, 07, 10, LP*

$\sum_j f_jg_j$ is shorthand for "multiply each dot's amount by its energy, then add them all up". The small $j$ counts the dots: $f_1g_1+f_2g_2+\dots$ For the step 10 answer only two amounts are not zero, so the sum is $0.5\times(-20568.44)+0.5\times(-20290.64)=-20429.54$ J/mol atoms.

*You don't need more than this to continue.*

---

### Core · How do I read a line μA + Δμ·x?

*maths and optimisation · needed for steps 11, LP*

A straight line on the $g$–$x$ plot is fixed by two numbers. Its height at $x=0$ is $\mu_A$. Its slope $\Delta\mu$ is how much it rises from $x=0$ to $x=1$, so its height at $x=1$ is $\mu_B=\mu_A+\Delta\mu$. At any $x$ the height is $\mu_A+\Delta\mu\,x$. The line of the step 10 menu (read in step 11) has $\mu_A=-19873.9$ and $\Delta\mu=-1389.0$, so at $z=0.40$ its height is $-19873.9-1389.0\times0.40=-20429.5$ J/mol atoms.

Where you met it: step 02, where the tangent's end heights were $\mu_A$ and $\mu_B$.

*You don't need more than this to continue.*

---

### What are a slope and a derivative?

*maths and optimisation · needed for steps 02, 11, 12*

The slope of a straight line is its rise divided by its run: between the two dots of step 11 it is $(-20568.44+20290.64)/0.2=-1389.0$. A curve has a different slope at every point. Its derivative $\mathrm{d}g/\mathrm{d}x$ is the slope of the tangent there, the line that just touches the curve. You never compute one in the advanced steps: every slope you need is printed.

*You don't need more than this to continue.*

---

### Why does a split's energy lie on a straight line?

*maths and optimisation · needed for steps 03, 07, 10, LP*

The energy of a split, per mole of atoms of the sample, is the amount-weighted sum $G=f_1g_1+f_2g_2$. As $z$ moves from $x_1$ to $x_2$ the amounts change in proportion (the lever rule), so $G$ moves along the straight line, the chord, joining the two dots. Every mixture of two dots lies on its chord, and the cheapest mixture at $z$ is the chord whose height at $z$ is lowest.

Where you met it: step 03 (or the printable two-phase sheet, part 3).

*You don't need more than this to continue.*

---

### Core · Why is the line a floor and my best mixture a ceiling?

*maths and optimisation · needed for steps 11, 14*

Any mixture you can actually make is a real candidate, so the true lowest energy is at or below it: a ceiling. Now take a line on or below every dot of the menu. Every mixture of those dots lies on a chord between dots, so it lies on or above the line too: at $z$, the line's height is a floor for these dots. On the step 10 menu floor and ceiling meet at $-20429.54$. The floor holds only for these dots: a state between them can still be lower.

*You don't need more than this to continue.*

---

### What is a dual, or a shadow price?

*maths and optimisation · needed for step 11*

A linear programme comes with one extra number per constraint row, its dual or shadow price: how much the best energy changes when that row's right-hand side changes a little, as long as the same dots stay in use. Where the used dots change (z on a dot), the rates left and right differ. The master of steps 10–11 has two rows, "amounts add to 1" and "B atoms add to $z$". Their prices are the line's $\mu_A$ and $\Delta\mu$. Nudge $z$ by 0.01 on the step 10 menu and the energy changes by $\Delta\mu\times0.01=-13.9$ J/mol atoms.

*You don't need more than this to continue.*

---

### Why do the floor and the ceiling meet?

*maths and optimisation · needed for step 11*

For the step 10 menu the highest floor line at $z$ and the lowest mixture give the same number, $-20429.54$. This is strong duality: a linear programme that has a solution has a twin problem, here "the highest line under all dots", with the same optimal value. For other convex problems the twins meet only under extra conditions, and for non-convex problems not in general. The advanced steps use it for the menu, and step 09 for the continuous curves (a linear programme with infinitely many columns), where it also holds here.

*You don't need more than this to continue.*

---

### Core · What is a reduced cost?

*maths and optimisation · needed for steps 12, 13*

Take the master's line and subtract its height from each state's energy: $g(x)-(\mu_A+\Delta\mu\,x)$. That difference is the state's reduced cost; drawn for every $x$ it is the gap curve of step 12. Used dots sit at zero. A dot strictly above the line is not used. When only one line fits the used dots, a state below it would lower the energy if added (when z sits on a used dot at a kink of the envelope, several lines fit: step 15): against the step 10 line, SOLID near $x=0.4489$ sits 61.2 J/mol atoms below.

*You don't need more than this to continue.*

---

### What is the lower envelope?

*maths and optimisation · needed for steps 09, 12*

Draw every state of every phase model as a dot, then pull a string up tight under all of them from $x=0$ to $x=1$. The string's shape is the lower convex envelope (the lower part of the convex hull). At each $z$ its height is the lowest energy any mixture can reach. Where the string follows a curve the sample is one phase; where it is straight, it spans two touching points: a split.

*You don't need more than this to continue.*

---

### Core · What is column generation?

*maths and optimisation · needed for steps 13, 18*

Instead of listing every possible state, start with a small menu and repeat:

- find the cheapest mixture of the menu and its line (the master);
- look for the state deepest below that line (the pricing step: the deepest dip of the gap curve);
- if nothing lies below, stop: the line is a floor for every state;
- otherwise add that state to the menu and start again.

In LP words each menu state is a column. On the lens, the remaining uncertainty after each round falls $61.18\to3.99\to1.55\to0.0027$ J/mol atoms.

*You don't need more than this to continue.*

---

### Core · How do ceiling, floor and remaining uncertainty fit together?

*maths and optimisation · needed for steps 14, 17*

Draw one number line for the energy at $z$. The ceiling (the best mixture found) is a mark at or above the truth; the floor (the line slid down by the deepest dip) is a mark at or below it. The truth lies between them, and their distance is the remaining uncertainty. For the step 10 menu: ceiling $-20429.54$, floor $-20490.72$, so at most 61.2 J/mol atoms are left. It measures how far you may be from the declared model's minimum, not how good the model is.

*You don't need more than this to continue.*

---

### Core · What is the difference between a local and a global minimum?

*maths and optimisation · needed for step 15*

On the gap curve, a local minimum is lower than everything near it; the global minimum is the lowest point of the whole curve. A search that only walks downhill from where it starts stops at the first local minimum it meets. Against the tangent at 0.15, the regular solution's gap curve is zero at 0.15 and dips to $-2082.0$ near 0.958: a downhill walk from 0.15 stays put and misses the deeper valley.

*You don't need more than this to continue.*

---

### What is a grid, and what can it miss?

*maths and optimisation · needed for steps 03, 10, 13*

A grid is a list of compositions at which each phase model is evaluated, like the step 10 menu 0.1, 0.3, 0.5, 0.7, 0.9. The solver can only mix the dots it has, and a state between grid points may be lower than every mixture of them. Step 03 part D's coarse grid gives $-20434.06$ at $z=0.40$, while the true answer is $-20473.12$. A finer grid helps only if it puts a dot near the true compositions.

Where you met it: step 03 part D.

*You don't need more than this to continue.*

---

### What if the answer is not unique?

*maths and optimisation · needed for steps 10, 11*

Two different things can be non-unique.

- Several optimal amounts: if a third dot lies exactly on the line, many mixtures give the same energy. In step 01, at the melting point 1000 K, solid and liquid have the same energy and every split ties.
- A line that can rotate: if $z$ sits exactly on a used dot at a corner of the envelope, many lines touch there. The energy is unique, but $\mu_A$ and $\Delta\mu$ are not. Step 03 part D's coarse grid is such a case.

*You don't need more than this to continue.*

---

### What are a relaxation, a floor and an underestimator?

*maths and optimisation · needed for step 16*

A relaxation is an easier problem whose answer can only be lower: you allow more, or you replace a hard curve by one that lies below it. Its answer is a floor. An underestimator is such a replacement curve. On an interval, step 16 replaces the regular solution's hump term $\Omega x(1-x)$ by its chord: the new curve lies on or below the true gap curve everywhere on that interval, and its lowest point has a formula.

*You don't need more than this to continue.*

---

### What is an interval [l, u], and why halve it?

*maths and optimisation · needed for step 16*

$[l,u]$ means every composition from $l$ to $u$, ends included. Branch-and-bound starts with $[0,1]$. When it cannot decide an interval, it cuts it at the midpoint into two halves and looks at each again. Smaller intervals give tighter floors: the chord's distance from the curve shrinks with the square of the width.

*You don't need more than this to continue.*

---

### What do prune and incumbent mean?

*maths and optimisation · needed for step 16*

To prune an interval is to cross it out: its floor shows that nothing in it lies deeper than the tolerance, so it never needs another look. The incumbent is the best state actually found so far, here the deepest evaluated point of the gap curve. The search is finished when every interval is pruned; an interval that is neither pruned nor split is still open, and the answer is then "unresolved", not "stable".

*You don't need more than this to continue.*

---

### Why does the computer print −0.0 or 1e-9?

*maths and optimisation · needed for steps 14, 16*

Computers store numbers with about 16 significant digits, so results carry tiny rounding errors. A printed $-0.0$, $3\times10^{-10}$ or $-1.5\times10^{-9}$ J/mol atoms means zero within rounding. A tolerance says how small is small enough: the branch-and-bound of step 16 uses $\varepsilon=1$ J/mol atoms, far below the model's own uncertainty, and does not chase dips shallower than that.

*You don't need more than this to continue.*

---

### What is a checkable answer?

*maths and optimisation · needed for steps 16, 17*

A checkable answer lets anyone confirm the result without trusting the solver: a mixture that makes the sample (its energy is the ceiling), a line, and a list of intervals covering $[0,1]$. A short separate program recomputes every interval's floor from the formula, checks that no part of $[0,1]$ is missing, and compares ceiling minus floor with the tolerance. In ordinary floating point this is a teaching check, not a rigorous proof.

*You don't need more than this to continue.*

---

### Where have I seen this LP before?

*maths and optimisation · needed for steps 03, 10*

Three times already. In step 01 the computer chose the amounts of solid and liquid, non-negative and adding to one: the smallest version, with two dots. In step 03 part D a linear programme mixed a grid of SOLID and LIQUID dots to find the lens split. Notebook f4, section 2, writes the same LP in code for step 03 part A, and notebook f4b, section 5, for the lens. The advanced steps read the same problem again and ask what its extra numbers mean; the optional LP primer starts from scratch.

*You don't need more than this to continue.*

---

### How does this course name LP things?

*thermodynamics · needed for steps 08, 09, 10, 11, 12, 13, 14, 15, 16, LP*

- Variables are the amounts $f_j\ge0$; $x$ and $z$ are compositions, fixed data. SciPy's res.x holds the amounts.
- A master is a restricted master over the listed states: minimise with rows $\sum_jf_j=1$, $\sum_jf_jx_j=z$.
- Prices are SciPy's eqlin.marginals, the change of the optimum per unit right-hand side: $\mu_A$ and $\Delta\mu$.
- Ceiling: the master's value, an upper bound. Floor: a dual lower bound. Ceiling minus floor: the remaining uncertainty (your optimality gap).
- Gap alone: a state's reduced cost; driving force: minus the most negative gap. A miscibility gap is a phase model splitting in two.
- Basis: in the boxes for operations research, the LP basis (the used dots); elsewhere written amount basis. Vertex: pycalphad's word for a phase in use.

*You don't need more than this to continue.*

---

### Which words will I meet in the literature?

*both decks · needed for steps 05, 10, 11, 12, 13, 14, 15, 16, 17, 18*

- Menu: a grid of trial points (pycalphad's density is pdens).
- Two coexisting compositions of one phase model: composition sets (Thermo-Calc's FCC_A1#2).
- Ceiling and floor: upper and lower bounds on the minimum; ceiling minus floor, the remaining uncertainty, is the optimality gap.
- The line under the dots: the tangent line or, with more components, tangent plane; its end heights are the chemical potentials.
- $\Delta\mu=\mu_B-\mu_A$: the exchange (diffusion) potential.
- Gap curve: the tangent-plane distance (Michelsen's stability test); minus its deepest value is the driving force.
- Adding the deepest state: column generation; in CALPHAD codes, global minimisation on a grid with refinement.
- Prices: duals, Lagrange multipliers, shadow prices; here the chemical potentials.

*You don't need more than this to continue.*

---

### How do I read a point on a triangle?

*maths and optimisation · needed for step 18*

With three components a composition has three fractions that add to 1, so it is a point in a triangle with A, B and C at the corners. The fraction of A is the distance from the side opposite A, measured as a share of the triangle's height; the same for B and C. A point on a side has none of the opposite component. The sample $z=(0.50,0.30,0.20)$ lies half-way up from the B–C side, 0.3 of the way from the A–C side and 0.2 from the A–B side.

*You don't need more than this to continue.*

---

### Which symbols and units does the advanced part use?

*thermodynamics · needed for step 08*

- $g(x)$: molar Gibbs energy of one phase model, J/mol atoms;
- $x$: B fraction inside a state; $z$: B fraction of the whole sample;
- $f$: amount of a state, mol atoms per mol sample;
- $\mu_A,\mu_B$: chemical potentials, J per mole of that element's atoms; $\Delta\mu=\mu_B-\mu_A$;
- $\Omega$: interaction energy, J/mol;
- $R=8.3145$ J/(mol K) and $T$ in K: $RT\approx11.6$ kJ/mol at 1400 K and 6.65 kJ/mol at 800 K.

*You don't need more than this to continue.*

---

### What are H and S, in one line each?

*thermodynamics · needed for steps 00, 08*

$H$, the enthalpy, is the energy bookkeeping at fixed pressure; in these models it is mostly bonding energy. It is not "stored heat". $S$, the entropy, counts how many microscopic arrangements fit what you observe: $S=k_B\ln W$. In $G=H-TS$ a higher $S$ lowers $G$, more so at higher $T$: $-TS$ is an entropy bonus.

Where you met it: step 00.

*You don't need more than this to continue.*

---

### Core · Why does a closed system at fixed T and p minimise G?

*thermodynamics · needed for steps 00, 08*

Put the sample in a large heat bath at temperature $T$ and pressure $p$. Heat may cross; atoms may not. The second law says the entropy of sample plus bath cannot fall. Heat $Q$ taken by the sample lowers the bath's entropy by $Q/T$, and at fixed $p$, with only $pV$ work, $Q=\Delta H$. So $\Delta S-\Delta H/T\ge0$, which is $\Delta G\le0$: $G$ of the sample cannot rise. At equilibrium the sample is in its allowed state of lowest $G$; whether and when it gets there is kinetics.

Where you met it: step 00.

*You don't need more than this to continue.*

---

### Why are the numbers negative, and what is zero?

*thermodynamics · needed for step 08*

Only differences of $G$ matter. Each element's zero is a chosen reference, so a value like $-20429.54$ J/mol atoms means nothing alone. Adding the same straight line $a+bx$ to every phase model's curve changes no split and no choice of states; it only shifts $\mu_A$ by $a$ and $\Delta\mu$ by $b$. In optimisation words: adding the same affine function of the constraint rows to every cost moves the optimal value and the duals, not the optimal amounts.

*You don't need more than this to continue.*

---

### Core · What is the difference between a phase, a phase model and a grid state?

*thermodynamics · needed for steps 05, 06, 08, 10*

A phase model is a formula for one structure, for example SOLID or LIQUID, giving a curve $g(x)$. A phase is a uniform region of a real sample, and one phase model can describe two coexisting phases of different composition (a miscibility gap). A grid state is one dot: one phase model at one composition. Two neighbouring dots of the same phase model can together stand for one phase between them, so counting dots is not counting phases.

*You don't need more than this to continue.*

---

### What are a mole of atoms, z, x and f?

*thermodynamics · needed for step 08*

Energies are per mole of atoms, like cost per tonne in blending. $z$ is the B fraction of the whole sample, fixed by what you put in; $x$ is the B fraction inside one state; $f$ is a state's amount, in moles of atoms in that state per mole of sample. A sample at $z=0.40$ made of 0.5 SOLID at $x=0.5$ and 0.5 LIQUID at $x=0.3$ keeps every atom: $0.5\times0.5+0.5\times0.3=0.40$.

*You don't need more than this to continue.*

---

### What is g° = h − Ts, and where is the melting point?

*thermodynamics · needed for steps 01, 09*

For a pure element each phase model has a straight line in $T$: $g^\circ=h-Ts$, with constant $h$ and $s$ here. The line with the larger $s$ falls faster. Where the solid and liquid lines cross, both have the same $g^\circ$: that temperature is the melting point, and above it the liquid is lower. Pure A at 1400 K: solid $1000-10\times1400=-13000$, liquid $7000-16\times1400=-15400$ J/mol atoms, so the liquid wins.

Where you met it: step 01.

*You don't need more than this to continue.*

---

### How is an ideal g(x) built?

*thermodynamics · needed for steps 02, 08*

Start with the straight line between the two pure ends, $(1-x)g^\circ_A+xg^\circ_B$: the energy if nothing mixed. Add the mixing term $RT[x\ln x+(1-x)\ln(1-x)]$, negative inside $(0,1)$ and zero at the ends; it is $-T$ times the mixing entropy. At $x=0.4$ and 1400 K it is about $-7834$ J/mol atoms. The sum is the phase model's curve.

Where you met it: step 02.

*You don't need more than this to continue.*

---

### Where does x ln x come from?

*thermodynamics · needed for steps 02, 08*

Put $k$ B atoms on $N$ sites. The number of arrangements is $W=N!/(k!\,(N-k)!)$, and the mixing entropy is $k_B\ln W$. For large $N$, Stirling's approximation turns $\ln W/N$ into $-[x\ln x+(1-x)\ln(1-x)]$ with $x=k/N$. Per mole of atoms the mixing entropy is $-R[x\ln x+(1-x)\ln(1-x)]$, which is positive; $-T$ times it is the mixing term in $g(x)$.

*You don't need more than this to continue.*

---

### What does Ω do?

*thermodynamics · needed for steps 03, 08, 15*

A regular solution adds $\Omega x(1-x)$ to the ideal curve: the extra energy of unlike neighbours, largest at $x=0.5$. CALPHAD papers write $\Omega$ as the Redlich–Kister parameter $L_0$. When $\Omega>2RT$ the curve bends down somewhere. It is then no longer convex, and a sample there does better by splitting into an A-rich and a B-rich region of the same structure. The advanced steps use $\Omega=20000$ J/mol at 800 K, where $2RT\approx13300$ J/mol; the split is at 0.070 and 0.930.

Where you met it: step 03 part B.

*You don't need more than this to continue.*

---

### Are two neighbouring dots two phases?

*thermodynamics · needed for steps 09, 13, 18*

Often not. On a grid, a phase's true composition usually lies between two dots, so the solver mixes the two neighbours to get close: two positive amounts, one phase. But inside a miscibility gap two dots of one phase model can be two real compositions of a split (step 03 part B). Counting positive amounts counts dots, not phases: the curve between the dots decides. With a finer menu, or once column generation adds the right state, the twin dots give way to one.

*You don't need more than this to continue.*

---

### What do the phase rule and a tie line say?

*thermodynamics · needed for steps 09, 18*

Gibbs' phase rule: at fixed $T$ and $p$, a sample with $C$ components generically has at most $C$ coexisting phases; more are possible only at special conditions, such as a binary's invariant (eutectic) temperature, where three coexist. So a binary at fixed $p$ and an ordinary fixed $T$ has at most two. A tie line joins the compositions of two coexisting phases; a sample anywhere on it splits into those two, in amounts given by the lever rule. On the lens at 1400 K it runs from 0.312 to 0.441.

*You don't need more than this to continue.*

---

### What are liquidus, solidus and the lens?

*thermodynamics · needed for steps 03, 09, 12*

At each temperature, find the compositions of the coexisting liquid and solid. Plotted against $T$, the liquid compositions trace the liquidus and the solid compositions the solidus. Between them lies the lens: samples there are part liquid, part solid. In the lens of steps 10–14, A melts at 1000 K and B at 1800 K; at 1400 K the liquid has $x=0.312$ and the solid $x=0.441$.

Where you met it: step 03 part C.

*You don't need more than this to continue.*

---

### Core · What is a chemical potential?

*thermodynamics · needed for steps 02, 09, 18*

$\mu_B$ is how much the total Gibbs energy changes per mole of B added, for a small addition at fixed $T$, $p$ and amount of A. On the $g$–$x$ plot it is a height: draw the tangent at the state's composition; it meets $x=0$ at $\mu_A$ and $x=1$ at $\mu_B$. For an ideal phase $\mu_B=g^\circ_B+RT\ln x$. Coexisting phases share the same $\mu_A$ and $\mu_B$: their common tangent.

Where you met it: step 02.

*You don't need more than this to continue.*

---

### What is the exchange slope Δμ = μB − μA?

*thermodynamics · needed for steps 02, 04, 09, 11*

In a full crystal a B atom can only come in if an A atom leaves. The energy of that swap is $\Delta\mu=\mu_B-\mu_A$, the slope of the tangent: the exchange slope of step 02, which steps 09–11 read as the exchange price. It is what the master's second price measures: the line of the step 10 menu (read in step 11) has $\Delta\mu=-1389.0$ J/mol atoms, so there, replacing a little A by B lowers the energy.

Where you met it: step 02.

*You don't need more than this to continue.*

---

### Core · Metastable or unstable: what is the difference?

*thermodynamics · needed for steps 03, 07, 09, 15, 17*

Where the curve bends up, a uniform state is stable against small composition changes; if a split is still lower, it is metastable and can persist until a new region forms. Where the curve bends down, inside the spinodal, it is unstable: any small change lowers the energy. The binodal marks the coexisting compositions. Regular solution at 800 K: binodal 0.070, spinodal 0.211; $z=0.15$ is metastable, $z=0.50$ unstable.

*You don't need more than this to continue.*

---

### What are a supersaturated solid solution and a nucleus?

*thermodynamics · needed for steps 09, 15*

A supersaturated solid solution holds more B than its equilibrium state would, like $z=0.15$ in the regular solution at 800 K. To split, it must first form a small region of the new composition, a nucleus. The bulk model leaves out the energy of the interface around it, which makes small nuclei costly. That barrier, and the time atoms need to move, can keep the sample metastable for a long time.

*You don't need more than this to continue.*

---

### What are lattice stabilities and subsystem assessments?

*thermodynamics · needed for step 09*

A lattice stability is the Gibbs energy of a pure element in a structure it does not adopt on its own, relative to its stable one; it is needed whenever an alloy phase reaches that pure end. CALPHAD databases are built from subsystem assessments: each element and each binary is fitted to its own data, then combined and extrapolated to more components. Extrapolated and metastable parts are often only weakly constrained by data.

*You don't need more than this to continue.*

---

### What are CALPHAD and a database?

*thermodynamics · needed for steps 05, 06, 09, 17*

CALPHAD (CALculation of PHAse Diagrams) describes every phase model's $g$ with a physics-based formula whose parameters are fitted to measurements and calculations. A database (a TDB file) stores those formulas and parameters, and a calculation minimises $G$ with them. In optimisation words, the costs are estimated coefficients: a perfectly solved model can still be wrong about the material.

Where you met it: step 00 and step 05.

*You don't need more than this to continue.*

---

### What is pycalphad?

*thermodynamics · needed for steps 03, 05, 09*

An open-source Python program that reads a CALPHAD database and computes energies and equilibria. The course uses version 0.11.2. Steps 03 part D, 05 and 06 use it; the advanced steps' main track does not need it; the optional notebook task01b uses it.

*You don't need more than this to continue.*

---

### Which sign does work have?

*maths and optimisation · needed for step 00*

In this course work done on the sample counts as positive: $\Delta U=q+w_{\mathrm{on}}$. A sample that receives 100 J of heat and does 30 J of work on its surroundings has $w_{\mathrm{on}}=-30$ J, so $\Delta U=100-30=70$ J. Some books count work done by the sample as positive and write $\Delta U=q-w$; the physics is the same, only the sign of $w$ flips.

*You don't need more than this to continue.*

---

### What is a reversible transfer?

*thermodynamics · needed for step 00*

A reversible transfer passes through equilibrium states with no friction or other dissipation, so it could be run backwards leaving no trace in the sample or its surroundings; going slowly alone is not enough. Only then does the entropy change follow from the heat: $dS=\delta q_{\mathrm{rev}}/T$, or $\Delta S=q_{\mathrm{rev}}/T$ when $T$ stays constant. A reversible 600 J input at a constant 300 K gives $\Delta S=2$ J/K. If heat $q$ flows irreversibly in from surroundings at a constant temperature $T$, the sample's entropy change is larger than $q/T$; entropy is a property of the state, not a kind of heat.

*You don't need more than this to continue.*

---

### Why do the conditions pick the potential?

*thermodynamics · needed for step 00*

What you hold fixed decides which energy is lowest at equilibrium. An isolated whole at fixed U and V maximises its entropy. A closed sample at fixed T and V minimises $F=U-TS$; at fixed T and p it minimises $G=H-TS$. The course works at fixed T and p, so it compares Gibbs energies. Comparing the smallest H alone misses the entropy bonus $-TS$.

Where you met it: step 00.

*You don't need more than this to continue.*

---

### Isolated, closed or open?

*thermodynamics · needed for steps 00, 04*

An isolated system exchanges nothing with its surroundings. A closed system exchanges heat (and possibly work) but no atoms: its amounts of A and B stay fixed. An open system also exchanges atoms, usually with a large reservoir that fixes their chemical potentials. Step 04 compares a closed cell with an open boundary at fixed reservoir prices.

*You don't need more than this to continue.*

---

### Why does the steeper line belong to higher s?

*maths and optimisation · needed for step 01*

For a pure phase $g^\circ=h-Ts$ is a straight line in $T$ with slope $-s$. The larger the entropy $s$, the faster the line falls as $T$ rises. The liquid has the larger entropy (16 against 10 J/(mol K) for A), so its line falls faster and overtakes the solid's at 1000 K: above that, the liquid is lower.

Where you met it: step 01.

*You don't need more than this to continue.*

---

### Zero heat capacity?

*thermodynamics · needed for step 01*

The course's pure-element lines use a constant $h$ and a constant $s$. That is the same as assuming zero heat capacity within each phase, over the temperature range used. Real data have a heat capacity, which makes $h$ and $s$ change with $T$ and the lines curve slightly. For learning how a minimum is chosen, straight lines are enough.

*You don't need more than this to continue.*

---

### Phase amount fraction or mole fraction?

*thermodynamics · needed for steps 01, 02*

Two different fractions. The phase amount fraction $f$ says how much of the sample is in one state: moles of atoms in that state per mole of sample. The mole fraction $x$ says what is inside a state: the share of B among its atoms. A sample half solid and half liquid has $f=0.5$ for each, whatever their compositions.

*You don't need more than this to continue.*

---

### Ends win: why does a tie give a segment?

*maths and optimisation · needed for step 01*

When the only choice is how much is solid and how much liquid, the energy is a straight line in the liquid fraction, from all-solid to all-liquid. A straight line is lowest at one of its ends, so the answer is all solid or all liquid. Only when both ends have the same energy, at the melting point, is every split equally good: a whole segment of answers.

Where you met it: step 01.

*You don't need more than this to continue.*

---

### How do I read a TDB PARAMETER line?

*thermodynamics · needed for steps 05, 06*

A line such as PARAMETER G(LIQUID,CU;0) 298.15 expression; 3200 N ! names a quantity (here the Gibbs energy of pure Cu in the liquid), the temperature range of the expression, the expression itself in J per mole of formula units of that phase (as set by its site ratios), measured from the element references (SER), and a reference. The number after the expression is the upper temperature, and Y or N says whether another range follows. Names such as GHSERCU are functions defined elsewhere in the file, here the Gibbs energy of pure Cu in its reference state. Several lines together build each phase model's $g$. pycalphad reads and evaluates them; step 05's optional extension evaluates one by hand.

Where you met it: step 05.

*You don't need more than this to continue.*

---

### What are an endmember and a reference energy?

*thermodynamics · needed for step 02*

An endmember is one configuration of a phase model, with exactly one kind of occupant on each sublattice: a model building block, not necessarily a stable material. In a one-sublattice phase such as ALPHA that is pure A or pure B in that structure; in step 06's ordered phases an endmember such as Nb:Ni:Ni holds several elements. Its Gibbs energy is a reference value. The straight line between the two endmember energies is the energy of the unmixed parts; in step 02 it is $-9000+12000x$ J/mol atoms at 1000 K. The curve of a mixture is measured from that line.

Where you met it: step 02.

*You don't need more than this to continue.*

---

### Why is 0 ln 0 = 0?

*maths and optimisation · needed for step 02*

$\ln 0$ is not a number, but $x\ln x$ goes to zero as $x$ goes to zero: $x$ shrinks faster than $\ln x$ grows. So the mixing term $RT[x\ln x+(1-x)\ln(1-x)]$ is zero at the pure ends, as it must be: a pure element has nothing to mix. Use the limit; do not ask a calculator for $\ln0$.

*You don't need more than this to continue.*

---

### Why is mixing G negative when the mixing enthalpy is zero?

*thermodynamics · needed for step 02*

In an ideal solution unlike neighbours cost nothing, so the enthalpy of mixing is zero. But mixing creates many more arrangements: the entropy rises, and $-T$ times that rise is negative. At $x=0.10$ and 1000 K the mixing term is about $-2702.9$ J/mol atoms. Zero mixing enthalpy does not make the total enthalpy or the total Gibbs energy zero.

Where you met it: step 02.

*You don't need more than this to continue.*

---

### What is a solid solution?

*thermodynamics · needed for step 02*

A crystal in which atoms of B sit on the same kind of sites as A, at random, over a range of compositions. Copper and nickel form one over the whole composition range at high temperature: one face-centred cubic phase from pure Cu to pure Ni. Below about 640 K the step 05 model separates it into two FCC compositions (a miscibility gap). Its Gibbs energy is a curve in composition, not a single point as for a compound with a fixed formula.

*You don't need more than this to continue.*

---

### Site, occupancy or excess?

*thermodynamics · needed for step 04*

A site is a place an atom can sit. Occupancy $\theta$ is the fraction of a boundary's sites holding B. Excess compares the boundary with a bulk reference on the same number of sites: how many more B atoms the boundary holds than bulk material would. With 200 boundary sites at $\theta=0.15$ and a bulk of $x_b=0.10$, the excess is $200\times(0.15-0.10)=10$ B atoms.

Where you met it: step 04.

*You don't need more than this to continue.*

---

### Why use both boundaries' area?

*maths and optimisation · needed for step 04*

The teaching cell has two equal boundaries, each with 100 sites and 20 nm². The excess counts B atoms at both, so it must be divided by the area of both, 40 nm². Ten excess B atoms over 40 nm² is 0.25 atom/nm². Dividing both boundaries' count by one boundary's area would double the answer.

*You don't need more than this to continue.*

---

### Why subtract the reservoir μ in the grand potential?

*thermodynamics · needed for step 04*

An open boundary trades atoms with a huge reservoir at fixed prices $\mu_A$ and $\mu_B$. Every B it takes, the reservoir pays for at price $\mu_B$, and it hands back an A worth $\mu_A$. So the boundary minimises its own energy minus what the reservoir's atoms cost: $g_s-(1-\theta)\mu_A-\theta\mu_B$. For a bulk at the same prices this is zero, so what remains is an excess.

Where you met it: step 04.

*You don't need more than this to continue.*

---

### How do I get θ from the odds?

*maths and optimisation · needed for step 04*

The open boundary's answer comes as odds: $r=\theta/(1-\theta)$, the ratio of B to A on the boundary. To turn odds into a fraction, divide by one plus the odds: $\theta=r/(1+r)$. Odds of 0.2028 give $\theta=0.2028/1.2028\approx0.1686$, the occupancy of step 04's open boundary.

*You don't need more than this to continue.*

---

### Where does the boundary's B come from?

*thermodynamics · needed for step 04*

In a closed cell no atom enters or leaves, so every extra B atom on the boundary comes from the bulk, whose B fraction falls a little. With 850 B atoms in the 8200-site cell, $x_b=(850-200\theta)/8000$. In an open cell the reservoir supplies the B instead, and the bulk stays at its fixed composition.

Where you met it: step 04.

*You don't need more than this to continue.*

---

### Why compare at the same inventory?

*thermodynamics · needed for step 04*

Two candidate states can only be compared if they hold the same atoms: the same total of A and of B. Otherwise the energy difference mixes the states with a change of what is in the box. The extension of step 04 starts both boundary states from the same bulk and occupancy, so both hold 850 B atoms, then minimises each before subtracting.

Where you met it: the extension of step 04.

*You don't need more than this to continue.*

---

### What is the baseline η per all sites?

*maths and optimisation · needed for step 04*

A baseline $\eta$ is a constant energy of a boundary state per mole of boundary sites, added whatever the occupancy. On the all-site basis it is diluted by the bulk: 200 boundary sites out of 8200, so a baseline of 2000 J/mol boundary sites adds $200\times2000/8200=48.78$ J/mol all sites.

*You don't need more than this to continue.*

---

### What is Newton's method?

*maths and optimisation · needed for step 03*

A way to solve equations by repeated straight-line guesses. At the current guess, replace the curve by its tangent, jump to where the tangent gives zero, and repeat. Near the answer each step roughly doubles the number of correct digits. Step 03 part D uses it to solve the two equal-chemical-potential equations; it needs a reasonable start.

Where you met it: step 03 part D.

*You don't need more than this to continue.*

---

### Which B is this?

*thermodynamics · needed for steps 02, 03, 10, 15*

The course's invented models use the letter B for different elements. Step 02's ALPHA has a B with end energy $13000-10T$ J/mol; the melting lens of step 03 part C has a B that melts at 1800 K. The two B components are different, so their numbers cannot be mixed. Each step names its model; steps 15–17 use step 02's B, steps 10–14 the lens B.

*You don't need more than this to continue.*

---

### Why can a restricted calculation only be higher?

*both decks · needed for steps 01, 14*

Leaving a phase or a state out of a calculation only removes options, and the cheapest of fewer candidates cannot be cheaper than the cheapest of all. At 1100 K pure A has $g=-10000$ as a solid and $-10600$ J/mol as a liquid; a SOLID-only calculation returns $-10000$, 600 above the full answer. It describes a declared, restricted model, a superheated solid, not the equilibrium. The advanced steps call such an answer a ceiling.

Where you met it: step 01.

*You don't need more than this to continue.*
