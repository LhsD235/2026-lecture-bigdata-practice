# Week 4 Observations

## Task 1 — Three Sketches

A Bloom filter cannot have a false negative because every inserted item sets all of its hash-selected bits to 1, and those bits are never cleared. The predicted false-positive rate was **0.860%**, while the measured rate was **0.820%**; the small difference is expected because the formula gives an expected probability while the experiment uses a finite sample.

For Flajolet-Martin, I used groups of two hash estimates, averaged each group, and then took the median of the group averages. The final estimate was **22,528** for a true distinct count of **19,953 (1.13x)**; an earlier grouping of four produced **28,672 (1.44x)**, showing that the combining rule affects the estimate.

Reservoir sampling handles an unknown stream length in `j = rng.randrange(i + 1)`: each newly observed item is considered using only the number of items seen so far, and it replaces an existing reservoir item only when `j < k`. Therefore, the algorithm never needs to know the final stream length and stores only `k` items.

## Task 2 — Where Exact Stops Fitting

The exact-set approach became unpleasant at **25,600,000 stream items**, where it took **34.79 s** and reached **756.5 MB** peak memory. Neither resource was completely exhausted, but execution time became the first practical limitation for repeated experiments, while memory was also increasing rapidly.

Exact memory grew approximately linearly: from **46.6 MB at 1.6 million items** to **756.5 MB at 25.6 million items**, about **16.2x growth for a 16x larger stream**. In contrast, Flajolet-Martin remained around **0.01 MB** across the recorded sizes, approximately **1x memory growth**, because its state depends on the number of hash registers rather than the stream length.

A factor-of-two distinct estimate can be acceptable for rough traffic monitoring or order-of-magnitude capacity planning, where the exact user count is not critical. It would not be acceptable for billing, quotas, or a precise daily KPI, where an error approaching 2x could lead to materially wrong decisions.

## Task 3 — Same Memory, Fewer Mistakes

I changed the number of Bloom-filter hash functions to **k = 7**. Since `m/n = 80,000/8,000 = 10`, the optimum is `k = (m/n) ln 2 = 10 ln 2 ≈ 6.93`, so the nearest integer is 7.

At the optimum, the theoretical minimum false-positive rate is approximately `(0.6185)^(m/n) = (0.6185)^10 ≈ 0.819%`. My measured rate was **0.820%**, compared with the baseline **9.511%**, so the implementation reached essentially the theoretical floor while keeping zero false negatives and the same 80,000-bit budget.

If `n` were unknown, I would either choose a reasonable capacity estimate and grow/rebuild the filter when it approaches that capacity, or use a scalable Bloom-filter design. Guessing `n` too low causes the filter to become saturated and increases false positives; guessing too high wastes memory by allocating more bits than are needed.
