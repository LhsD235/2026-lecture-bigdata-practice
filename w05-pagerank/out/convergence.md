# PageRank Convergence Measurements

## Environment

- CPU: 13th Gen Intel(R) Core(TM) i7-1360P
- RAM: 15.6 GiB usable physical memory
- OS: Windows 11 10.0.26200 (the implementation is standard Python and is also runnable in Ubuntu/WSL)
- Python: 3.12.14
- Other load: Codex desktop and ordinary background services; no deliberate CPU-heavy workload

Wall-clock timings are specific to this run and machine. Iteration counts are the
more reproducible result.

## A1-A3: beta

All rows below use 1,200 nodes and L1 tolerance `1e-10`.

| beta | iterations | seconds | first three |
|---:|---:|---:|---|
| 0.50 | 14 | 0.0194 | p00009, p00001, p00006 |
| 0.70 | 17 | 0.0160 | p00009, p00001, p00006 |
| 0.85 | 20 | 0.0165 | p00009, p00001, p00006 |
| 0.95 | 23 | 0.0244 | p00009, p00001, p00006 |
| 0.99 | 24 | 0.0220 | p00009, p00001, p00006 |

The iteration count rises as beta approaches 1. Teleportation contracts rank
differences; reducing its probability makes the iteration behave more like the
raw link walk, so the subdominant modes decay more slowly. Timing is noisy at
this small scale, but the iteration trend is monotone.

## A4: graph size

Both sizes use tolerance `1e-10`; 20,000 is 16.7 times 1,200.

| beta | nodes | iterations | seconds | time ratio vs. 1,200 |
|---:|---:|---:|---:|---:|
| 0.85 | 1,200 | 20 | 0.0165 | 1.0x |
| 0.85 | 20,000 | 21 | 0.3661 | 22.2x |
| 0.95 | 1,200 | 23 | 0.0244 | 1.0x |
| 0.95 | 20,000 | 24 | 0.4113 | 16.8x |

The iteration count changed by only one in each comparison: convergence rate is
mainly a property of beta and graph structure, not simply the number of nodes.
Wall time grew strongly because every iteration scans all nodes and edges.

## A5: tolerance

These rows use beta `0.85` and 1,200 nodes.

| tolerance | iterations | seconds |
|---:|---:|---:|
| 1e-6 | 12 | 0.0091 |
| 1e-10 | 20 | 0.0165 |

Four extra decimal digits cost eight extra iterations in this experiment, or
about two iterations per digit on average.

## A6: top 10 versus beta

At beta `0.50`:

`p00009, p00001, p00006, p00005, p00003, p00002, p00000, p00004, p00007, p00008`

At beta `0.70` and every measured beta above it:

`p00009, p00001, p00006, p00005, p00003, p00002, p00004, p00000, p00007, p00008`

The set of ten pages did not change, and the first six stayed fixed. The first
ordering change occurred at beta `0.70`, where `p00004` and `p00000` exchanged
seventh and eighth place. Thus the head of this ranking is robust, but even a
reasonable beta choice can change close positions; published ranks should state
the beta used.
