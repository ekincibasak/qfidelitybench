# Scientific methods

## Fidelity and circuit directions

For two-qubit feature states |psi_i> = U(phi_i)|00>, the ideal fidelity kernel is

K_ij = |<psi_j|psi_i>|² = Tr(rho_i rho_j).

Forward prepares i, applies the prescribed midpoint W, and uncomputes j. Reverse exchanges i and j while retaining the same midpoint sign. In the isolated coherent model W = exp(-i theta ZZ/2), p_f = |<psi_j|W|psi_i>|². For general channels, probabilities come from density-matrix evolution, not that coherent formula.

The fixed compiled schedule has six RY, seven RZ, four CX, two barriers and two measurements; basis ry/rz/cx, optimization zero, transpiler seed21 and identity wiring. Even theta=0 retains the midpoint CX–RZ–CX schedule. The noiseless condition has theta=0 and no noise channels. The demonstration uses only noiseless and theta=+0.10 midpoint cases.

The production conditions were noiseless; midpoint +0.10; local ZZ +0.03 after each CX; and two-qubit depolarizing rho -> 0.99rho+0.01I/4 after each CX. No readout noise was included in production. These are synthetic models, not calibrated hardware channels. The wider historical comparison CSV includes other explicitly labelled controls; do not conflate them with the production condition set.

## Four estimators at equal total shots S

- Forward: N_f/S, with N_f ~ Binomial(S,p_f).
- Reverse: N_r/S, with N_r ~ Binomial(S,p_r).
- Random: choose one fair direction independently before measurements, then take S shots in that direction.
- Paired: (N_f_half + N_r_half)/S, with S/2 independent shots in each direction.

Let a=(p_f-p_r)/2, b=(p_f+p_r)/2-K, q_f=p_f(1-p_f) and q_r=p_r(1-p_r). The paired mean is K+b and its variance is (q_f+q_r)/(2S). Random has the same mean and average conditional shot variance, plus direction variance a². Consequently MSE_random − MSE_paired = a². This is elementary variance accounting, not a new theorem or universal superiority over fixed directions.

For isolated midpoint ZZ, a is odd in theta and b is even. That model-specific cancellation must not be assumed for arbitrary interleaved channels. The saved first repetition is illustrative; the historical studies estimate repeat-averaged errors across a fixed pair set.

## Frozen downstream experiment

Twelve datasets use seeds101–112. Each has 48 independent synthetic two-dimensional uniform[-1,1] inputs, split 24 train / 12 validation / 12 test. The raw target is sin(2pi*x0)+0.3cos(3pi*x1). Training-only mean and population standard deviation standardize inputs. Angles are [pi*z0, pi*z1, pi*(z0+z1)/2, pi*(z0-z1)/2]. Targets are not centered or scaled.

Training off-diagonal pairs are sampled once per arm and mirrored, with diagonal fixed to1 at zero shots. Cross-kernel rows are held-out observations and columns are training observations. Forward always prepares the training input and uncomputes the held-out input. Each dataset has 276 training and 576 cross pairs, total852. Budgets are S=256 and1024, with 100 shot repetitions per condition/budget.

KRR solves (K_train + alpha*I)w = y_train and predicts K_cross*w. Alpha is exactly {0.01,0.1,1,10}; there is no hidden sample-count multiplier, intercept, PSD repair, adaptive jitter or validation refit. Validation MSE selects alpha; exact ties choose the smaller alpha. Linear, RBF and ideal fidelity references use the same splits. RBF bandwidths use training-only distances. Candidates fail for condition number >1e12, nonfinite solution, solver error or normalized residual >1e-10. All-candidate failure blocks primary aggregate reporting; it is not silently removed.

## Statistical inference and costs

Average 100 shot repetitions within each dataset before comparing paired with forward, reverse and random. This gives 12 independent differences per contrast, not1,200 independent datasets. The 3 controls × 4 conditions × 2 budgets form one family of24 paired two-sided t tests (df=11), Holm FWER0.05, with pointwise95% t confidence intervals. Practical benefit additionally requires at least5% reduction in the ratio of dataset-averaged grand-mean risks against all three controls within a condition/budget. Degenerate and failed results follow the frozen explicit policies.

Production's 20,938,752,000 NumPy-modeled shots are distinct from the 120 finite-shot Aer anchor executions /61,440 actual simulator shots. Exact simulator probability checks are another diagnostic category. None is a hardware execution claim. The compact preview contains aggregate production evidence, not its full raw archive or production runner.
