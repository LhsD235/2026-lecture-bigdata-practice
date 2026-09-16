# Week 3 — Observations

## Task 1: MinHash and LSH

I implemented Jaccard similarity, MinHash signature generation,
and LSH candidate selection.

For MinHash, I used a row-based approach. The program scans each
matrix row once and updates the signatures of the columns that
contain that row.

This avoids scanning the entire matrix separately for every
column.

I also observed that MinHash is an approximation. For S1 and S4,
the true Jaccard similarity was 2/3, but their two-position
MinHash signatures matched completely, giving an estimate of 1.0.

This difference occurred because only two hash functions were
used. Using more hash functions can generally provide a more
stable similarity estimate.

### Banding Implementation

In `lsh_candidates()`, I divided each MinHash signature into bands
of equal size.

If the signature length was not divisible by the number of bands,
my implementation raised a ValueError.

I chose this approach to avoid silently discarding signature values
and to ensure that every band contains the same number of rows.

Document pairs that matched in at least one band were added to a
candidate set. Using a set prevented duplicate pairs from being stored.

## Task 2: Finding the Crossover

I compared Brute Force and LSH using five dataset sizes,
from 250 to 4,000 documents.

Brute Force was faster at 500 documents (0.90s vs. 1.26s),
but LSH became faster at 1,000 documents (1.52s vs. 3.54s).
Therefore, the crossover on my machine lies between
500 and 1,000 documents.

At 4,000 documents, Brute Force took 54.80 seconds and
performed 7,998,000 similarity comparisons. LSH took
3.04 seconds and performed only 229 comparisons.

I stopped at 4,000 documents because Brute Force took
nearly one minute. The results show that LSH's preprocessing
cost matters for small datasets, but reducing similarity
comparisons becomes more beneficial as the dataset grows.

Detailed measurements are recorded in out/curve.md and
out/crossover.json.

## Task 3: Finding Similar Pairs with Fewer Comparisons

### Implementation and Parameters

I implemented `YourFinder` using MinHash and LSH to reduce the
number of similarity comparisons.

My implementation uses the following parameters:

- Similarity threshold: 0.6
- Number of hash functions: 120
- Number of bands: 30
- Rows per band: 4

First, the program generates a 120-value MinHash signature for
each document.

Next, it divides each signature into 30 bands, with 4 values
per band. Documents that have identical values in at least
one band are selected as candidate pairs.

Finally, the program calculates the actual Jaccard similarity
only for these candidate pairs and returns pairs whose
similarity is at least 0.6.

I used a set to prevent duplicate candidate pairs from being
compared multiple times.

### Benchmark Results

I evaluated my implementation using `python3 bench.py --yours`.

The benchmark contained 2,120 documents and 121 truly similar
document pairs.

| Metric | Brute Force | My LSH Implementation |
|---|---:|---:|
| Similarity comparisons | 2,246,140 | 123 |
| Runtime | 7.73s | 0.49s |
| Recall | 100% | 100% |
| Precision | 100% | 100% |

My implementation reduced the number of similarity comparisons
from 2,246,140 to 123, avoiding approximately 99.99% of the
comparisons.

The algorithm checked 123 candidate pairs and returned the
121 pairs that met the similarity threshold.

It achieved 100% recall and precision in this benchmark,
meaning that it did not miss any truly similar pairs or
return any incorrect pairs in this test.

However, this result does not guarantee perfect recall on
every dataset, because LSH can miss pairs during candidate
selection.

### Parameter Selection and S-Curve

I used 120 hash functions and divided each signature into 30 bands
with 4 rows per band.

The approximate probability that two documents with similarity s
become a candidate pair is:

P(candidate) = 1 - (1 - s^r)^b

where:
- s = Jaccard similarity
- r = number of rows per band
- b = number of bands

With my parameters, the formula becomes:

P(candidate) = 1 - (1 - s^4)^30

The approximate S-curve threshold is:

t = (1 / b)^(1 / r)
  = (1 / 30)^(1 / 4)
  ≈ 0.427

My target similarity threshold is 0.6, which is above this
approximate S-curve threshold.

At s = 0.6, the theoretical candidate probability is approximately:

P(candidate) = 1 - (1 - 0.6^4)^30
             ≈ 0.984

I chose these parameters to make documents near the target
similarity threshold likely to become candidates.

This configuration favors recall, although it can also produce
additional candidate pairs that must be filtered using the
actual similarity function.

The probability formula is an approximation based on the usual
MinHash and LSH assumptions. Actual recall must be verified
through experiments.

### Banding Trade-off Experiment

I changed the number of bands from 30 to 15 while keeping
the total number of hash functions at 120.

| Parameter | Original | Modified |
|---|---:|---:|
| Hash functions | 120 | 120 |
| Bands | 30 | 15 |
| Rows per band | 4 | 8 |
| Similarity comparisons | 123 | 83 |
| Recall | 100% | 68.6% |
| Precision | 100% | 100% |

With 15 bands and 8 rows per band, the number of comparisons
decreased from 123 to 83. However, recall dropped from
100% to 68.6%.

The benchmark contained 121 truly similar pairs. The modified
configuration found only 83 of them and missed 38 pairs.

This happened because the modified configuration required
8 signature values to match within a band instead of 4,
making candidate selection more selective.

The experiment showed that reducing comparisons too aggressively
can cause LSH to miss genuinely similar pairs.

I restored the original configuration of 30 bands and 4 rows
per band because it achieved 100% recall in the benchmark
while still using only 123 similarity comparisons.