# Product Overview

## What is 3R Analyzer Intelligence?
3R Analyzer Intelligence is an analytical platform designed to ingest IT incident data (e.g., from ServiceNow), intelligently group similar incidents using semantic AI clustering, and classify those clusters into actionable categories: **Runner**, **Repeater**, or **Rare**. 

## Business Problem
IT Service Desks are often overwhelmed by recurring incidents. Traditional text matching is insufficient to detect conceptually similar problems. By leveraging Large Language Models (LLMs) and embeddings, 3R Analyzer identifies the true underlying recurring problems, allowing IT leadership to prioritize permanent fixes.

## Target Users
* **Service Desk Managers**: To view the dashboard and monitor volume.
* **Problem Managers**: To investigate specific clusters and formulate problem tickets.
* **IT Executives**: To review PDF summary reports.

## Main Workflow
1. **Ingestion**: User uploads a CSV/XLSX export from ServiceNow.
2. **Background Processing**: The system queues a Job, generating embeddings, clustering, and performing 3R classification.
3. **Analysis**: Once complete, users explore the results in the Dashboard and Incident Investigation Workspace.
4. **Action**: Users export results to create ServiceNow Problem records.
