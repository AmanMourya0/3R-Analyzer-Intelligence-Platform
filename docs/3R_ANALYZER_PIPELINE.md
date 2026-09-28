# AI Pipeline

The 3R Analyzer pipeline consists of 11 strictly ordered stages. 

## Stages
1. **LOADING_DATA**: Reads the uploaded CSV/XLSX into a pandas DataFrame.
2. **APPLYING_SCOPE**: Filters out incidents already processed (if delta processing is implemented).
3. **PREPROCESSING**: Cleans text, handles nulls, formats dates, and prepares the `combined_text` column.
4. **GENERATING_EMBEDDINGS**: Uses `all-MiniLM-L6-v2` to convert text into high-dimensional vectors. (Batch size optimized).
5. **STORING_EMBEDDINGS**: Temporarily holds vectors in memory for clustering.
6. **CLUSTERING**: Groups similar embeddings using optimized DBSCAN with cosine similarity.
7. **CLUSTER_ANALYSIS**: Aggregates metadata (top CI, top Assignment Group) per cluster.
8. **NAMING_CLUSTERS**: Uses KeyBERT to extract a readable 3-4 word summary phrase for the cluster.
9. **RECURRENCE_ANALYSIS**: Analyzes the time-series distribution of the cluster to find bursts or sustained activity.
10. **THREE_R_CLASSIFICATION**: Applies the Runner/Repeater/Rare logic to each cluster.
11. **PERSISTING_RESULTS**: Safely writes all records to PostgreSQL using transaction chunks.

## Performance Characteristics
Baseline for a 5,000 incident dataset: **~65 seconds**.
The pipeline is instrumented with `stage_timer` for structured observability.
