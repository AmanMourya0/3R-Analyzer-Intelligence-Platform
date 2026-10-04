# 3R Analyzer Intelligence - 27K Performance Profile

## 1. Environment & Setup

* **Dataset**: ServiceNow Incidents (~27,000 records)
* **Embedding Model**: `all-MiniLM-L6-v2` (Running on CPU)
* **Clustering Algorithm**: HDBSCAN
* **Cluster Naming**: KeyBERT (Enabled)
* **Database**: PostgreSQL
* **Environment**: Local Development Environment (CPU)

## 2. Total End-to-End Processing Time

* **Total Time**: ~1516 seconds (25 minutes, 16 seconds)

## 3. Pipeline Stage Timings

| Stage | Duration (ms) | Duration (seconds) | Share of Total (%) | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **LOADING_DATA** | 7,915 | 7.9 | 0.5% | Pandas CSV reading |
| **PREPROCESSING** | 4,660 | 4.6 | 0.3% | Data cleaning & NaN handling |
| **GENERATING_EMBEDDINGS** | 1,148,607 | 1,148.6 (19.1m) | 75.7% | **Primary Bottleneck**. CPU-bound processing of 27k incidents using MiniLM. |
| **STORING_EMBEDDINGS** | 1,392 | 1.4 | 0.1% | DataFrame manipulation |
| **CLUSTERING** | 332,576 | 332.5 (5.5m) | 21.9% | **Secondary Bottleneck**. HDBSCAN O(N log N) overhead |
| **CLUSTER_ANALYSIS** | 2,680 | 2.6 | 0.2% | |
| **NAMING_CLUSTERS** | 594,020 | 594.0 (9.9m) | 28.3% | **Tertiary Bottleneck**. KeyBERT N-gram/MMR extraction over 1,647 clusters |
| **RECURRENCE_ANALYSIS** | 1 | 0.0 | <0.1% | |
| **THREE_R_CLASSIFICATION** | 20,747 | 20.7 | 1.0% | Efficient processing over 26k incidents |
| **PERSISTING_RESULTS** | 18,500 | 18.5 | 0.9% | Bulk PostgreSQL inserts |

**Total End-to-End Pipeline Duration (Simulated w/ KeyBERT)**: ~2,110 seconds (35 minutes, 10 seconds)

## 4. Conclusion and Recommendations

### KeyBERT Viability

Initially, the pipeline ran in ~25 minutes because KeyBERT gracefully fell back to frequency-based naming (taking just 0.5s) due to a missing package. However, when benchmarked properly, executing KeyBERT's N-gram extraction and MMR (Maximal Marginal Relevance) on 1,647 cluster texts took **9.9 minutes (594 seconds)** on the CPU. 
Because KeyBERT adds nearly 10 minutes of processing time and the combined embeddings + clustering take 25 minutes, **synchronous execution for large datasets is completely unviable**. The entire pipeline heavily depends on background execution via APScheduler, which is currently configured and working. No changes are needed to the architecture, as the background processing model perfectly supports this 35-minute workflow without blocking the UI.

### Pre-Processing Validation Gap

**Documented Finding:** Currently, the pipeline successfully uploads datasets and performs basic pre-processing without strictly enforcing length constraints aligned to the database schema (e.g. `Incident.priority` max length, `description` lengths, etc.). If a field severely exceeds its database column length, the pipeline will successfully complete the entire AI processing chain (Embeddings, Clustering, etc.) taking several minutes/hours, only to fail at the very last stage (`PERSISTING_RESULTS`) when SQLAlchemy attempts to commit the data. This represents a significant risk of wasted compute resources.

**Recommendation:** Add early schema validation (e.g. using Pydantic or Pandas bounds checking) before the pipeline transitions to `GENERATING_EMBEDDINGS` to fail fast on incompatible datasets.

### UI Progress Synchronization Issue

**Documented Finding:** The frontend previously marked stages as `COMPLETED` prematurely. This was caused by the frontend polling `/api/status`, which returns the status of the `latest_job` in the database. When uploading a dataset, the old `/upload` endpoint did not start the job but simply uploaded the file. The UI would poll immediately, get the previous job's `COMPLETED` status (with `percent: 100`), and assume the current processing was instantly completed.

**Resolution:** Fixed the endpoint routing in `frontend/src/api.js` to point to `/api/upload` (which correctly maps to the `frontend_api.py` endpoint) rather than the basic `upload.py` endpoint, ensuring the job is actually started and polled correctly.
