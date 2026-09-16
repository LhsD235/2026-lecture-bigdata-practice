# Task 2 — Crossover Measurement

## 1. Experiment Overview

I compared Brute Force and my LSH implementation to find the point where LSH becomes faster on my machine.

Both algorithms used the same document datasets and a Jaccard similarity threshold of 0.6. I measured execution time, similarity comparison count, and peak traced memory.

I tested five dataset sizes, from 250 to 4,000 documents. Since the original data generator produced only 2,120 documents, I modified `task2_crossover.py` to generate additional batches using different seeds. This allowed the experiment to use the requested number of documents. Dataset generation was performed outside the timed section.

## 2. Experimental Results

| Documents (n) | Brute Time (s) | Brute Comparisons | LSH Time (s) | LSH Comparisons |
|---:|---:|---:|---:|---:|
| 250 | 0.21 | 31,125 | 1.21 | 1 |
| 500 | 0.90 | 124,750 | 1.26 | 7 |
| 1,000 | 3.54 | 499,500 | 1.52 | 27 |
| 2,000 | 14.45 | 1,999,000 | 2.12 | 107 |
| 4,000 | 54.80 | 7,998,000 | 3.04 | 229 |

The experiment covers a 16-fold increase in dataset size, from 250 to 4,000 documents.

## 3. Crossover Point

Brute Force was faster at 500 documents, taking 0.90 seconds compared with 1.26 seconds for LSH.

However, at 1,000 documents, LSH took 1.52 seconds while Brute Force took 3.54 seconds.

Based on these results, the crossover on my machine lies between 500 and 1,000 documents. I did not measure additional sizes within this interval, so the exact crossover point is unknown.

I think this happens because LSH has to generate MinHash signatures and build buckets before comparing document pairs. For small datasets, this preparation takes longer than directly comparing every pair. As the dataset grows, avoiding unnecessary similarity comparisons becomes more beneficial.

## 4. Brute Force Runtime Growth

I also checked whether Brute Force runtime increases by approximately four times when the number of documents doubles.

| Document Size | Runtime Change | Growth Factor |
|---|---|---:|
| 250 → 500 | 0.21s → 0.90s | 4.29x |
| 500 → 1,000 | 0.90s → 3.54s | 3.93x |
| 1,000 → 2,000 | 3.54s → 14.45s | 4.08x |
| 2,000 → 4,000 | 14.45s → 54.80s | 3.79x |

Brute Force compares every possible unordered pair of documents, so the number of comparisons is:

C(n) = n(n - 1) / 2

When the dataset size doubles, the number of comparisons increases by approximately four times.

My measured runtime followed a similar pattern. The growth factors ranged from 3.79x to 4.29x, which is consistent with the expected quadratic time complexity, O(n^2).

## 5. LSH Performance

At 4,000 documents, Brute Force performed 7,998,000 similarity comparisons, while LSH performed only 229.

Their execution times were 54.80 seconds and 3.04 seconds, respectively.

LSH was approximately 18 times faster at this dataset size. It achieved this by using MinHash and banding to select candidate pairs instead of comparing every possible pair.

However, LSH was slower at 250 and 500 documents. This shows that reducing similarity comparisons does not automatically reduce total execution time. The cost of generating signatures and building buckets also needs to be considered.

## 6. Memory Usage

At the largest dataset size, the measured peak memory usage was:

| Algorithm | Peak Traced Memory |
|---|---:|
| Brute Force | 0.02 MiB |
| LSH | 28.54 MiB |

LSH required more additional memory because it stored hash values, MinHash signatures, buckets, and candidate pairs.

Brute Force used very little additional traced memory because it compared document pairs directly without building these data structures.

Memory was measured using Python's `tracemalloc`. Since the input documents were created before memory tracking started, these values represent peak traced allocations during algorithm execution, not total process memory.

In this experiment, LSH reduced execution time and similarity comparisons at the cost of higher additional memory usage.

## 7. Practical Limit and Limitations

I stopped at 4,000 documents because Brute Force took 54.80 seconds, which was close to one minute. This was the largest size I measured, and I did not test 8,000 or more documents.

The experiment used synthetic documents, so results may differ with real datasets containing different document lengths or similarity distributions.

Also, this timing experiment did not directly verify whether the two algorithms returned exactly the same document pairs. LSH may miss some similar pairs when selecting candidates, so recall needs to be checked separately.

## 8. Experimental Environment

| Component | Specification |
|---|---|
| CPU | 13th Gen Intel Core i7-1360P |
| Environment | WSL2 Ubuntu |
| WSL Memory | 7.5 GiB |
| Swap Memory | 2.0 GiB |
| Other Programs Running | Not recorded during the experiment |

The RAM value is the memory visible to WSL, not necessarily the total physical RAM installed in the computer.

Since execution time depends on hardware and the execution environment, the crossover point may differ on another machine.

## 9. Conclusion

On my machine, Brute Force was faster for the smaller datasets, but LSH became faster somewhere between 500 and 1,000 documents.

At 4,000 documents, Brute Force took 54.80 seconds and performed 7,998,000 similarity comparisons. LSH took 3.04 seconds and performed only 229 similarity comparisons.

The main finding is that LSH has an initial preprocessing cost, but the reduction in similarity comparisons becomes valuable as the number of documents increases. In my experiment, this improvement came with higher additional memory usage.