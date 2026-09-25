import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

# Adjust python path to be able to import backend app
sys.path.append(r"c:\Users\aman\OneDrive\Desktop\3R Parent\02_PRODUCTION_3R_BACKEND\backend")

from app.pipelines.incident_pipeline import IncidentPipeline
from app.constants import CLUSTER_ID, THREE_R_CATEGORY, THREE_R_RUNNER, THREE_R_REPEATER, NOISE_CLUSTER
from app.clustering.three_r_classifier import ThreeRClassifier

def run_explain_audit():
    csv_path = r"c:\Users\aman\OneDrive\Desktop\3R Parent\02_PRODUCTION_3R_BACKEND\frontend\public\sample_tickets.csv"
    
    pipeline = IncidentPipeline(csv_path)
    result = pipeline.run()
    
    df = result.dataframe
    summaries = result.cluster_summaries
    recurrence_results = pipeline.recurrence_detector.detect(summaries)
    
    # We need to recreate the logic to see the signals
    classifier = ThreeRClassifier()
    # Mocking or extracting values directly
    
    # Recreate the percentiles used in ThreeRClassifier
    scores = [rr.recurrence_score for rr in recurrence_results if rr.recurrence_score > 0]
    counts = [s.incident_count for s in summaries if s.incident_count > 0]
    
    score_75 = np.percentile(scores, 75) if scores else 0
    count_75 = np.percentile(counts, 75) if counts else 0
    
    print(f"Thresholds: score_75={score_75:.2f}, count_75={count_75:.2f}\n")
    
    for summary, rr in zip(summaries, recurrence_results):
        cid = summary.cluster_id
        count = summary.incident_count
        score = rr.recurrence_score
        dist = summary.priority_distribution
        first_date = summary.first_incident_date
        last_date = summary.last_incident_date
        pc = rr.problem_candidate
        
        # Calculate span and velocity
        span_days = 0.0
        velocity = 0.0
        if first_date and last_date:
            try:
                fd = pd.to_datetime(first_date)
                ld = pd.to_datetime(last_date)
                span_days = (ld - fd).days
                if span_days > 0:
                    velocity = count / span_days
                elif span_days == 0 and count > 1:
                    velocity = float(count) # All on same day
            except Exception:
                pass
                
        # Priority impact
        high_prio = sum(v for k, v in dist.items() if str(k).upper() in ["CRITICAL", "HIGH", "P1", "P2", "1", "2"])
        high_prio_pct = (high_prio / count) * 100 if count > 0 else 0
        
        # Determine signals
        signals = []
        is_runner = False
        reason = []
        
        if len(summaries) == 1:
            signals.append("single_cluster_fallback")
            if pc:
                is_runner = True
                reason.append("Single cluster + problem candidate")
        else:
            if score >= score_75 and count >= count_75:
                signals.append(f"top_quartile(score>={score_75:.1f}, count>={count_75:.1f})")
                is_runner = True
                reason.append("Top quartile for score and volume")
                
            if velocity >= 1.0:
                signals.append(f"high_velocity({velocity:.2f}/day)")
                is_runner = True
                reason.append("High velocity (>=1/day)")
                
            if high_prio_pct >= 50.0:
                signals.append(f"high_priority_impact({high_prio_pct:.1f}%)")
                is_runner = True
                reason.append("High priority impact (>=50%)")
                
        cat = THREE_R_RUNNER if is_runner else THREE_R_REPEATER
        if cat == THREE_R_REPEATER:
            reason.append("Did not meet any Runner criteria (top quartile, high velocity, or high priority impact)")
            
        print(f"1. Cluster ID: {cid}")
        print(f"2. Incident count: {count}")
        print(f"3. Recurrence score: {score}")
        print(f"4. Priority distribution: {dist}")
        print(f"5. First incident date: {first_date}")
        print(f"6. Last incident date: {last_date}")
        print(f"7. Active span in days: {span_days}")
        print(f"8. Incident frequency / velocity: {velocity:.2f}")
        print(f"9. problem_candidate: {pc}")
        print(f"10. Signals: {', '.join(signals) if signals else 'None'}")
        print(f"11. Classification: {cat} - Reason: {'; '.join(reason)}")
        print("-" * 50)

if __name__ == '__main__':
    run_explain_audit()
