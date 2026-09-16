#!/usr/bin/env python3
"""Week 3 · Task 3 — Find the same pairs without comparing everything.

Textbook §3.4.

`BruteForce` compares every pair. On 3,000 documents that is 4.5 million
comparisons and it is completely correct. On 3 million documents it is 4.5
trillion and it is completely useless.

Beat it. Find the same near-duplicate pairs while making far fewer comparisons.

    python3 bench.py
    python3 bench.py --yours

The harness counts every call you make to `similarity()`. That is your score.
It also checks **recall** - which of the truly similar pairs you found. Skipping
comparisons is easy; skipping comparisons without losing the pairs is the task.
"""
import random

class BruteForce:
    """Correct, and quadratic."""

    def __init__(self, threshold):
        self.threshold = threshold

    def find(self, docs, similarity):
        """docs is [set_of_shingles, ...]. Return {(i, j), ...} with i < j."""
        out = set()
        for i in range(len(docs)):
            for j in range(i + 1, len(docs)):
                if similarity(docs[i], docs[j]) >= self.threshold:
                    out.add((i, j))
        return out


class YourFinder:
    """LSH-based near-duplicate finder."""

    def __init__(self, threshold):
        self.threshold = threshold

        # 120 hashes = 30 bands * 4 rows per band
        self.num_hashes = 120
        self.bands = 30
        self.rows_per_band = self.num_hashes // self.bands

        # Hash function:
        # h(x) = (a*x + b) % prime
        self.prime = 4_294_967_311

        # 같은 실행마다 같은 hash 함수들이 만들어지도록 고정 seed 사용
        rng = random.Random(2026)

        self.hash_params = [
            (
                rng.randrange(1, self.prime),
                rng.randrange(0, self.prime)
            )
            for _ in range(self.num_hashes)
        ]

    def find(self, docs, similarity):
        if not docs:
            return set()

        # -------------------------------------------------
        # 1. 등장하는 모든 shingle의 hash 값을 미리 계산
        # -------------------------------------------------
        universe = set()

        for doc in docs:
            universe.update(doc)

        hashed = {}

        for x in universe:
            hashed[x] = [
                (a * x + b) % self.prime
                for a, b in self.hash_params
            ]

        # -------------------------------------------------
        # 2. 각 document의 MinHash signature 생성
        # -------------------------------------------------
        signatures = []

        for doc in docs:
            sig = [self.prime] * self.num_hashes

            for x in doc:
                hash_values = hashed[x]

                for h_idx, hash_value in enumerate(hash_values):
                    if hash_value < sig[h_idx]:
                        sig[h_idx] = hash_value

            signatures.append(sig)

        # -------------------------------------------------
        # 3. Banding → candidate pair 생성
        # -------------------------------------------------
        candidates = set()

        for band_idx in range(self.bands):
            buckets = {}

            start = band_idx * self.rows_per_band
            end = start + self.rows_per_band

            for doc_idx, sig in enumerate(signatures):

                # 현재 band의 signature 값
                band = tuple(sig[start:end])

                bucket = buckets.setdefault(band, [])

                # 이미 같은 bucket에 들어와 있는 문서와 candidate 생성
                for other_idx in bucket:
                    candidates.add((other_idx, doc_idx))

                bucket.append(doc_idx)

        # -------------------------------------------------
        # 4. Candidate에 대해서만 실제 Jaccard similarity 계산
        # -------------------------------------------------
        out = set()

        for i, j in candidates:
            if similarity(docs[i], docs[j]) >= self.threshold:
                out.add((i, j))

        return out