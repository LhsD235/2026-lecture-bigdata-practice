# Week 3 — Observations

## Task 1: MinHash and LSH

I implemented Jaccard similarity, MinHash signatures, and LSH candidate generation. My MinHash function scans each matrix row once and updates every column containing that row; it does not scan the entire matrix separately for each column. This matters when the matrix is too large to revisit repeatedly.

In `lsh_candidates()`, I raise a `ValueError` if the signature length is not divisible by the number of bands. This keeps all bands the same size without silently dropping any signature entries. I store candidate pairs in a set to avoid duplicates.

For S1 and S4, the true Jaccard similarity is **2/3**, but the two-hash MinHash estimate is **1.0** because both signature positions agree. More hash functions could reduce the estimate's variance, at the cost of extra hashing, memory, and computation.

## Task 2: Finding the Crossover

I tested **250, 500, 1,000, 2,000, and 4,000** documents (five sizes across a 16× range). Because one call to `bench.build()` produces 2,120 documents, I modified the Task 2 measurement script to generate additional batches with different seeds when needed. Dataset generation was excluded from the timed section.

Brute Force was faster at 500 documents (**0.90 s** versus **1.26 s**), while LSH was faster at 1,000 (**1.52 s** versus **3.54 s**). Thus, my measured crossover lies **between 500 and 1,000 documents**; I did not measure its exact location. The successive Brute Force time increases when doubling the dataset were **4.29×, 3.93×, 4.08×, and 3.79×**, consistent with quadratic growth.

At 4,000 documents, waiting time became the limiting factor: Brute Force took **54.80 s** and **7,998,000 comparisons**, while LSH took **3.04 s** and **229 comparisons**. I stopped at that size rather than claiming results for larger datasets. The experiment ran on an **Intel Core i7-1360P in WSL2 Ubuntu**, with **7.5 GiB of WSL-visible memory**; whether other applications were running was not recorded. Full results, including traced peak memory, are in `out/curve.md` and `out/crossover.json`.

## Task 3: Finding Similar Pairs with Fewer Comparisons

My `YourFinder` builds **120-value MinHash signatures**, divides them into **30 bands of 4 rows**, and calls the exact similarity function only for pairs sharing at least one band. It uses the supplied `similarity()` function for final filtering at the **0.6** threshold and a set to avoid duplicate candidate comparisons.

### S-curve calculation and parameter choice

For similarity `s`, `b` bands, and `r` rows per band, the approximate probability of becoming a candidate is:

```text
P(candidate) = 1 - (1 - s^r)^b
```

With `b = 30` and `r = 4`, the approximate transition point is `(1/30)^(1/4) ≈ 0.427`, below the target similarity of `0.6`. At `s = 0.6`, the approximate candidate probability is `1 - (1 - 0.6^4)^30 ≈ 0.984`. I placed the transition below the target to favor recall, accepting some extra candidates. These are theoretical approximations; actual recall was measured with the benchmark.

### Benchmark and banding trade-off

The fixed-seed benchmark had **2,120 documents** and **121 truly similar pairs**. Brute Force made **2,246,140** similarity comparisons; my original configuration made **123**, with **100% recall** and **100% precision**. The saved `out/bench.txt` recorded **7.73 s** for Brute Force and **0.49 s** for LSH. In this run, all 121 true pairs were returned, and two additional candidates were rejected by the exact similarity check. Perfect recall here does not guarantee perfect recall on other datasets.

I then kept 120 hashes but changed to **15 bands of 8 rows**. The approximate transition moved to `(1/15)^(1/8) ≈ 0.713`, above the target of 0.6. Comparisons dropped from **123 to 83**, but recall fell from **100% to 68.6%**: the modified configuration found only 83 of the 121 true pairs, missing 38. I restored **30 bands × 4 rows**, since reducing comparisons is not useful here if it loses so many real pairs.

### When hashing overhead matters

The benchmark charges calls to `similarity()` but does not count signature generation or bucketing as comparisons. Those operations still consume time and memory. In Task 2, LSH was slower at 250 and 500 documents despite making far fewer similarity comparisons; even at 4,000 documents, its preprocessing and candidate search contributed to a total runtime of **3.04 s**. Ignoring hashing is therefore a poor approximation when preprocessing dominates—for example, with small datasets, large shingle sets, or many hash functions. The actual crossover depends on the workload and machine rather than a universal document count.
