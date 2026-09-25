import re

# 1. Patch incident_pipeline.py
with open("app/pipelines/incident_pipeline.py", "r", encoding="utf-8") as f:
    code = f.read()

if "stage_timer" not in code:
    code = code.replace(
        "from app.models.pipeline_result import PipelineResult",
        "from app.models.pipeline_result import PipelineResult\nfrom app.services.performance.stage_timer import stage_timer"
    )

    code = code.replace(
        "dataframe = IncidentLoader(\n                    self.dataset_path\n                ).load()",
        "with stage_timer('LOADING_DATA'):\n                    dataframe = IncidentLoader(\n                        self.dataset_path\n                    ).load()"
    )

    code = code.replace(
        "df = self.preprocessor.clean(\n                dataframe\n            )",
        "with stage_timer('PREPROCESSING', len(dataframe)):\n                df = self.preprocessor.clean(\n                    dataframe\n                )"
    )

    code = code.replace(
        "embeddings = (\n                self.embedding_generator\n                .generate_embeddings(\n                    df[COMBINED_TEXT].tolist()\n                )\n            )",
        "with stage_timer('GENERATING_EMBEDDINGS', len(df)):\n                embeddings = (\n                    self.embedding_generator\n                    .generate_embeddings(\n                        df[COMBINED_TEXT].tolist()\n                    )\n                )"
    )

    code = code.replace(
        "df[EMBEDDING] = embeddings.tolist()",
        "with stage_timer('STORING_EMBEDDINGS', len(df)):\n                df[EMBEDDING] = embeddings.tolist()"
    )

    code = code.replace(
        "labels = self.cluster_generator.generate(\n                embeddings\n            )",
        "with stage_timer('CLUSTERING', len(df)):\n                labels = self.cluster_generator.generate(\n                    embeddings\n                )"
    )

    code = code.replace(
        "cluster_summaries = (\n                self.cluster_analyzer.analyze(\n                    df\n                )\n            )",
        "with stage_timer('CLUSTER_ANALYSIS', len(df)):\n                cluster_summaries = (\n                    self.cluster_analyzer.analyze(\n                        df\n                    )\n                )"
    )

    code = code.replace(
        "cluster_summaries = self.cluster_namer.name_clusters(\n                    cluster_summaries=cluster_summaries,\n                    combined_texts=df[COMBINED_TEXT].tolist(),\n                    cluster_labels=df[CLUSTER_ID].tolist(),\n                )",
        "with stage_timer('NAMING_CLUSTERS', len(cluster_summaries)):\n                    cluster_summaries = self.cluster_namer.name_clusters(\n                        cluster_summaries=cluster_summaries,\n                        combined_texts=df[COMBINED_TEXT].tolist(),\n                        cluster_labels=df[CLUSTER_ID].tolist(),\n                    )"
    )

    code = code.replace(
        "recurrence_results = (\n                self.recurrence_detector.detect(\n                    cluster_summaries\n                )\n            )",
        "with stage_timer('RECURRENCE_ANALYSIS', len(cluster_summaries)):\n                recurrence_results = (\n                    self.recurrence_detector.detect(\n                        cluster_summaries\n                    )\n                )"
    )

    code = code.replace(
        "df, cluster_summaries, three_r_summary = (\n                self.three_r_classifier.classify(\n                    dataframe=df,\n                    embeddings=embeddings,\n                    cluster_summaries=cluster_summaries,\n                    recurrence_results=recurrence_results\n                )\n            )",
        "with stage_timer('THREE_R_CLASSIFICATION', len(df)):\n                df, cluster_summaries, three_r_summary = (\n                    self.three_r_classifier.classify(\n                        dataframe=df,\n                        embeddings=embeddings,\n                        cluster_summaries=cluster_summaries,\n                        recurrence_results=recurrence_results\n                    )\n                )"
    )

    with open("app/pipelines/incident_pipeline.py", "w", encoding="utf-8") as f:
        f.write(code)


# 2. Patch process_service.py
with open("app/services/process_service.py", "r", encoding="utf-8") as f:
    code = f.read()

if "stage_timer" not in code:
    code = code.replace(
        "from app.models.pipeline_result import (\n    PipelineResult\n)",
        "from app.models.pipeline_result import (\n    PipelineResult\n)\nfrom app.services.performance.stage_timer import stage_timer"
    )

    code = code.replace(
        "scoped_df = self._apply_processing_scope(source_df, job)",
        "with stage_timer('APPLYING_SCOPE', len(source_df)):\n            scoped_df = self._apply_processing_scope(source_df, job)"
    )

    code = code.replace(
        "result = self.pipeline.run(\n            dataframe=scoped_df,\n            progress_callback=callback\n        )",
        "result = self.pipeline.run(\n            dataframe=scoped_df,\n            progress_callback=callback\n        )"
    )

    # Wrap the persistence
    code = code.replace(
        "IncidentRepository(session).save_batch(\n            result.dataframe\n        )\n\n        ClusterRepository(session).save_batch(\n            result.cluster_summaries\n        )\n\n        RecurrenceRepository(session).save_batch(\n            result.recurrence_results\n        )",
        "with stage_timer('PERSISTING_RESULTS'):\n            IncidentRepository(session).save_batch(\n                result.dataframe\n            )\n\n            ClusterRepository(session).save_batch(\n                result.cluster_summaries\n            )\n\n            RecurrenceRepository(session).save_batch(\n                result.recurrence_results\n            )"
    )

    with open("app/services/process_service.py", "w", encoding="utf-8") as f:
        f.write(code)

print("Patch complete.")
