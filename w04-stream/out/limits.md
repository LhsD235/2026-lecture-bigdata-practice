# Task 2 — Exact Distinct vs. Flajolet-Martin

## Machine

* CPU: 13th Gen Intel Core i7-1360P
* Environment: Windows with WSL2 (Ubuntu)
* WSL-visible RAM: approximately 7.5 GiB
* Swap: approximately 2.0 GiB
* Other workload: VS Code, terminal, and normal Windows/WSL background processes were running during the experiment.

## Measurements

| Stream size (n) | Distinct | Exact time | Exact peak memory |  FM time | FM peak memory | FM / truth |
| --------------: | -------: | ---------: | ----------------: | -------: | -------------: | ---------: |
|         100,000 |   36,702 |     0.09 s |            3.9 MB |   8.65 s |        0.01 MB |      1.34x |
|         200,000 |   73,410 |     0.18 s |            5.8 MB |  17.42 s |        0.01 MB |      1.34x |
|         400,000 |  146,970 |     0.40 s |           11.6 MB |  35.18 s |        0.01 MB |      1.34x |
|       1,600,000 |  587,625 |     1.60 s |           46.6 MB | 141.53 s |        0.01 MB |      1.78x |

## Exact-limit experiment

I continued testing the exact-set implementation separately in order to find where it became unpleasant on my machine.

| Stream size (n) |  Distinct | Exact time | Exact peak memory |
| --------------: | --------: | ---------: | ----------------: |
|       6,400,000 | 2,349,909 |     7.62 s |          188.4 MB |
|      25,600,000 | 9,399,592 |    34.79 s |          756.5 MB |

I stopped at **25,600,000 stream items**.

At this point, the exact implementation required about **756.5 MB of peak memory** and **34.79 seconds** for a single run. The program did not run out of RAM, but the experiment had become inconvenient for repeated testing because both execution time and memory usage had grown significantly.

Neither resource was exhausted. I stopped because the 34.79-second runtime had become inconvenient for repeated experiments, while memory had also grown to 756.5 MB and continued to scale approximately linearly.

## Memory growth

The exact set's peak memory increased as the stream size increased:

* 100,000 items: 3.9 MB
* 400,000 items: 11.6 MB
* 1,600,000 items: 46.6 MB
* 6,400,000 items: 188.4 MB
* 25,600,000 items: 756.5 MB

From 1,600,000 to 25,600,000 items, the stream size increased by **16x**.

Over the same range, exact peak memory increased from **46.6 MB to 756.5 MB**, which is approximately **16.2x**.

Therefore, the exact set shows approximately linear memory growth as the number of processed items increases.

Flajolet-Martin behaved differently. Across the recorded benchmark sizes, its measured peak memory remained approximately **0.01 MB**.

This shows the main difference between the two approaches:

* The exact set uses memory that grows with the number of distinct items.
* Flajolet-Martin keeps a fixed amount of state, so its memory usage remains approximately constant as the stream grows.

## Flajolet-Martin accuracy

The measured ratios between the FM estimate and the true number of distinct items were:

* n = 100,000: 1.34x
* n = 200,000: 1.34x
* n = 400,000: 1.34x
* n = 1,600,000: 1.78x

The estimate did not consistently become more accurate as the stream size increased.

For the first three measurements, FM overestimated the true value by approximately 1.34x. At 1,600,000 items, the estimate was less accurate and reached 1.78x.

This demonstrates the trade-off of Flajolet-Martin: it uses bounded memory, but its distinct-count estimate is approximate and can fluctuate.
