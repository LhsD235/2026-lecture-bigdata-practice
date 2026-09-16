# Task 2 — Crossover Measurement

## 1. Experiment setup

I compared Brute Force and my MinHash-based LSH finder using identical synthetic document sets and a Jaccard similarity threshold of **0.6**. I measured wall-clock time, calls to the similarity function, and peak memory traced during each algorithm's execution.

I tested five document counts from 250 to 4,000, a **16×** range. Since a single `bench.build()` call supplies only 2,120 documents, I updated `task2_crossover.py` to generate further batches with different seeds for larger `n`. Document generation happened outside the timed section.

## 2. Measurements

| Documents | Brute Force time (s) | Brute comparisons | LSH time (s) | LSH comparisons |
|---:|---:|---:|---:|---:|
| 250 | 0.21 | 31,125 | 1.21 | 1 |
| 500 | 0.90 | 124,750 | 1.26 | 7 |
| 1,000 | 3.54 | 499,500 | 1.52 | 27 |
| 2,000 | 14.45 | 1,999,000 | 2.12 | 107 |
| 4,000 | 54.80 | 7,998,000 | 3.04 | 229 |

The full, unrounded measurements are saved in `out/crossover.json`.

## 3. Quadratic growth check

Brute Force checks every unordered document pair, giving `n(n - 1) / 2` comparisons. I checked its measured runtime rather than relying on that formula alone:

| Dataset doubled | Brute time change | Time multiplier |
|---|---|---:|
| 250 → 500 | 0.21 → 0.90 s | 4.29× |
| 500 → 1,000 | 0.90 → 3.54 s | 3.93× |
| 1,000 → 2,000 | 3.54 → 14.45 s | 4.08× |
| 2,000 → 4,000 | 14.45 → 54.80 s | 3.79× |

All four measurements are reasonably close to a fourfold increase when `n` doubles, consistent with quadratic scaling. At 4,000 documents, the comparison count was exactly `4,000 × 3,999 / 2 = 7,998,000`.

## 4. Crossover and why it occurs

At **500** documents, Brute Force took **0.90 s** and LSH took **1.26 s**. At **1,000**, Brute Force took **3.54 s** and LSH took **1.52 s**. The crossover therefore occurred **somewhere between 500 and 1,000 documents** in the measured range; I did not determine the precise number.

LSH loses at small sizes because generating MinHash signatures, creating bands and buckets, and constructing candidates require work before any exact similarity comparisons occur. When the dataset becomes larger, eliminating most pairwise comparisons outweighs that setup cost. At 4,000 documents, LSH took **3.04 s** and tested **229** candidates, compared with **54.80 s** and **7,998,000** comparisons for Brute Force.

## 5. Peak memory at the largest size

| Algorithm | Peak traced memory at n = 4,000 |
|---|---:|
| Brute Force | 0.02 MiB |
| LSH | 28.54 MiB |

LSH stores hashed shingle values, signatures, buckets, and candidate pairs, whereas Brute Force creates far fewer intermediate structures. These values come from Python's `tracemalloc` **during the algorithm call**. Because the documents were generated before tracing began, the figures are not total process RAM usage and should be interpreted as traced allocations within the measured section.

## 6. Practical limit and limitations

I stopped at **4,000 documents** because Brute Force took **54.80 seconds**, close to a minute. Waiting time, rather than observed memory pressure, was the reason for stopping. I did not measure 8,000 or 16,000 documents.

The documents are synthetic, so document size and similarity distributions may differ in real workloads. This timing experiment also does not directly verify that both algorithms return the same pairs; recall is checked separately in Task 3.

## 7. Machine and measurement conditions

| Item | Recorded information |
|---|---|
| CPU | 13th Gen Intel Core i7-1360P |
| OS / environment | WSL2 Ubuntu |
| WSL-visible RAM | 7.5 GiB |
| WSL swap | 2.0 GiB |
| Other applications running | VS Code and Chrome (about 2-3 browser windows) |

The memory above is what WSL reported, not necessarily all physical RAM installed in the laptop. VS Code and approximately 2–3 Chrome windows were open during the experiment. Other background processes were not systematically
recorded, so I cannot claim that the machine was otherwise idle. This missing detail limits how precisely another person could reproduce my timings.

## 8. Conclusion

On this machine, Brute Force was faster for the smallest measured datasets, but LSH was faster by 1,000 documents. At 4,000 documents, LSH substantially reduced similarity comparisons and wall time, while using more additional traced memory. The measured crossover is **between 500 and 1,000 documents**, not an exact or universal threshold.
