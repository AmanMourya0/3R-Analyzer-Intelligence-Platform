import os
import sys
import pandas as pd
import numpy as np

# Adjust python path to be able to import backend app
sys.path.append(r"c:\Users\aman\OneDrive\Desktop\3R Parent\02_PRODUCTION_3R_BACKEND\backend")

from app.pipelines.incident_pipeline import IncidentPipeline
from app.constants import (
    CLUSTER_ID, THREE_R_CATEGORY, SEMANTIC_MATCH_CLUSTER_ID,
    THREE_R_RUNNER, THREE_R_REPEATER, THREE_R_RARE, NOISE_CLUSTER,
    INCIDENT_NUMBER
)

def run_audit():
    csv_path = r"c:\Users\aman\OneDrive\Desktop\3R Parent\02_PRODUCTION_3R_BACKEND\frontend\public\sample_tickets.csv"
    
    pipeline = IncidentPipeline(csv_path)
    result = pipeline.run()
    
    df = result.dataframe
    summaries = result.cluster_summaries
    three_r_summary = result.three_r_summary
    
    print("=== PIPELINE OUTPUT ===")
    total_processed = len(df)
    runner = df[df[THREE_R_CATEGORY] == THREE_R_RUNNER].shape[0]
    repeater = df[df[THREE_R_CATEGORY] == THREE_R_REPEATER].shape[0]
    rare = df[df[THREE_R_CATEGORY] == THREE_R_RARE].shape[0]
    
    # Original HDBSCAN assignment
    hdbscan_clustered = df[df[CLUSTER_ID] != NOISE_CLUSTER].shape[0]
    hdbscan_noise = df[df[CLUSTER_ID] == NOISE_CLUSTER].shape[0]
    
    # Semantic match
    noise_matched = df[(df[CLUSTER_ID] == NOISE_CLUSTER) & (df[SEMANTIC_MATCH_CLUSTER_ID].notna())].shape[0]
    noise_rare = df[(df[CLUSTER_ID] == NOISE_CLUSTER) & (df[SEMANTIC_MATCH_CLUSTER_ID].isna())].shape[0]
    
    coverage = runner + repeater + rare
    
    print(f"Total processed: {total_processed}")
    print(f"Runner: {runner}")
    print(f"Repeater: {repeater}")
    print(f"Rare: {rare}")
    print(f"Original HDBSCAN clustered: {hdbscan_clustered}")
    print(f"Original HDBSCAN noise: {hdbscan_noise}")
    print(f"Noise semantically matched: {noise_matched}")
    print(f"Noise remaining Rare: {noise_rare}")
    print(f"Runner + Repeater + Rare: {coverage}")
    print(f"Coverage invariant: {coverage == total_processed}")
    
    print("\n--- CLUSTERS ---")
    for summary in summaries:
        reason = getattr(summary, 'three_r_reason', 'UNKNOWN')
        print(f"Cluster {summary.cluster_id}: {getattr(summary, 'three_r_category', 'UNKNOWN')} ({summary.incident_count} incidents)")
        print(f"  Reason: {reason}")

    print("\n=== NOISE MATCHING AUDIT ===")
    noise_df = df[df[CLUSTER_ID] == NOISE_CLUSTER]
    for idx, row in noise_df.iterrows():
        inc_num = row.get(INCIDENT_NUMBER)
        match_id = row.get(SEMANTIC_MATCH_CLUSTER_ID)
        cat = row.get(THREE_R_CATEGORY)
        
        # Calculate max similarity ourselves to report it (or we can just print the data)
        # Actually, the pipeline doesn't store max similarity in the dataframe. We'll recalculate it to display.
        from app.constants import EMBEDDING
        vec1 = np.array(row[EMBEDDING])
        # Centroids
        centroids = []
        for s in summaries:
            cluster_incidents = df[df[CLUSTER_ID] == s.cluster_id]
            embs = np.stack(cluster_incidents[EMBEDDING].values)
            centroid = embs.mean(axis=0)
            centroid = centroid / np.linalg.norm(centroid)
            centroids.append((s.cluster_id, centroid))
            
        sims = []
        for cid, centroid in centroids:
            sim = np.dot(vec1, centroid) / (np.linalg.norm(vec1) * np.linalg.norm(centroid))
            sims.append((cid, sim))
            
        sims.sort(key=lambda x: x[1], reverse=True)
        max_sim = sims[0][1] if sims else 0
        nearest = sims[0][0] if sims else None
        
        if pd.notna(match_id):
            print(f"Incident Number: {inc_num}")
            print(f"Original cluster_id: -1")
            print(f"semantic_match_cluster_id: {int(match_id)}")
            print(f"maximum cosine similarity: {max_sim:.4f}")
            print(f"matched cluster: {int(match_id)}")
            print(f"inherited 3R category: {cat}")
            print("-")
        else:
            print(f"Incident Number: {inc_num}")
            print(f"maximum cosine similarity: {max_sim:.4f}")
            print(f"nearest cluster: {nearest}")
            print(f"similarity result: Not matched (Threshold not met)")
            print("-")

if __name__ == '__main__':
    run_audit()
