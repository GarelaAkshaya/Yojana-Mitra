from __future__ import annotations

import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.embeddings.bge_encoder import LocalEncoder
from backend.retrieval.faiss_index import VectorIndex


def main() -> None:
    encoder = LocalEncoder()
    sample = ["Eligibility income below two lakh rupees and age 18 to 35."] * 25
    start = time.perf_counter()
    vectors = encoder.encode(sample)
    embed_ms = (time.perf_counter() - start) * 1000 / len(sample)

    index = VectorIndex()
    index.save_vectors({idx + 1: vector for idx, vector in enumerate(vectors)})
    start = time.perf_counter()
    index.search(vectors[0], top_k=5)
    search_ms = (time.perf_counter() - start) * 1000

    print(f"embedding_ms_per_chunk={embed_ms:.2f}")
    print(f"vector_search_ms={search_ms:.2f}")


if __name__ == "__main__":
    main()
