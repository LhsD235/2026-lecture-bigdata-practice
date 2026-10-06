#!/usr/bin/env python3
"""Week 5 · Task 3 — PageRank on a graph that will not fit as a matrix.

Textbook §5.2 (efficient PageRank), §5.2.1 - §5.2.3.

`DenseMatrix` is PageRank written the way the equations are written: build the
transition matrix M, multiply. It is correct, it is easy to read, and it stores
n^2 numbers for a graph with almost no edges.

The web's matrix is about 99.9999% zeros. Storing them is the problem, and
§5.2 is the chapter about not doing that.

    python3 bench.py
    python3 bench.py --yours

Correctness first: the harness compares your ranks against the dense version
element by element. A fast PageRank that ranks pages differently is a different
algorithm, not a faster one.
"""


class DenseMatrix:
    """PageRank as written in the equations. Stores n^2 floats."""

    def __init__(self, beta=0.85, tol=1e-10, max_iter=100):
        self.beta, self.tol, self.max_iter = beta, tol, max_iter

    def run(self, graph):
        nodes = list(graph)
        n = len(nodes)
        index = {v: i for i, v in enumerate(nodes)}

        # the full transition matrix, zeros and all
        M = [[0.0] * n for _ in range(n)]
        for v, outs in graph.items():
            if outs:
                share = 1.0 / len(outs)
                for w in outs:
                    M[index[w]][index[v]] = share
            else:
                for i in range(n):           # dead end: spread it everywhere
                    M[i][index[v]] = 1.0 / n

        r = [1.0 / n] * n
        for self.iterations in range(1, self.max_iter + 1):
            nr = [0.0] * n
            for i in range(n):
                row = M[i]
                s = 0.0
                for j in range(n):
                    if row[j]:
                        s += row[j] * r[j]
                nr[i] = self.beta * s + (1 - self.beta) / n
            delta = sum(abs(a - b) for a, b in zip(nr, r))
            r = nr
            if delta < self.tol:
                break
        return {v: r[index[v]] for v in nodes}

    def memory_floats(self):
        return getattr(self, "_n", 0) ** 2


class YourPageRank:
    """Your PageRank.

        __init__(beta=0.85, tol=1e-10, max_iter=100)
        run(graph) -> {node: rank}
        memory_floats() -> the largest number of floats you held at once

    Same ranks, to within 1e-9 per node. Far less memory.

    `graph` is {node: [out-neighbours]}. Note what that already is: an adjacency
    list, which is the sparse representation. The dense version throws that
    structure away and then pays to get it back.

    Two things to be careful about, and they are the same two as Task 1:

      * dead ends, whose rank has to go somewhere
      * the teleport term, which touches every node and is therefore the one
        part that looks like it needs a dense operation - it does not, and
        working out why is the point of §5.2.3

    `memory_floats()` is on your honour and the harness reads it. Count the
    numbers you actually hold at once.
    """

    def __init__(self, beta=0.85, tol=1e-10, max_iter=100):
        if not 0.0 <= beta <= 1.0:
            raise ValueError("beta must be between 0 and 1")
        if tol < 0:
            raise ValueError("tol must be non-negative")
        if max_iter < 0:
            raise ValueError("max_iter must be non-negative")
        self.beta, self.tol, self.max_iter = beta, tol, max_iter
        self.iterations = 0
        self._memory_floats = 0

    def run(self, graph):
        nodes = list(graph)
        n = len(nodes)
        if n == 0:
            self.iterations = 0
            self._memory_floats = 0
            return {}

        node_set = set(nodes)
        for source, outs in graph.items():
            unknown = set(outs) - node_set
            if unknown:
                raise ValueError(
                    f"{source!r} links to unknown nodes: {sorted(unknown)!r}"
                )

        # The graph is already sparse. Keep it as an adjacency list and hold
        # only the current and next rank vector (2n floating-point values).
        ranks = {node: 1.0 / n for node in nodes}
        self._memory_floats = 2 * n
        self.iterations = 0

        for step in range(1, self.max_iter + 1):
            dangling_rank = sum(ranks[node] for node in nodes if not graph[node])
            uniform = ((1.0 - self.beta) + self.beta * dangling_rank) / n
            new_ranks = {node: uniform for node in nodes}

            for source in nodes:
                outs = graph[source]
                if not outs:
                    continue
                contribution = self.beta * ranks[source] / len(outs)
                for target in outs:
                    new_ranks[target] += contribution

            delta = sum(abs(new_ranks[node] - ranks[node]) for node in nodes)
            ranks = new_ranks
            self.iterations = step
            if delta < self.tol:
                break

        return ranks

    def memory_floats(self):
        return self._memory_floats
