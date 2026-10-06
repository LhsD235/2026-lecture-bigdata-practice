# Observations

## Task 1

In the broken walk, rank at a dead end has nowhere to go and disappears. I
redistribute that dangling mass uniformly; uniform teleportation also lets a
surfer escape a spider trap, so the same uniform-jump mechanism repairs both.
Physically, beta is the probability of following a link, while `1 - beta` is
the probability of jumping to a uniformly chosen page.

## Task 2

As beta approached 1, convergence slowed from 14 to 24 iterations because less
teleportation gives weaker contraction. Increasing the graph from 1,200 to
20,000 nodes added only one iteration but made each iteration much slower because
it scans more nodes and edges. The top-10 set stayed fixed, but positions 7 and
8 first swapped at beta 0.70, so reported rankings should disclose beta.

## Task 3

I keep the supplied adjacency list and two length-n rank vectors instead of an
`n x n` matrix: `2n` floating values (2,400 here), with graph storage proportional
to `n + edges`. Teleport and dangling redistribution are uniform scalar offsets,
so one scalar is computed and applied while initializing the next rank vector;
no dense matrix is needed. The worst difference from the dense result was
`1.17e-15`, caused only by floating-point addition order.
