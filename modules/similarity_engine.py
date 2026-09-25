"""
Similarity Detection Engine for CivicPulse AI.
Leverages scikit-learn TF-IDF Vectorization and Cosine Similarity
to discover potentially similar/duplicate complaints across historical data.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .text_processing import clean_text


class SimilarityEngine:
    """
    Computes text vector embeddings using TF-IDF and evaluates
    cosine similarity to detect potentially duplicate or related complaints.
    """

    def __init__(self, similarity_threshold: float = 0.35):
        """
        Args:
            similarity_threshold: Minimum cosine similarity score (0.0 to 1.0)
                                  to classify a record as potentially similar.
        """
        self.similarity_threshold = similarity_threshold

    def find_similar(
        self,
        new_title: str,
        new_description: str,
        existing_complaints: List[Dict[str, Any]],
        new_location: str = "",
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Compares new complaint text against existing complaints.
        
        Returns:
            {
                "similar_count": int,
                "top_score": float,
                "top_complaint_id": str,
                "has_similar": bool,
                "matches": [
                    {
                        "complaint_id": "CP-2026-0001",
                        "title": "...",
                        "similarity_score": 0.87,
                        "similarity_percentage": 87.0,
                        "category": "Electrical",
                        "status": "Pending",
                        "location": "EEE Lab 2",
                        "label": "Potentially similar complaint",
                        "created_at": "..."
                    }, ...
                ]
            }
        """
        if not existing_complaints:
            return {
                "similar_count": 0,
                "top_score": 0.0,
                "top_complaint_id": "",
                "has_similar": False,
                "matches": []
            }

        # Prepare query text
        query_text = clean_text(f"{new_title} {new_description} {new_location}")
        if not query_text.strip():
            return {
                "similar_count": 0,
                "top_score": 0.0,
                "top_complaint_id": "",
                "has_similar": False,
                "matches": []
            }

        # Prepare corpus texts
        corpus = []
        valid_indices = []
        for idx, comp in enumerate(existing_complaints):
            c_title = comp.get("title", "")
            c_desc = comp.get("description", "")
            c_loc = comp.get("location", "")
            combined = clean_text(f"{c_title} {c_desc} {c_loc}")
            if combined.strip():
                corpus.append(combined)
                valid_indices.append(idx)

        if not corpus:
            return {
                "similar_count": 0,
                "top_score": 0.0,
                "top_complaint_id": "",
                "has_similar": False,
                "matches": []
            }

        try:
            # Fit TF-IDF on corpus + query
            vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                sublinear_tf=True,
                max_features=10000
            )
            all_texts = [query_text] + corpus
            tfidf_matrix = vectorizer.fit_transform(all_texts)

            query_vector = tfidf_matrix[0:1]
            corpus_vectors = tfidf_matrix[1:]

            # Compute Cosine Similarities
            similarities = cosine_similarity(query_vector, corpus_vectors)[0]

            matches = []
            for rank_idx, score in enumerate(similarities):
                if score >= self.similarity_threshold:
                    original_record = existing_complaints[valid_indices[rank_idx]]
                    
                    # Boost slightly if locations match exactly
                    final_score = float(score)
                    if new_location and original_record.get("location"):
                        if new_location.strip().lower() == original_record.get("location", "").strip().lower():
                            final_score = min(1.0, final_score + 0.05)

                    matches.append({
                        "complaint_id": original_record.get("complaint_id", ""),
                        "title": original_record.get("title", ""),
                        "description": original_record.get("description", ""),
                        "similarity_score": round(final_score, 3),
                        "similarity_percentage": round(final_score * 100, 1),
                        "category": original_record.get("category", "Other"),
                        "location": original_record.get("location", ""),
                        "status": original_record.get("status", "Pending"),
                        "priority": original_record.get("priority", "Medium"),
                        "created_at": original_record.get("created_at", ""),
                        "label": "Potentially similar complaint"
                    })

            # Sort matches descending by similarity score
            matches.sort(key=lambda m: m["similarity_score"], reverse=True)
            matches = matches[:top_k]

            top_score = matches[0]["similarity_score"] if matches else 0.0
            top_complaint_id = matches[0]["complaint_id"] if matches else ""

            return {
                "similar_count": len(matches),
                "top_score": top_score,
                "top_complaint_id": top_complaint_id,
                "has_similar": len(matches) > 0,
                "matches": matches
            }

        except Exception as e:
            # Fallback gracefully if any vectorization error occurs
            return {
                "similar_count": 0,
                "top_score": 0.0,
                "top_complaint_id": "",
                "has_similar": False,
                "matches": [],
                "error": str(e)
            }


# Singleton helper
_similarity_instance: Optional[SimilarityEngine] = None

def get_similarity_engine() -> SimilarityEngine:
    """Returns singleton SimilarityEngine instance."""
    global _similarity_instance
    if _similarity_instance is None:
        _similarity_instance = SimilarityEngine()
    return _similarity_instance
