#!/usr/bin/env python3
"""
Reproduction script for the numerical checks in Section 16 of
"Mission-Invariant Architecture Morphing" (MIAM).

Validates internal arithmetic only. It does not measure security efficacy.
Requires Python 3.8+ and NumPy.
"""
import math
from collections import Counter

import numpy as np


def entropy(labels):
    n = len(labels)
    return -sum((k / n) * math.log2(k / n) for k in Counter(labels).values())


def variation_of_information(p1, p2):
    joint = list(zip(p1, p2))
    return 2 * entropy(joint) - entropy(p1) - entropy(p2)


def main():
    # Retention half-times (Equations for T50,det and T50,Pois)
    tau, rho = 300.0, 0.25
    lam = 1.0 / tau
    t50_det = tau * math.log(2) / math.log(1 / rho)
    t50_pois = math.log(2) / (lam * (1 - rho))
    print(f"T50,det  = {t50_det:.2f} s")
    print(f"T50,Pois = {t50_pois:.2f} s")

    # RTR from synthetic replay counts
    successes = np.array([2, 8, 0, 5, 16])
    v = successes / 20.0
    w = np.array([5, 3, 2, 4, 1])
    c = np.array([0.9, 0.8, 0.7, 0.6, 0.5])
    num, den = float(np.sum(w * c * v)), float(np.sum(w * c))
    print(f"v = {v.tolist()}  RTR = {num:.2f}/{den:.1f} = {num / den:.5f}")

    # PSR under the independence approximation
    paths = [[0.1, 0.4, 0.25], [0.4, 0.8], [0.1, 0.8]]
    pw = np.array([5, 3, 2])
    surv = np.array([np.prod(p) for p in paths])
    print(f"path survivals = {np.round(surv, 4).tolist()}  PSR = {np.sum(pw * surv) / np.sum(pw):.3f}")

    # Partition distance for the Figure 5 morph: capabilities A..E
    before = ["S1", "S1", "S2", "S3", "S2"]  # A,B in S1; C,E in S2; D in S3
    after = ["T1", "T1", "T2", "T1", "T3"]   # A,B,D in T1; C in T2; E in T3
    h1, h2, hj = entropy(before), entropy(after), entropy(list(zip(before, after)))
    print(f"H(Pi) = {h1:.5f}  H(Pi') = {h2:.5f}  H(Pi,Pi') = {hj:.5f} bits")
    vi = variation_of_information(before, after)
    print(f"VI = {vi:.5f} bits  D_Pi = {vi / math.log2(len(before)):.5f}")

    # Attacker completion model
    b = 1 / 1200.0
    print(f"b/(b + lambda(1-rho)) = {b / (b + lam * (1 - rho)):.4f}")

    # Recurrence-aware retention: 4 graphs, no self-transition
    m = 4
    Q = (np.ones((m, m)) - np.eye(m)) / (m - 1)
    eig = sorted(np.linalg.eigvals(Q).real, reverse=True)
    print(f"eigenvalues of Q = {np.round(eig, 4).tolist()}")
    for name, vvec in [("valid in 1 of 4", np.array([1, 0, 0, 0.0])),
                       ("valid in 2 of 4", np.array([1, 1, 0, 0.0]))]:
        seq = [float((np.linalg.matrix_power(Q, n) @ vvec)[0]) for n in range(9)]
        print(f"{name}: " + ", ".join(f"{x:.4f}" for x in seq))
    # Poisson arrivals, 1-of-4 case: E[v(t)] = 1/4 + 3/4 exp(-4 lambda t / 3)
    t50_rec = 3 * math.log(3) / (4 * lam)
    print(f"T50 under recurrence (1 of 4, Poisson) = {t50_rec:.2f} s")

    # Monte Carlo check of E[rho^N(t)] at the analytical Poisson half-time
    rng = np.random.default_rng(20260926)
    N = rng.poisson(lam * t50_pois, size=120_000)
    r = rho ** N
    se = np.std(r, ddof=1) / math.sqrt(len(r))
    print(f"Monte Carlo mean retention at T50,Pois = {np.mean(r):.4f} +/- {1.96 * se:.4f} (95% CI; target 0.5)")

    # Bell numbers
    def bell(n):
        row = [1]
        for _ in range(n):
            nxt = [row[-1]]
            for x in row:
                nxt.append(nxt[-1] + x)
            row = nxt
        return row[0]
    print("Bell:", {n: bell(n) for n in (5, 8, 10, 15, 20)})


if __name__ == "__main__":
    main()
