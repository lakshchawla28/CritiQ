"""
apps/recommendations/ml/engine.py

AI-powered recommendation engine (embeddings-based).
Primary flow:
 - Build movie embeddings (using SentenceTransformer if available, else TF-IDF)
 - Build user profile embeddings (weighted average of movie embeddings by user ratings)
 - For each user compute top-N nearest movies (cosine similarity)
 - Save recommendations to DB (apps.recommendations.models.Recommendation)

Notes:
 - This file persists embeddings to disk (npy) under the app's ml_data/ directory.
 - Requirements (install in your venv):
     pip install numpy scikit-learn pandas
     pip install sentence-transformers  # optional but recommended for quality
     pip install faiss-cpu               # optional for large scale nearest neighbor
"""

import os
import logging
import json
from pathlib import Path
from typing import List, Tuple, Optional

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from django.conf import settings
from django.db import transaction

# Try optional higher-quality embedding model
USE_TRANSFORMERS = False
try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None
    USE_TRANSFORMERS = False

# Models
from apps.movies.models import Movie, UserMovieInteraction
from apps.authentication.models import User
from apps.recommendations.models import Recommendation

logger = logging.getLogger(__name__)

# Storage paths
BASE_DIR = Path(__file__).resolve().parent
ML_DATA_DIR = BASE_DIR / "ml_data"
ML_DATA_DIR.mkdir(parents=True, exist_ok=True)

MOVIE_IDX_PATH = ML_DATA_DIR / "movie_index.json"       # maps idx->movie_id
MOVIE_EMB_PATH = ML_DATA_DIR / "movie_embeddings.npy"  # embeddings matrix
VECTORIZER_PATH = ML_DATA_DIR / "tfidf_vectorizer.pkl" # optional (not pickled in this file)


# Configuration
EMBEDDING_DIM = 384 if USE_TRANSFORMERS and SentenceTransformer is not None else None
TFIDF_MAX_FEATURES = 20_000
DEFAULT_TOP_K = 20

# Rating mapping (same as elsewhere)
RATING_MAP = {
    "trash": 1.0,
    "timepass": 2.0,
    "worth": 3.0,
    "peak": 4.0,
}


class EmbeddingBackend:
    """
    Wrapper that either uses SentenceTransformer (if installed) or TF-IDF.
    """

    def __init__(self, model_name: Optional[str] = "all-MiniLM-L6-v2"):
        self.use_transformer = USE_TRANSFORMERS and SentenceTransformer is not None
        self.model_name = model_name
        self.tfidf_vectorizer = None
        self.transformer = None

        if self.use_transformer:
            try:
                self.transformer = SentenceTransformer(self.model_name)
                logger.info(f"Loaded SentenceTransformer: {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to load SentenceTransformer ({e}), falling back to TF-IDF")
                self.use_transformer = False
                self.transformer = None

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Returns an (N, D) numpy array of embeddings.
        If transformer available -> use it. Otherwise -> TF-IDF vectors (dense).
        """
        if self.use_transformer and self.transformer is not None:
            # SentenceTransformer returns numpy
            embeddings = self.transformer.encode(texts, show_progress_bar=True, convert_to_numpy=True)
            return embeddings.astype(np.float32)
        else:
            # TF-IDF fallback
            if self.tfidf_vectorizer is None:
                self.tfidf_vectorizer = TfidfVectorizer(max_features=TFIDF_MAX_FEATURES, stop_words='english')
                X = self.tfidf_vectorizer.fit_transform(texts)
            else:
                X = self.tfidf_vectorizer.transform(texts)

            dense = X.toarray().astype(np.float32)
            return dense


class RecommendationEngine:
    """
    Main engine for embeddings-based recommendations.
    """

    def __init__(self, backend: Optional[EmbeddingBackend] = None):
        self.backend = backend or EmbeddingBackend()
        self.movie_index = []     # list of movie_id (order matches embeddings rows)
        self.movie_embeddings = None  # numpy array (N_movies, D)
        self._load_index_and_embeddings()

    # ---------------------------
    # Persistence helpers
    # ---------------------------
    def _save_index_and_embeddings(self):
        """Persist movie index (json) and embeddings (npy) to disk."""
        try:
            with open(MOVIE_IDX_PATH, "w", encoding="utf-8") as f:
                json.dump(self.movie_index, f)
            if self.movie_embeddings is not None:
                np.save(MOVIE_EMB_PATH, self.movie_embeddings)
            logger.info("Saved movie index and embeddings to disk.")
        except Exception as e:
            logger.exception("Failed to save embeddings/index: %s", e)

    def _load_index_and_embeddings(self):
        """Load persisted index and embeddings if available."""
        try:
            if MOVIE_IDX_PATH.exists() and MOVIE_EMB_PATH.exists():
                with open(MOVIE_IDX_PATH, "r", encoding="utf-8") as f:
                    self.movie_index = json.load(f)
                self.movie_embeddings = np.load(MOVIE_EMB_PATH)
                logger.info("Loaded persisted movie embeddings: %d movies", len(self.movie_index))
            else:
                self.movie_index = []
                self.movie_embeddings = None
        except Exception as e:
            logger.exception("Failed to load persisted embeddings/index: %s", e)
            self.movie_index = []
            self.movie_embeddings = None

    # ---------------------------
    # Building movie corpus & embeddings
    # ---------------------------
    def _build_movie_corpus(self) -> Tuple[List[str], List[str]]:
        """
        Build textual corpus for movies.
        Returns:
            movie_ids, corpus_texts
        """
        movies_qs = Movie.objects.all().only("id", "title", "overview", "genres")
        movie_ids = []
        texts = []

        for mv in movies_qs:
            movie_ids.append(str(mv.id))
            # create a short corpus string: title + overview + genre names (ids are fine too)
            title = mv.title or ""
            overview = mv.overview or ""
            genres = ""
            try:
                # genres might be list of ids; join them to string
                if isinstance(mv.genres, (list, tuple)):
                    genres = " ".join([str(g) for g in mv.genres])
                else:
                    genres = str(mv.genres)
            except Exception:
                genres = ""

            text = " . ".join([title, overview, genres])
            texts.append(text)

        return movie_ids, texts

    def build_movie_embeddings(self, force: bool = False):
        """
        Build movie embeddings and persist them.
        Set force=True to rebuild from scratch.
        """
        # If already built and not forced, skip
        if self.movie_embeddings is not None and not force:
            logger.info("Movie embeddings already exist; skipping build (set force=True to rebuild).")
            return

        movie_ids, corpus = self._build_movie_corpus()

        if not movie_ids:
            logger.warning("No movies found to build embeddings.")
            return

        logger.info("Building embeddings for %d movies (transformer=%s).", len(movie_ids), self.backend.use_transformer)
        embs = self.backend.embed_texts(corpus)

        # Normalize embeddings to unit vectors for cosine similarity
        norms = np.linalg.norm(embs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        embs = embs / norms

        self.movie_index = movie_ids
        self.movie_embeddings = embs.astype(np.float32)
        self._save_index_and_embeddings()
        logger.info("Built and saved movie embeddings.")

    # ---------------------------
    # User profile embedding
    # ---------------------------
    def _build_user_profile(self, user: User) -> Optional[np.ndarray]:
        """
        Build a single vector representing user's preferences by weighted average of
        embeddings of movies they rated / interacted with.
        Returns normalized embedding vector or None if not enough info.
        """
        interactions = UserMovieInteraction.objects.filter(
            user=user
        ).exclude(rating__isnull=True).select_related("movie")

        if not interactions.exists():
            # fallback: if user has some watched movies without rating, use them with small weight
            interactions = UserMovieInteraction.objects.filter(user=user, is_watched=True).select_related("movie")
            if not interactions.exists():
                return None

        movie_id_to_idx = {m_id: idx for idx, m_id in enumerate(self.movie_index)}
        vecs = []
        weights = []

        for it in interactions:
            m_id = str(it.movie_id)
            idx = movie_id_to_idx.get(m_id)
            if idx is None:
                # movie not in embeddings (maybe newly added) -> skip
                continue
            emb = self.movie_embeddings[idx]
            rating = 0.0
            if it.rating:
                rating = float(RATING_MAP.get(it.rating, 0.0))
            else:
                rating = 1.0 if it.is_watched else 0.5

            vecs.append(emb * rating)
            weights.append(rating)

        if not vecs:
            return None

        stacked = np.vstack(vecs)
        weights_arr = np.array(weights).reshape(-1, 1)
        weighted = (stacked * weights_arr).sum(axis=0) / (weights_arr.sum() if weights_arr.sum() != 0 else 1.0)

        # normalize
        norm = np.linalg.norm(weighted)
        if norm == 0:
            return None
        return (weighted / norm).astype(np.float32)

    # ---------------------------
    # Recommendation for a user
    # ---------------------------
    def recommend_for_user(self, user: User, top_k: int = DEFAULT_TOP_K) -> List[Tuple[str, float]]:
        """
        Returns list of (movie_id, score) recommended for the user.
        Does NOT write to DB. Use generate_and_save_for_user to persist.
        """
        if self.movie_embeddings is None:
            logger.info("Movie embeddings missing, building now.")
            self.build_movie_embeddings(force=False)

        user_vec = self._build_user_profile(user)
        if user_vec is None:
            logger.info("Not enough user data to build profile for user %s", user.id)
            return []

        # compute cosine similarity between user_vec and all movie embeddings
        scores = cosine_similarity(user_vec.reshape(1, -1), self.movie_embeddings).reshape(-1)
        # get top indices sorted
        top_idx = np.argsort(scores)[::-1]

        # filter out movies user already interacted with (watched or rating) to avoid recommending them
        interacted_movie_ids = set(UserMovieInteraction.objects.filter(user=user).values_list("movie_id", flat=True))
        recommendations = []
        for idx in top_idx:
            movie_id = self.movie_index[int(idx)]
            if movie_id in [str(x) for x in interacted_movie_ids]:
                continue
            score = float(scores[int(idx)])
            recommendations.append((movie_id, score))
            if len(recommendations) >= top_k:
                break

        return recommendations

    # ---------------------------
    # Save recommendations to DB
    # ---------------------------
    def save_user_recommendations(self, user: User, recs: List[Tuple[str, float]], reason: str = "ai_embedding"):
        """
        Writes recommendations for a single user to DB. Uses update_or_create for idempotency.
        """
        if not recs:
            logger.info("No recommendations to save for user %s", user.id)
            return

        # Convert movie id strings to actual Movie FK references when creating objects
        from apps.movies.models import Movie as MovieModel
        with transaction.atomic():
            for movie_id, score in recs:
                try:
                    movie_obj = MovieModel.objects.get(id=movie_id)
                except MovieModel.DoesNotExist:
                    logger.debug("Movie %s not found in DB when saving recommendation", movie_id)
                    continue

                Recommendation.objects.update_or_create(
                    user=user,
                    movie=movie_obj,
                    defaults={
                        "score": float(score),
                        "reason": reason,
                    }
                )

    # ---------------------------
    # Bulk generate & save recommendations for all users
    # ---------------------------
    def generate_recommendations_for_all(self, top_k: int = DEFAULT_TOP_K, force_rebuild_embeddings: bool = False):
        """
        Compute and persist recommendations for every active user.
        """
        logger.info("Starting generate_recommendations_for_all: top_k=%d force_rebuild=%s", top_k, force_rebuild_embeddings)
        if force_rebuild_embeddings or self.movie_embeddings is None:
            self.build_movie_embeddings(force=True)

        users = User.objects.filter(is_active=True)  # optionally filter is_verified if you have that flag
        count = 0
        for user in users.iterator():
            recs = self.recommend_for_user(user, top_k=top_k)
            self.save_user_recommendations(user, recs, reason="ai_embedding")
            count += 1

        logger.info("Generated recommendations for %d users", count)
        return count

    # ---------------------------
    # Utility: refresh only new/changed movies (optional)
    # ---------------------------
    def upsert_movie_embeddings_for_new_movies(self):
        """
        Add embeddings for movies that are in DB but not yet in self.movie_index
        Useful for incremental updates without rebuilding whole matrix.
        """
        movie_ids_db = [str(m.id) for m in Movie.objects.only("id")]
        missing = [mid for mid in movie_ids_db if mid not in self.movie_index]
        if not missing:
            logger.info("No new movies to embed.")
            return 0

        logger.info("Embedding %d new movies", len(missing))
        # Build their corpus
        new_texts = []
        for mid in missing:
            mv = Movie.objects.get(id=mid)
            title = mv.title or ""
            overview = mv.overview or ""
            genres = ""
            if isinstance(mv.genres, (list, tuple)):
                genres = " ".join([str(g) for g in mv.genres])
            else:
                genres = str(mv.genres)
            new_texts.append(" . ".join([title, overview, genres]))

        new_embs = self.backend.embed_texts(new_texts)
        norms = np.linalg.norm(new_embs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        new_embs = (new_embs / norms).astype(np.float32)

        # append
        if self.movie_embeddings is None:
            self.movie_embeddings = new_embs
            self.movie_index = missing
        else:
            self.movie_embeddings = np.vstack([self.movie_embeddings, new_embs])
            self.movie_index.extend(missing)

        self._save_index_and_embeddings()
        logger.info("Upserted %d movie embeddings.", len(missing))
        return len(missing)
