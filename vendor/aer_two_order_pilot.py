#!/usr/bin/env python3
"""Small Qiskit Aer pilot for two-order kernel estimation.

Design: use only synthetic 2-qubit feature vectors; no external research data.
Comparison: one order uses S shots; two orders use S/2 + S/2 shots per pair.
The optional explicit RZZ instruction is a MIDPOINT error toy model, not a
calibrated always-on ZZ mechanism. Circuit-level thermal and readout errors are
additional illustrative channels (not fit to any hardware backend).

Install: pip install -r requirements-aer.txt
Run:     python aer_two_order_pilot.py --shots 4096 --points 12 --repeats 5
"""
from __future__ import annotations

import argparse
import json
import platform
from importlib.metadata import version
from qiskit import qasm2
from pathlib import Path

import numpy as np

try:
    from qiskit import QuantumCircuit, transpile
    from qiskit.quantum_info import Statevector
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import (
        NoiseModel,
        ReadoutError,
        depolarizing_error,
        thermal_relaxation_error,
    )
except ImportError as exc:
    raise SystemExit(
        "Qiskit/Qiskit Aer unavailable. Install with 'pip install -r requirements-aer.txt'. "
        f"Original error: {exc}"
    ) from exc


BASIS_GATES = ["ry", "rz", "cx"]


def encoding(x: np.ndarray) -> QuantumCircuit:
    """Two-qubit complex feature map with real data parameters and one CX."""
    qc = QuantumCircuit(2)
    qc.ry(float(x[0]), 0)
    qc.rz(float(x[1]), 0)
    qc.ry(float(x[2]), 1)
    qc.rz(float(x[3]), 1)
    qc.cx(0, 1)
    qc.ry(float(0.35 * x[0] - 0.20 * x[3]), 1)
    qc.rz(float(0.18 * x[1] + 0.29 * x[2]), 0)
    return qc


def circuit(x: np.ndarray, y: np.ndarray, theta: float) -> QuantumCircuit:
    """Prepare x, apply W, uncompute y: P_xy = |<psi_y|W|psi_x>|^2."""
    qc = QuantumCircuit(2, 2)
    qc.compose(encoding(x), inplace=True)
    # Explicit midpoint coherent unitary; NOT a realistic per-gate noise model.
    if theta != 0:
        qc.rzz(theta, 0, 1)
    qc.compose(encoding(y).inverse(), inplace=True)
    qc.measure([0, 1], [0, 1])
    return qc


def noise_model(*, gate_error: float, readout_error: float, t1_us: float,
                t2_us: float, thermal: bool = True) -> NoiseModel:
    if not 0 <= gate_error <= 1 or not 0 <= readout_error <= 1:
        raise ValueError("Error probabilities must be in [0, 1].")
    nm = NoiseModel(basis_gates=BASIS_GATES)
    # Illustrative durations only; units in seconds in these formulas.
    t1, t2 = t1_us * 1e-6, t2_us * 1e-6
    if thermal:
        one = thermal_relaxation_error(t1, t2, 40e-9)
        two_relax = thermal_relaxation_error(t1, t2, 200e-9)
        two = two_relax.tensor(two_relax)
        nm.add_all_qubit_quantum_error(one, ["ry"])
        if gate_error:
            two = depolarizing_error(gate_error, 2).compose(two)
        nm.add_all_qubit_quantum_error(two, ["cx"])
    elif gate_error:
        nm.add_all_qubit_quantum_error(depolarizing_error(gate_error, 2), ["cx"])
    # RZ is assumed virtual and ideal in this simplified channel model.
    if readout_error:
        e = float(readout_error)
        nm.add_all_qubit_readout_error(ReadoutError([[1-e, e], [e, 1-e]]))
    return nm


def zero_probability(result, idx: int, shots: int) -> float:
    counts = result.get_counts(idx)
    if sum(counts.values()) != shots:
        raise ValueError("Returned counts do not match requested shot budget.")
    return float(counts.get("00", 0) / shots)


def evaluate(*, points: int, shots: int, theta: float, repeats: int,
             seed: int, gate_error: float, readout_error: float,
             t1_us: float, t2_us: float, noise_mode: str = "none",
             thermal: bool = True) -> dict:
    if points < 3 or shots < 2 or shots % 2:
        raise ValueError("Use >=3 points and a positive even shot count.")
    if repeats < 1:
        raise ValueError("repeats must be >=1")
    if noise_mode not in {"none", "illustrative"}:
        raise ValueError("Unknown noise mode")
    if noise_mode == "none" and theta != 0:
        raise ValueError("Noiseless reference requires theta=0")
    rng = np.random.default_rng(seed)
    xs = rng.uniform(-np.pi, np.pi, size=(points, 4))
    psis = [Statevector.from_instruction(encoding(row)).data for row in xs]
    pairs = [(i, j) for i in range(points) for j in range(i+1, points)]
    exact = np.array([abs(np.vdot(psis[i], psis[j]))**2 for i,j in pairs])
    forward = [circuit(xs[i], xs[j], theta) for i,j in pairs]
    backward = [circuit(xs[j], xs[i], theta) for i,j in pairs]
    nm = None if noise_mode == "none" else noise_model(
        gate_error=gate_error, readout_error=readout_error,
        t1_us=t1_us, t2_us=t2_us, thermal=thermal)
    sim = AerSimulator(method="density_matrix", noise_model=nm)
    # Explicit identical basis in both modes; RZZ decomposes into CX-RZ-CX.
    cf = transpile(forward, basis_gates=BASIS_GATES, optimization_level=0,
                   seed_transpiler=seed, num_processes=1)
    cb = transpile(backward, basis_gates=BASIS_GATES, optimization_level=0,
                   seed_transpiler=seed, num_processes=1)
    gate_counts = {"forward": [dict(c.count_ops()) for c in cf],
                   "backward": [dict(c.count_ops()) for c in cb]}
    # Need independent finite-shot samples for each protocol and repetition.
    rows = []
    for k in range(repeats):
        run_seed = seed + 173 * k
        one_res = sim.run(cf, shots=shots, seed_simulator=run_seed).result()
        f_res = sim.run(cf, shots=shots//2, seed_simulator=run_seed + 1).result()
        b_res = sim.run(cb, shots=shots//2, seed_simulator=run_seed + 2).result()
        single = np.array([zero_probability(one_res, z, shots) for z in range(len(pairs))])
        pf = np.array([zero_probability(f_res, z, shots//2) for z in range(len(pairs))])
        pb = np.array([zero_probability(b_res, z, shots//2) for z in range(len(pairs))])
        paired = (pf+pb)/2
        rmse_single = float(np.sqrt(np.mean((single-exact)**2)))
        rmse_paired = float(np.sqrt(np.mean((paired-exact)**2)))
        rows.append({"repeat":k,
                     "simulator_seeds":[run_seed,run_seed+1,run_seed+2],
                     "counts_single":[one_res.get_counts(z) for z in range(len(pairs))],
                     "counts_forward_half":[f_res.get_counts(z) for z in range(len(pairs))],
                     "counts_reverse_half":[b_res.get_counts(z) for z in range(len(pairs))],
                     "single_estimates":single.tolist(), "paired_estimates":paired.tolist(),"rmse_single":rmse_single,
                     "rmse_paired":rmse_paired,
                     "relative_gain":1-rmse_paired/rmse_single if rmse_single else None,
                     "raw_asymmetry_rms":float(np.sqrt(np.mean(((pf-pb)/2)**2)))})
    return {
        "disclaimer":"Synthetic data and illustrative noise; not calibrated hardware or a novelty claim",
        "environment":dict(python=platform.python_version(),platform=platform.platform(),
                           packages={name:version(name) for name in ["numpy","qiskit","qiskit-aer"]}),
        "synthetic_features":xs.tolist(), "pairs":pairs, "ideal_reference":exact.tolist(),
        "noise_mode":noise_mode, "thermal_requested":thermal,
        "effective_noise_model":None if nm is None else nm.to_dict(),
        "basis_gates":BASIS_GATES,"optimization_level":0,"seed_transpiler":seed,
        "compiled_qasm":{ "forward":[qasm2.dumps(c) for c in cf],
                          "backward":[qasm2.dumps(c) for c in cb]},
        "resources_per_repeat":dict(single_shots=len(pairs)*shots,
            paired_shots=len(pairs)*shots,single_circuit_executions=len(pairs),
            paired_circuit_executions=2*len(pairs),
            total_shots_both_protocols=2*len(pairs)*shots),
        "settings":dict(points=points,pairs=len(pairs),shots_per_pair=shots,
                        theta_midpoint=theta,repeats=repeats,seed=seed,
                        gate_error=gate_error,readout_error=readout_error,
                        t1_us=t1_us,t2_us=t2_us),
        "compiled_gate_counts_all_pairs":gate_counts,
        "repetitions":rows,
        "average_rmse_single":float(np.mean([r["rmse_single"] for r in rows])),
        "average_rmse_paired":float(np.mean([r["rmse_paired"] for r in rows])),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--noise-model", choices=["none", "illustrative"], default="none")
    p.add_argument("--no-thermal", action="store_true")
    p.add_argument("--shots", type=int, default=4096)
    p.add_argument("--points", type=int, default=12)
    p.add_argument("--repeats", type=int, default=5)
    p.add_argument("--seed", type=int, default=2026)
    p.add_argument("--theta", type=float, default=0.0,
                   help="RZZ angle in radians; not a calibrated physical ZZ coupling")
    p.add_argument("--gate-error", type=float, default=0.005)
    p.add_argument("--readout-error", type=float, default=0.01)
    p.add_argument("--t1-us", type=float, default=150)
    p.add_argument("--t2-us", type=float, default=100)
    p.add_argument("--output", type=Path, default=Path("aer_pilot_results.json"))
    args = p.parse_args()
    out = evaluate(points=args.points,shots=args.shots,repeats=args.repeats,
                   theta=args.theta,seed=args.seed,
                   gate_error=args.gate_error,readout_error=args.readout_error,
                   t1_us=args.t1_us,t2_us=args.t2_us,
                   noise_mode=args.noise_model,thermal=not args.no_thermal)
    args.output.write_text(json.dumps(out, indent=2, default=lambda x: x.tolist()), encoding="utf-8")
    print(json.dumps({"average_rmse_single":out["average_rmse_single"],
                      "average_rmse_paired":out["average_rmse_paired"],
                      "saved":str(args.output)},indent=2))


if __name__ == "__main__":
    main()
