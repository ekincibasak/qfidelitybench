# Verified findings and interpretation

## Kernel estimation

Under isolated midpoint coherent error +0.10 at S=1024, historical actual-Aer paired/comparator MSE ratios were:

| Comparator | Ratio | Pointwise approximate95% Monte Carlo interval |
|---|---:|---|
| Forward | 0.517149 | [0.504620,0.529678] |
| Reverse | 0.518544 | [0.505867,0.531222] |
| Random | 0.516284 | [0.503290,0.529278] |

These are 1,000 repeat measurements of 28 pairs on one fixed synthetic eight-point geometry, not independent dataset-generalization evidence. The full historical comparison table is included with engine/noise/budget labels to avoid representing this selected condition as all results. A ratio below1 favors paired; the selected single-repetition demonstration need not favor it.

## Frozen downstream KRR: null finding

All9,600 dataset/condition/budget/repeat units completed, yielding38,400 estimator outputs with no failed/missing primary cells. None of24 primary tests was significant after Holm correction. The smallest adjusted p-value was approximately0.24665. Risk ratios ranged approximately0.98032–1.01678; none met the required ≤0.95 practical threshold. No condition/budget passed against all three controls.

This is no demonstrated downstream advantage under the frozen design. It does not establish estimator equivalence, prove absence of benefit elsewhere or support quantum advantage. All contrasts, per-dataset means and within-dataset shot standard deviations are retained in `results/krr_statistics.json`.

## Limitations retained

- Alpha=10 was selected for32.4375% of the quantum fits, at the upper frozen-grid boundary. No post-result grid expansion occurred.
- Two-qubit ideal fidelity Grams have rank at most16; a24-point training Gram is rank deficient before regularization.
- Finite-shot matrices may be indefinite. No PSD repair was applied; the algebraic ridge predictor has no asserted convex RKHS interpretation for indefinite matrices.
- Twelve independent datasets give limited precision; paired-t assumptions and fixed task/noise design constrain interpretation.
- An earlier matrix-diagnostic stage disclosed a post-result correction for sparse-event inference, retaining its original analysis. No PSD-superiority claim is made here, and no sparse-event significance result is used as headline evidence.
- No real-device run, runtime speedup, multi-qubit validation or broad task-generalization claim is supported.

![Alpha boundary](../figures/alpha_boundary.png)

This unchanged production diagnostic shows the per-dataset proportion of repetitions selecting alpha=10 by method/condition/budget. It is descriptive, not a new hypothesis test.
