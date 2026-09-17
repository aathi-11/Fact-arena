from typing import List, Dict, Any
import numpy as np
from rank_bm25 import BM25Okapi
import faiss
from sentence_transformers import SentenceTransformer

_EMBEDDER = None

def get_embedder():
    global _EMBEDDER
    if _EMBEDDER is None:
        _EMBEDDER = SentenceTransformer("all-MiniLM-L6-v2")
    return _EMBEDDER

def build_faiss_index(docs: List[str]):
    embedder = get_embedder()
    embeddings = embedder.encode(docs, convert_to_numpy=True)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    return index, embeddings

def bm25_search(query: str, docs: List[str], k: int = 5) -> List[int]:
    tokenized_corpus = [doc.lower().split() for doc in docs]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)
    top_k_indices = np.argsort(scores)[::-1][:k]
    return top_k_indices.tolist()

def dense_search(query: str, index, k: int = 5) -> List[int]:
    embedder = get_embedder()
    query_vector = embedder.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_vector)
    _, indices = index.search(query_vector, k)
    return indices[0].tolist()

def reciprocal_rank_fusion(dense_ranks: List[int], bm25_ranks: List[int], c: int = 60) -> List[int]:
    scores: Dict[int, float] = {}
    
    for rank, doc_id in enumerate(dense_ranks):
        scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (c + rank + 1)
        
    for rank, doc_id in enumerate(bm25_ranks):
        scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (c + rank + 1)
        
    sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [doc_id for doc_id, _ in sorted_docs]

def hybrid_search(query: str, docs: List[str], k: int = 5) -> List[str]:
    if not docs:
        return []
    index, _ = build_faiss_index(docs)
    dense_indices = dense_search(query, index, k=min(k, len(docs)))
    bm25_indices = bm25_search(query, docs, k=min(k, len(docs)))
    fused_indices = reciprocal_rank_fusion(dense_indices, bm25_indices)
    return [docs[idx] for idx in fused_indices[:k]]
