import os
import sys

# Adjust python path
sys.path.append(r"c:\Users\aman\OneDrive\Desktop\3R Parent\02_PRODUCTION_3R_BACKEND\backend")

from app.database.database import SessionLocal
from app.repositories.job_repository import JobRepository
from app.services.process_service import ProcessService
from app.services.scheduler_service import SchedulerService

from app.pipelines.incident_pipeline import IncidentPipeline

from app.pipelines.incident_pipeline import IncidentPipeline
import os

def run():
    session = SessionLocal()
    repo = JobRepository(session)
    dataset_path = r"c:\Users\aman\OneDrive\Desktop\3R Parent\02_PRODUCTION_3R_BACKEND\backend\dataset\Dummy_Incident_Dataset_V2_5000.xlsx"
    job = repo.create(
        dataset_path=dataset_path,
        source_type="servicenow"
    )
    session.commit()
    session.refresh(job)
    print(f"Created job {job.id}")
    
    pipeline = IncidentPipeline(dataset_path)
    process_service = ProcessService(pipeline)
    print("Processing...")
    process_service.process_job(job.id)
    
    print("Done processing. Verifying invariants...")
    session.refresh(job)
    
    print(f"Status: {job.status}")
    print(f"Total: {job.total_incidents}")
    print(f"Runner: {job.total_runners}")
    print(f"Repeater: {job.total_repeaters}")
    print(f"Rare: {job.total_rares}")
    
    sum_3r = (job.total_runners or 0) + (job.total_repeaters or 0) + (job.total_rares or 0)
    print(f"Invariant sum: {sum_3r} == {job.total_incidents} -> {sum_3r == job.total_incidents}")

if __name__ == "__main__":
    run()
