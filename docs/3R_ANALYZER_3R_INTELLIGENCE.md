# 3R Intelligence

The core analytical value of this platform is the categorization of incident clusters into three buckets:

* **Runner**: High-volume, high-velocity incidents that need immediate automation or systemic fixes. These typically have supporting problem signals.
* **Repeater**: Recurring issues that happen regularly but at a lower velocity or without systemic severity, needing gradual root-cause elimination.
* **Rare**: One-off incidents that do not form a pattern.

## Fundamental Invariant
`Total Incidents = Runner Incidents + Repeater Incidents + Rare Incidents`

## Classification Logic
The system implements the following rules (in order):
1. **Priority Repeater**: If a cluster consists entirely of High Priority (P1/P2) incidents, it is immediately a `Repeater`.
2. **High-Velocity Burst (Runner/Repeater)**: If a cluster has ≥3 incidents within a 7-day window:
   - If it has a supporting problem signal (Problem Candidate = True), it is a `Runner`.
   - Otherwise, it is a `Repeater`.
3. **Sustained High Activity**: If a cluster has ≥3 incidents spanning more than 7 days, it is a `Repeater`.
4. **Rare**: Any cluster that does not meet the above criteria is `Rare`.

## What is a Cluster?
Clusters are formed by taking the `Short description` + `Description` of incidents, passing them through `all-MiniLM-L6-v2` to get semantic embeddings, and clustering them using DBSCAN/Cosine Similarity algorithms.
