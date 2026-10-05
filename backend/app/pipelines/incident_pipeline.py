"""
Incident Processing Pipeline

This module orchestrates the complete preprocessing pipeline
for historical incidents.

Pipeline Flow:
    Load Dataset
        ↓
    Preprocess Dataset
        ↓
    Generate Embeddings
        ↓
    Generate Semantic Clusters
        ↓
    Generate Cluster Summaries
        ↓
    Generate Recurrence Results

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from typing import Callable, Optional

import pandas as pd

from app.services.incident_loader import IncidentLoader
from app.services.preprocessing import Preprocessor
from app.clustering.embedding import SemanticEmbeddingGenerator
from app.clustering.cluster import SemanticClusterer
from app.constants import (
    EMBEDDING,
    COMBINED_TEXT,
    CLUSTER_ID
)
from app.clustering.cluster_analyzer import ClusterAnalyzer
from app.clustering.cluster_namer import ClusterNamer
from app.clustering.recurrence import RecurrenceDetector
from app.clustering.three_r_classifier import ThreeRClassifier
from app.models.pipeline_result import PipelineResult
from app.services.performance.stage_timer import stage_timer

from app.utils.logger import logger
from app.core.exceptions import JobCancelledException


class IncidentPipeline:
    """
    End-to-end pipeline for incident processing.
    """

    def __init__(
        self,
        dataset_path: Optional[str] = None
    ) -> None:
        """
        Initialize all required pipeline components.
        """

        self.dataset_path = dataset_path

        self.preprocessor = Preprocessor()

        self.embedding_generator = SemanticEmbeddingGenerator()

        self.cluster_generator = SemanticClusterer()

        self.cluster_analyzer = ClusterAnalyzer()

        self.cluster_namer = ClusterNamer()

        self.recurrence_detector = RecurrenceDetector()

        self.three_r_classifier = ThreeRClassifier()

    def run(
        self,
        dataframe: Optional[pd.DataFrame] = None,
        progress_callback: Optional[
            Callable[[str, str, int], None]
        ] = None,
        check_cancellation: Optional[Callable[[], None]] = None
    ) -> PipelineResult:
        """
        Execute the complete pipeline.

        Parameters
        ----------
        dataframe : Optional[pd.DataFrame]
            Incident dataframe supplied by the service layer.

        progress_callback : Optional[Callable]
            Callback used to report pipeline progress.

            Parameters:
                stage : str
                message : str
                percent : int

        Returns
        -------
        PipelineResult
            Complete pipeline result containing processed data
            and analysis.
        """

        def report_progress(
            stage: str,
            message: str,
            percent: int
        ) -> None:
            """
            Safely report pipeline progress.

            Progress reporting must never break the actual
            incident-processing pipeline.
            """

            if progress_callback is None:
                return

            try:

                progress_callback(
                    stage,
                    message,
                    percent
                )

            except Exception:

                logger.exception(
                    "Unable to report pipeline progress."
                )

        try:

            logger.info("=" * 60)
            logger.info(
                "Starting Incident Processing Pipeline"
            )
            logger.info("=" * 60)

            # -------------------------------------------------
            # Dataset Loading
            # -------------------------------------------------

            if dataframe is None:

                if not self.dataset_path:

                    raise ValueError(
                        "A dataframe or dataset_path is required."
                    )

                report_progress(
                    "LOADING_DATA",
                    "Loading incident dataset...",
                    5
                )

                with stage_timer('LOADING_DATA'):
                    dataframe = IncidentLoader(
                        self.dataset_path
                    ).load()

            # -------------------------------------------------
            # Step 1 : Clean Dataset
            # -------------------------------------------------

            if check_cancellation:
                check_cancellation()

            report_progress(
                "PREPROCESSING",
                "Preparing and cleaning incident data...",
                15
            )

            with stage_timer('PREPROCESSING', len(dataframe)):
                df = self.preprocessor.clean(
                    dataframe
                )

            logger.info(
                "Dataset preprocessing completed."
            )

            # -------------------------------------------------
            # Step 2 : Generate Embeddings
            # -------------------------------------------------

            if check_cancellation:
                check_cancellation()

            report_progress(
                "GENERATING_EMBEDDINGS",
                "Generating semantic understanding of incidents...",
                30
            )

            with stage_timer('GENERATING_EMBEDDINGS', len(df)):
                embeddings = (
                    self.embedding_generator
                    .generate_embeddings(
                        df[COMBINED_TEXT].tolist(),
                        check_cancellation=check_cancellation
                    )
                )

            logger.info(
                "Incident embeddings generated."
            )

            # -------------------------------------------------
            # Step 3 : Store embeddings
            # -------------------------------------------------

            report_progress(
                "STORING_EMBEDDINGS",
                "Preparing semantic data for analysis...",
                40
            )

            with stage_timer('STORING_EMBEDDINGS', len(df)):
                df[EMBEDDING] = embeddings.tolist()

            # -------------------------------------------------
            # Step 4 : Generate Semantic Clusters
            # -------------------------------------------------

            if check_cancellation:
                check_cancellation()

            report_progress(
                "CLUSTERING",
                "Detecting semantically similar incident groups...",
                55
            )

            with stage_timer('CLUSTERING', len(df)):
                labels = self.cluster_generator.generate(
                    embeddings
                )

            df[CLUSTER_ID] = labels

            logger.info(
                "Semantic clustering completed."
            )

            # -------------------------------------------------
            # Step 5 : Generate Cluster Summaries
            # -------------------------------------------------

            if check_cancellation:
                check_cancellation()

            report_progress(
                "CLUSTER_ANALYSIS",
                "Analyzing incident clusters and patterns...",
                70
            )

            with stage_timer('CLUSTER_ANALYSIS', len(df)):
                cluster_summaries = (
                    self.cluster_analyzer.analyze(
                        df
                    )
                )

            logger.info(
                "Cluster analysis completed."
            )

            # -------------------------------------------------
            # Step 5.5 : Generate Cluster Names (Standard)
            # -------------------------------------------------
            # Uses fast, deterministic token-frequency naming.
            # KeyBERT is NOT invoked here — it is an optional
            # post-pipeline enrichment operation.
            # -------------------------------------------------

            report_progress(
                "NAMING_CLUSTERS",
                "Generating cluster names...",
                78
            )

            if check_cancellation:
                check_cancellation()

            if hasattr(self, "cluster_namer") and self.cluster_namer is not None:
                with stage_timer('NAMING_CLUSTERS', len(cluster_summaries)):
                    cluster_summaries = self.cluster_namer.name_clusters(
                        cluster_summaries=cluster_summaries,
                        combined_texts=df[COMBINED_TEXT].tolist(),
                        cluster_labels=df[CLUSTER_ID].tolist(),
                    )

            logger.info(
                "Cluster naming completed."
            )

            # -------------------------------------------------
            # Step 6 : Generate Recurrence Results
            # -------------------------------------------------

            if check_cancellation:
                check_cancellation()

            report_progress(
                "RECURRENCE_ANALYSIS",
                "Detecting recurring incidents and problem candidates...",
                85
            )

            with stage_timer('RECURRENCE_ANALYSIS', len(cluster_summaries)):
                recurrence_results = (
                    self.recurrence_detector.detect(
                        cluster_summaries
                    )
                )

            logger.info(
                "Recurrence analysis completed."
            )

            # -------------------------------------------------
            # Step 7 : Generate 3R Classification
            # -------------------------------------------------

            if check_cancellation:
                check_cancellation()

            report_progress(
                "THREE_R_CLASSIFICATION",
                "Classifying incidents into Runner, Repeater, and Rare...",
                90
            )

            with stage_timer('THREE_R_CLASSIFICATION', len(df)):
                df, cluster_summaries, three_r_summary = (
                    self.three_r_classifier.classify(
                        dataframe=df,
                        embeddings=embeddings,
                        cluster_summaries=cluster_summaries,
                        recurrence_results=recurrence_results
                    )
                )

            logger.info(
                "3R classification completed."
            )

            # -------------------------------------------------
            # Pipeline Complete
            # -------------------------------------------------

            if check_cancellation:
                check_cancellation()

            logger.info(
                "Pipeline completed successfully."
            )

            return PipelineResult(
                dataframe=df,
                cluster_summaries=cluster_summaries,
                recurrence_results=recurrence_results,
                three_r_summary=three_r_summary
            )

        except JobCancelledException:

            logger.info(
                "Incident pipeline execution cancelled."
            )

            raise

        except Exception:

            logger.exception(
                "Incident pipeline execution failed."
            )

            raise