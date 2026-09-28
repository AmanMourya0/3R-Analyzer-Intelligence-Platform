# Production Deployment Guide (Phase 4 Prep)

This document outlines the infrastructure required for the eventual Phase 4 production rollout.

## Infrastructure Requirements
* **Database**: Managed PostgreSQL instance (e.g., AWS RDS, Azure Postgres).
* **Backend Compute**: 4+ vCPU, 8GB+ RAM required for the AI embedding models. Containerization (Docker) is recommended.
* **Frontend Hosting**: Static web host (e.g., Nginx, Vercel, AWS S3+CloudFront).

## Monitoring
Ensure `/health` and `/ready` endpoints are hooked into the load balancer or Kubernetes readiness probes.
