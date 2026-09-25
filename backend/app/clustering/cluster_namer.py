import logging
from collections import Counter
from typing import Dict, List

from app.models.cluster_summary import ClusterSummary
from app.config.settings import EMBEDDING_MODEL

logger = logging.getLogger(__name__)

KEYBERT_TOP_N: int = 3
KEYBERT_DIVERSITY: float = 0.5
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

_kw_model = None


def _get_kw_model():
    global _kw_model
    if _kw_model is None:
        try:
            from keybert import KeyBERT
            from sentence_transformers import SentenceTransformer
            logger.info("Loading KeyBERT model: %s", EMBEDDING_MODEL)
            st_model = SentenceTransformer(EMBEDDING_MODEL)
            _kw_model = KeyBERT(model=st_model)
            logger.info("KeyBERT model loaded.")
        except Exception as exc:
            logger.warning("KeyBERT unavailable (%s). Using frequency fallback.", exc)
    return _kw_model


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

def extract_cluster_name(texts: List[str]) -> str:
    if not texts:
        return "Unknown Issues"
    sample = texts[:CLUSTER_NAME_CAP]
    combined = " ".join(sample)
    kw = _get_kw_model()
    if kw is not None:
        try:
            keywords = kw.extract_keywords(
                combined,
                keyphrase_ngram_range=(1, 3),
                stop_words="english",
                use_mmr=True,
                diversity=KEYBERT_DIVERSITY,
                top_n=KEYBERT_TOP_N,
            )
            if keywords:
                return _format_cluster_name(keywords[0][0])
        except Exception as exc:
            logger.warning("KeyBERT extraction failed: %s", exc)
    return _frequency_name(sample)


class ClusterNamer:
    """
    Assigns human-readable cluster names to ClusterSummary objects.
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

        logger.info("Naming %d clusters...", len(cluster_summaries))

        docs_to_extract = []
        cluster_indices = []

        for i, summary in enumerate(cluster_summaries):
            cid = summary.cluster_id
            texts = cluster_texts.get(cid, [])
            if not texts:
                object.__setattr__(summary, "cluster_name", "Unknown Issues")
                continue

            sample = texts[:CLUSTER_NAME_CAP]
            combined = " ".join(sample)
            docs_to_extract.append(combined)
            cluster_indices.append((i, sample))

        kw = _get_kw_model()

        if kw is not None and docs_to_extract:
            try:
                logger.info("Batch extracting keywords for %d clusters...", len(docs_to_extract))
                # extract_keywords on a list returns a list of lists of (keyword, score) tuples
                all_keywords = kw.extract_keywords(
                    docs_to_extract,
                    keyphrase_ngram_range=(1, 3),
                    stop_words="english",
                    use_mmr=True,
                    diversity=KEYBERT_DIVERSITY,
                    top_n=KEYBERT_TOP_N,
                )
                
                # Check if it returned a single list instead of a list of lists (if only 1 doc)
                if len(docs_to_extract) == 1 and all_keywords and isinstance(all_keywords[0], tuple):
                    all_keywords = [all_keywords]

                for idx_pair, keywords in zip(cluster_indices, all_keywords):
                    i, sample = idx_pair
                    summary = cluster_summaries[i]
                    if keywords and isinstance(keywords, list) and len(keywords) > 0 and isinstance(keywords[0], tuple):
                        name = _format_cluster_name(keywords[0][0])
                        object.__setattr__(summary, "cluster_name", name)
                        logger.debug("Cluster %d -> %s", summary.cluster_id, name)
                    else:
                        name = _frequency_name(sample)
                        object.__setattr__(summary, "cluster_name", name)
            except Exception as exc:
                logger.warning("KeyBERT batched extraction failed: %s", exc)
                for i, sample in cluster_indices:
                    name = _frequency_name(sample)
                    object.__setattr__(cluster_summaries[i], "cluster_name", name)
        else:
            for i, sample in cluster_indices:
                name = _frequency_name(sample)
                object.__setattr__(cluster_summaries[i], "cluster_name", name)

        logger.info("Cluster naming completed.")
        return cluster_summaries
