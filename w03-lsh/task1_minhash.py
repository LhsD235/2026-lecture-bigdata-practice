#!/usr/bin/env python3
"""Week 3 · Task 1 — Minhash and LSH, built from the matrix up.

Textbook §3.2 - §3.4.

Comparing every pair is quadratic, so it stops being possible somewhere around
a hundred thousand documents. The way out is two ideas stacked:

    minhash   replace a set with a short signature, such that the chance two
              signatures agree in a position equals their Jaccard similarity
    LSH       hash bands of those signatures so that similar pairs collide and
              you only ever compare the ones that did

You build both. The textbook's §3.3.5 example is small enough to check by hand,
and the harness checks you against it.

    python3 task1_minhash.py --verify
"""
import argparse

# §3.3.5. Rows are elements 0..4, columns are the sets S1..S4.(예제 행렬)
BOOK = [[1, 0, 0, 1],
        [0, 0, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 1, 1],
        [0, 0, 1, 0]]
# The two hash functions the textbook uses on the row numbers.
BOOK_HASHES = [lambda r: (r + 1) % 5, lambda r: (3 * r + 1) % 5]

#Jaccard Similarity: 두 집합에서의 교집합 / 합집합
def jaccard(a, b):
    """|a and b| / |a or b|. Empty union is 0, not an error."""
    union = a | b

    #에러를 발생하는게 아님
    if not union:
        return 0

    intersection = a & b
    return len(intersection) / len(union)

def minhash_signatures(columns, hashes, n_rows):
    """Build the signature matrix, one pass over the rows.

    `columns` is [set_of_row_numbers, ...], one entry per document.
    Return [[sig for each hash] for each column].
    """

    # 각 column마다 hash 개수만큼 signature 공간을 만든다.
    # 처음에는 어떤 값이 최소인지 모르므로 무한대로 초기화한다.
    signatures = [
        [float("inf")] * len(hashes)
        for _ in columns
    ]

    # row를 딱 한 번씩 순회.
    for r in range(n_rows):

        # 현재 row의 hash 값들을 한 번만 계산
        hash_values = [h(r) for h in hashes]

        # 현재 row가 들어 있는 column을 찾는다.
        for c, column in enumerate(columns):

            if r in column:

                # 해당 column의 각 hash signature 갱신
                for h_idx, hash_value in enumerate(hash_values):
                    signatures[c][h_idx] = min(
                        signatures[c][h_idx],
                        hash_value
                    )

    return signatures


def lsh_candidates(signatures, bands):
    """Split each signature into `bands` bands and hash each band.

    Two columns are candidates if they land in the same bucket for at least
    one band. Return {(i, j), ...} with i < j.
    """

    if not signatures:
        return set()

    sig_len = len(signatures[0])

    # signature 길이가 bands로 정확히 나누어지지 않으면 오류
    if sig_len % bands != 0:
        raise ValueError("signature length must divide evenly by bands")

    rows_per_band = sig_len // bands
    candidates = set()

    # band 하나씩 처리
    for band_idx in range(bands):
        buckets = {}

        start = band_idx * rows_per_band
        end = start + rows_per_band

        # 각 document(column)의 현재 band를 bucket에 넣기
        for doc_idx, signature in enumerate(signatures):
            band = tuple(signature[start:end])

            if band not in buckets:
                buckets[band] = []

            buckets[band].append(doc_idx)

        # 같은 bucket에 들어간 document들은 candidate
        for docs in buckets.values():
            for i in range(len(docs)):
                for j in range(i + 1, len(docs)):
                    candidates.add((docs[i], docs[j]))

    return candidates


# ------------------------------------------------------------------- harness
def columns_from_matrix(matrix):
    n_rows, n_cols = len(matrix), len(matrix[0])
    return [{r for r in range(n_rows) if matrix[r][c]} for c in range(n_cols)]


def verify():
    fails = 0

    def check(label, got, want):
        nonlocal fails
        ok = got == want
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:<44} {got}"
              + ("" if ok else f"\n{'':>54}want {want}"))
        fails += not ok

    cols = columns_from_matrix(BOOK)
    try:
        # S1 = {0,3}, S4 = {0,2,3}: intersection 2, union 3
        check("jaccard(S1, S4)", round(jaccard(cols[0], cols[3]), 4), round(2 / 3, 4))
        check("jaccard(S1, S2)", jaccard(cols[0], cols[1]), 0.0)
        check("jaccard on empty sets", jaccard(set(), set()), 0)
    except NotImplementedError:
        print("  jaccard is still a stub"); return 1

    try:
        sig = minhash_signatures(cols, BOOK_HASHES, len(BOOK))
    except NotImplementedError:
        print("  minhash_signatures is still a stub"); return 1

    # Figure 3.4 in the textbook.
    check("signature of S1", sig[0], [1, 0])
    check("signature of S2", sig[1], [3, 2])
    check("signature of S3", sig[2], [0, 0])
    check("signature of S4", sig[3], [1, 0])

    try:
        cands = lsh_candidates([[1, 0], [3, 2], [0, 0], [1, 0]], bands=2)
    except NotImplementedError:
        print("  lsh_candidates is still a stub"); return 1
    # With one row per band, S1 and S4 are identical, so they must collide.
    check("S1 and S4 are candidates", (0, 3) in cands, True)
    check("S1 and S2 are not", (0, 1) in cands, False)

    print(f"\n  {'all ok' if not fails else str(fails) + ' failed'}")
    if not fails:
        print("  Note that S1 and S4 agree in both signature positions, which "
              "estimates\n  their similarity as 1.0 when it is actually 2/3. "
              "Two hashes is not many.")
    return 1 if fails else 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    raise SystemExit(verify() if a.verify else p.print_help())
