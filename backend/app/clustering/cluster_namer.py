import logging
from collections import Counter
from typing import Dict, List

from app.models.cluster_summary import ClusterSummary

logger = logging.getLogger(__name__)

CLUSTER_NAME_CAP: int = 50

_UPPERCASE_ACRONYMS = {
    "vpn", "dns", "dhcp", "ssl", "tls", "ssh", "ftp", "api", "http", "https",
    "ldap", "mfa", "2fa", "sso", "saml", "iam", "rbac", "acl", "ids", "ips",
    "siem", "edr", "sql", "cpu", "ram", "gpu", "os", "pc", "vm", "ad", "gpo",
    "ou", "aws", "gcp", "ui", "ux", "ci", "cd", "qa", "uat",
}

_STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "shall", "that", "this",
    "these", "those", "it", "its", "we", "they", "them", "their", "our",
    "your", "my", "his", "her", "i", "he", "she", "you", "who", "which",
    "when", "where", "how", "what", "all", "each", "both", "few", "more",
    "most", "other", "some", "such", "than", "too", "very", "just", "also",
    "so", "if", "then", "about", "above", "after", "again", "against",
    "any", "because", "before", "between", "during", "into", "through",
    "under", "until", "up", "while",
}


def _format_cluster_name(phrase: str) -> str:
    words = phrase.strip().split()
    titled = []
    for word in words:
        if word.lower() in _UPPERCASE_ACRONYMS:
            titled.append(word.upper())
        else:
            titled.append(word.capitalize())
    return " ".join(titled) + " Issues"


def _frequency_name(texts: List[str]) -> str:
    counter: Counter = Counter()
    for text in texts:
        tokens = text.lower().split()
        counter.update(t for t in tokens if t not in _STOP_WORDS and len(t) > 2)
    top = [w for w, _ in counter.most_common(2)]
    phrase = " ".join(top) if top else "General"
    return _format_cluster_name(phrase)


class ClusterNamer:
    """
    Assigns human-readable cluster names using fast, deterministic
    token-frequency analysis.

    This is the DEFAULT naming strategy used in the core 3R processing
    pipeline. It does NOT use KeyBERT or any ML model.

    Placed after ClusterAnalyzer, before RecurrenceDetector.
    """

    def name_clusters(
        self,
        cluster_summaries: List[ClusterSummary],
        combined_texts: List[str],
        cluster_labels: List[int],
    ) -> List[ClusterSummary]:
        cluster_texts: Dict[int, List[str]] = {}
        for text, label in zip(list(combined_texts), list(cluster_labels)):
            if label == -1:
                continue
            cluster_texts.setdefault(label, []).append(text)

        logger.info("Naming %d clusters (standard/frequency)...", len(cluster_summaries))

        for summary in cluster_summaries:
            cid = summary.cluster_id
            texts = cluster_texts.get(cid, [])
            if not texts:
                object.__setattr__(summary, "cluster_name", "Unknown Issues")
                continue

            sample = texts[:CLUSTER_NAME_CAP]
            name = _frequency_name(sample)
            object.__setattr__(summary, "cluster_name", name)

        logger.info("Standard cluster naming completed.")
        return cluster_summaries


# ======================================================================
# AI CLUSTER NAMER — Optional KeyBERT enrichment
# ======================================================================
# KeyBERT is lazily imported ONLY when AIClusterNamer is instantiated.
# This class is NEVER used in the core processing pipeline.
# ======================================================================

KEYBERT_TOP_N: int = 3
KEYBERT_DIVERSITY: float = 0.5


class AIClusterNamer:
    """
    AI-powered cluster naming using KeyBERT.

    This class is used ONLY for optional enrichment AFTER core pipeline
    processing is complete. It is never part of the critical path.

    KeyBERT is lazily loaded on first use to avoid import cost at startup.
    """

    def __init__(self):
        self._kw_model = None
        self._available = None  # None = unknown, True/False after check

    def _get_kw_model(self):
        if self._kw_model is not None:
            return self._kw_model

        try:
            from keybert import KeyBERT
            from sentence_transformers import SentenceTransformer
            from app.config.settings import settings

            logger.info("Loading KeyBERT model: %s", settings.EMBEDDING_MODEL)
            st_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            self._kw_model = KeyBERT(model=st_model)
            self._available = True
            logger.info("KeyBERT model loaded for AI enrichment.")
        except Exception as exc:
            self._available = False
            logger.error("KeyBERT unavailable for AI enrichment: %s", exc)
            raise RuntimeError(
                f"AI cluster naming dependency (KeyBERT) is unavailable: {exc}"
            ) from exc

        return self._kw_model

    @property
    def is_available(self) -> bool:
        """Check if KeyBERT can be loaded without actually loading it."""
        if self._available is not None:
            return self._available
        try:
            import keybert  # noqa: F401
            self._available = True
        except ImportError:
            self._available = False
        return self._available

    def generate_ai_names(
        self,
        cluster_texts: Dict[int, List[str]],
        cancelled_check=None,
    ) -> Dict[int, str]:
        """
        Generate AI-powered cluster names for the given cluster texts.

        Parameters
        ----------
        cluster_texts : Dict[int, List[str]]
            Mapping of cluster_id -> list of combined_text strings.
        cancelled_check : callable, optional
            A callable that returns True if the job has been cancelled.
            Checked between clusters for cooperative cancellation.

        Returns
        -------
        Dict[int, str]
            Mapping of cluster_id -> AI-generated cluster name.

        Raises
        ------
        RuntimeError
            If KeyBERT is not available.
        """
        kw = self._get_kw_model()

        docs_to_extract = []
        cluster_ids = []

        for cid, texts in cluster_texts.items():
            if not texts:
                continue
            sample = texts[:CLUSTER_NAME_CAP]
            combined = " ".join(sample)
            docs_to_extract.append(combined)
            cluster_ids.append(cid)

        if not docs_to_extract:
            return {}

        logger.info("AI batch extracting keywords for %d clusters (cooperatively)...", len(docs_to_extract))

        result = {}
        for cid, doc in zip(cluster_ids, docs_to_extract):
            # Check cancellation between clusters
            if cancelled_check and cancelled_check():
                logger.info("AI naming cancelled after processing %d clusters.", len(result))
                return result

            try:
                keywords = kw.extract_keywords(
                    doc,
                    keyphrase_ngram_range=(1, 3),
                    stop_words="english",
                    use_mmr=True,
                    diversity=KEYBERT_DIVERSITY,
                    top_n=KEYBERT_TOP_N,
                )
                
                if keywords and isinstance(keywords, list) and len(keywords) > 0 and isinstance(keywords[0], tuple):
                    name = _format_cluster_name(keywords[0][0])
                else:
                    # Fallback to frequency for this cluster
                    texts = cluster_texts.get(cid, [])
                    name = _frequency_name(texts[:CLUSTER_NAME_CAP])

                result[cid] = name

            except Exception as e:
                logger.warning("Error generating AI name for cluster %s: %s", cid, e)
                texts = cluster_texts.get(cid, [])
                result[cid] = _frequency_name(texts[:CLUSTER_NAME_CAP])

        logger.info("AI cluster naming completed for %d clusters.", len(result))
        return result
