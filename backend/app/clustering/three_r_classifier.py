"""
ThreeRClassifier

Evaluates clusters and incidents to assign RUNNER, REPEATER, or RARE classifications.

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""
from typing import List, Tuple
import pandas as pd
import numpy as np

from app.constants import (
    THREE_R_CATEGORY,
    SEMANTIC_MATCH_CLUSTER_ID,
    THREE_R_RUNNER,
    THREE_R_REPEATER,
    THREE_R_RARE,
    CLUSTER_ID,
    NOISE_CLUSTER,
    CREATED_DATE
)
from app.config.settings import SIMILARITY_THRESHOLD
from app.models.cluster_summary import ClusterSummary
from app.models.recurrence_result import RecurrenceResult
from app.models.three_r_summary import ThreeRSummary
from app.utils.logger import logger


def cosine_similarity_vectors(vec1: np.ndarray, vectors: np.ndarray) -> np.ndarray:
    """Calculate cosine similarity between one vector and a matrix of vectors."""
    if len(vectors) == 0:
        return np.array([])
        
    norm1 = np.linalg.norm(vec1)
    norms = np.linalg.norm(vectors, axis=1)
    
    if norm1 == 0:
        return np.zeros(len(vectors))
        
    # Avoid division by zero
    norms = np.where(norms == 0, 1.0, norms)
    
    dot_products = np.dot(vectors, vec1)
    similarities = dot_products / (norm1 * norms)
    return np.clip(similarities, -1.0, 1.0)


class ThreeRClassifier:
    """
    Classifies incidents and clusters into RUNNER, REPEATER, and RARE categories.
    """
    
    def classify(
        self,
        dataframe: pd.DataFrame,
        embeddings: np.ndarray,
        cluster_summaries: List[ClusterSummary],
        recurrence_results: List[RecurrenceResult]
    ) -> Tuple[pd.DataFrame, List[ClusterSummary], ThreeRSummary]:
        """
        Execute 3R classification on the processed dataset.
        """
        logger.info("Starting 3R Classification...")
        
        df = dataframe.copy()
        df[THREE_R_CATEGORY] = None
        df[SEMANTIC_MATCH_CLUSTER_ID] = None
        
        # 1. Calculate cluster representative embeddings (centroids)
        centroids = {}
        for summary in cluster_summaries:
            cluster_indices = df[df[CLUSTER_ID] == summary.cluster_id].index
            if len(cluster_indices) > 0:
                cluster_embeddings = embeddings[cluster_indices]
                centroid = np.mean(cluster_embeddings, axis=0)
                centroids[summary.cluster_id] = centroid
        
        runner_cluster_ids = set()
        repeater_cluster_ids = set()
        
        # Calculate data-driven relative thresholds if we have enough clusters
        score_75 = 0
        count_75 = 0
        if len(recurrence_results) >= 3:
            score_75 = np.percentile([r.recurrence_score for r in recurrence_results], 75)
            count_75 = np.percentile([r.cluster_summary.incident_count for r in recurrence_results], 75)
            
        # 2. Classify valid clusters as Runner or Repeater
        for result in recurrence_results:
            summary = result.cluster_summary
            cid = summary.cluster_id
            
            # Temporal / Velocity calculation
            try:
                first_dt = pd.to_datetime(summary.first_incident_date)
                last_dt = pd.to_datetime(summary.last_incident_date)
                active_days = (last_dt - first_dt).days
            except Exception:
                active_days = 0
                
            velocity = summary.incident_count / active_days if active_days > 0 else float(summary.incident_count)
            
            # Extract Signals
            is_top_quartile = False
            if len(recurrence_results) >= 3:
                is_top_quartile = (result.recurrence_score >= score_75 and summary.incident_count >= count_75 and result.recurrence_score > 0)
                
            high_pri_count = sum(c for p, c in summary.priority_distribution.items() if str(p).upper() in ["P1", "P2", "HIGH", "CRITICAL"])
            high_priority_pct = (high_pri_count / summary.incident_count) * 100.0 if summary.incident_count > 0 else 0.0
            
            has_priority_support = high_priority_pct >= 33.0
            has_strong_priority_support = high_priority_pct >= 50.0
            is_problem = result.problem_candidate
            
            is_runner = False
            reason = []
            
            # Condition 1: Sustained High Activity
            if is_top_quartile and active_days >= 14:
                is_runner = True
                reason.append("Sustained high-volume recurring activity")
                
            # Condition 2: Severe Burst
            elif is_top_quartile and velocity >= 2.0:
                is_runner = True
                reason.append("Severe burst activity with top quartile volume")
                
            # Condition 3: High-Impact Burst
            elif summary.incident_count >= 5 and velocity >= 1.0 and (has_priority_support or is_problem):
                is_runner = True
                reason.append("High-velocity burst with supporting impact/problem signal")
                
            # Condition 4: Sustained Problem
            elif summary.incident_count >= 5 and active_days >= 14 and has_strong_priority_support and is_problem:
                is_runner = True
                reason.append("Sustained baseline activity with strong priority and problem signals")
                
            if is_runner:
                runner_cluster_ids.add(cid)
                summary.three_r_category = THREE_R_RUNNER
                # Store the reason temporarily for logs and testing if needed, though not persisted.
                summary.three_r_reason = reason[0]
                logger.info(f"Cluster {cid} classified as RUNNER. Reason: {reason[0]}")
            else:
                repeater_cluster_ids.add(cid)
                summary.three_r_category = THREE_R_REPEATER
                summary.three_r_reason = "Normal recurring activity (did not meet elevated Runner criteria)"
                logger.info(f"Cluster {cid} classified as REPEATER. Reason: Normal recurring activity")

        # Assign category to clustered incidents
        df.loc[df[CLUSTER_ID].isin(runner_cluster_ids), THREE_R_CATEGORY] = THREE_R_RUNNER
        df.loc[df[CLUSTER_ID].isin(repeater_cluster_ids), THREE_R_CATEGORY] = THREE_R_REPEATER
        
        # 3. Second-stage semantic matching for noise incidents
        noise_mask = df[CLUSTER_ID] == NOISE_CLUSTER
        noise_indices = df[noise_mask].index
        
        centroid_matrix = []
        centroid_cids = []
        for cid, centroid in centroids.items():
            centroid_matrix.append(centroid)
            centroid_cids.append(cid)
            
        if len(centroid_matrix) > 0:
            centroid_matrix = np.array(centroid_matrix)
        
        for idx in noise_indices:
            emb = embeddings[idx]
            matched_cid = None
            max_sim = -1.0
            
            if len(centroid_matrix) > 0:
                similarities = cosine_similarity_vectors(emb, centroid_matrix)
                best_idx = np.argmax(similarities)
                max_sim = similarities[best_idx]
                if max_sim >= SIMILARITY_THRESHOLD:
                    matched_cid = centroid_cids[best_idx]
            
            if matched_cid is not None:
                # High semantic similarity -> inherit the matched cluster's category
                df.at[idx, SEMANTIC_MATCH_CLUSTER_ID] = matched_cid
                if matched_cid in runner_cluster_ids:
                    df.at[idx, THREE_R_CATEGORY] = THREE_R_RUNNER
                else:
                    df.at[idx, THREE_R_CATEGORY] = THREE_R_REPEATER
            else:
                # Weak/no match -> RARE
                df.at[idx, THREE_R_CATEGORY] = THREE_R_RARE
                
        # 4. Validation & Invariant Enforcement
        # Ensure all incidents have exactly one 3R category
        null_count = df[THREE_R_CATEGORY].isnull().sum()
        if null_count > 0:
            logger.warning(f"Found {null_count} incidents without a 3R category. Assigning to RARE.")
            df[THREE_R_CATEGORY] = df[THREE_R_CATEGORY].fillna(THREE_R_RARE)
            
        total = len(df)
        runner_count = (df[THREE_R_CATEGORY] == THREE_R_RUNNER).sum()
        repeater_count = (df[THREE_R_CATEGORY] == THREE_R_REPEATER).sum()
        rare_count = (df[THREE_R_CATEGORY] == THREE_R_RARE).sum()
        
        if runner_count + repeater_count + rare_count != total:
            msg = f"3R Classification coverage invariant failed! Total: {total}, RUNNER: {runner_count}, REPEATER: {repeater_count}, RARE: {rare_count}"
            logger.error(msg)
            raise ValueError(msg)
            
        logger.info(
            f"3R classification completed: Total={total} "
            f"Runner={runner_count} Repeater={repeater_count} Rare={rare_count} "
            f"Coverage={total}/{total}"
        )
        
        summary_obj = ThreeRSummary(
            total=total,
            runner_count=runner_count,
            repeater_count=repeater_count,
            rare_count=rare_count
        )
        
        return df, cluster_summaries, summary_obj
