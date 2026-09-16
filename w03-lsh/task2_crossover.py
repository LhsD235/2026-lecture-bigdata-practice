#!/usr/bin/env python3
"""Week 3 · Task 2 — Find the crossover on your own machine.

Textbook §3.4.

Everybody knows brute force is quadratic and LSH is not. That is not the
interesting question. The interesting question is **where, on the machine in
front of you, does it start to matter** - and that answer is yours alone. It
depends on your CPU, your memory, and how big your shingle sets are.

This script gives you the timing loop. The two methods are yours: import them
from Task 1 and Task 3.

    python3 task2_crossover.py --sizes 500,1000,2000,4000
    python3 task2_crossover.py --sizes 8000,16000          # keep going

Write down where it hurts. That is the deliverable.
"""

import argparse
import json
import os
import platform
import time
import tracemalloc


HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def machine():
    return {
        "platform": platform.platform(),
        "processor": platform.processor() or platform.machine(),
        "python": platform.python_version(),
    }


def timed(fn, *args):
    """Wall time and peak memory of one call."""
    tracemalloc.start()

    t0 = time.perf_counter()
    result = fn(*args)
    elapsed = time.perf_counter() - t0

    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return result, elapsed, peak


def build_docs(bench, n):
    """Build exactly n synthetic documents using different seeds.

    bench.build() creates only a fixed-size dataset, so repeatedly generate
    datasets with different seeds until at least n documents are available.
    """
    docs = []
    seed = bench.SEED

    while len(docs) < n:
        docs.extend(bench.build(seed))
        seed += 1

    return docs[:n]


def main():
    p = argparse.ArgumentParser()

    p.add_argument(
        "--sizes",
        default="250,500,1000,2000",
        help="comma-separated document counts to try",
    )

    p.add_argument(
        "--threshold",
        type=float,
        default=0.6,
    )

    a = p.parse_args()

    os.makedirs(OUT, exist_ok=True)

    import bench
    from task3_scale import BruteForce

    try:
        from task3_scale import YourFinder
    except Exception:
        YourFinder = None

    rows = []

    for n in [int(x) for x in a.sizes.split(",")]:

        # 요청한 n개만큼 실제 문서를 생성
        docs = build_docs(bench, n)

        # --------------------------------------------------
        # Brute Force
        # --------------------------------------------------
        sim = bench.Counter()

        _, t_brute, m_brute = timed(
            BruteForce(a.threshold).find,
            docs,
            sim,
        )

        c_brute = sim.calls

        row = {
            "n": n,
            "brute_s": t_brute,
            "brute_calls": c_brute,
            "brute_peak_bytes": m_brute,
        }

        # --------------------------------------------------
        # LSH
        # --------------------------------------------------
        if YourFinder is not None:
            sim2 = bench.Counter()

            try:
                _, t_lsh, m_lsh = timed(
                    YourFinder(a.threshold).find,
                    docs,
                    sim2,
                )

                row.update({
                    "lsh_s": t_lsh,
                    "lsh_calls": sim2.calls,
                    "lsh_peak_bytes": m_lsh,
                })

            except NotImplementedError:
                pass

        rows.append(row)

        # --------------------------------------------------
        # 결과 출력
        # --------------------------------------------------
        line = (
            f"  n={n:>6}  "
            f"brute {t_brute:>8.2f}s  "
            f"{c_brute:>12,} cmp"
        )

        if "lsh_s" in row:
            line += (
                f"   |  "
                f"lsh {row['lsh_s']:>7.2f}s  "
                f"{row['lsh_calls']:>9,} cmp"
            )

        print(line)

    # ------------------------------------------------------
    # 결과 저장
    # ------------------------------------------------------
    path = os.path.join(OUT, "crossover.json")

    if os.path.exists(path):
        with open(path, "r") as f:
            prior = json.load(f)
    else:
        prior = {"runs": []}

    prior["machine"] = machine()
    prior["runs"].extend(rows)

    with open(path, "w") as f:
        json.dump(prior, f, indent=2)

    print(
        f"\n  -> out/crossover.json  "
        f"({len(prior['runs'])} measurement(s))"
    )

    print(
        "  Keep raising --sizes until something becomes unpleasant. "
        "Record where."
    )


if __name__ == "__main__":
    main()