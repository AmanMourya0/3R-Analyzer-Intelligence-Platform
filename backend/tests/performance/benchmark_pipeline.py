import os
import sys

# Adjust python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.database.database import SessionLocal
from app.repositories.job_repository import JobRepository
from app.services.process_service import ProcessService
from app.pipelines.incident_pipeline import IncidentPipeline
from app.services.performance.stage_timer import PipelineProfiler


def reset_database(session):
    # For a clean benchmark, we might want to clean out the tables first, 
    # but the 5000 ticket dataset process does it anyway for the specific job.
    # However, let's keep the DB as is to simulate real world, or clear it out
    # to avoid DB size skewing results. Let's just run the pipeline.
    pass

def run_benchmark():
    session = SessionLocal()
    repo = JobRepository(session)
    dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../dataset/Dummy_Incident_Dataset_V2_5000.xlsx'))
    
    if not os.path.exists(dataset_path):
        print(f"Dataset not found at {dataset_path}")
        return

    job = repo.create(
        dataset_path=dataset_path,
        source_type="servicenow"
    )
    session.commit()
    session.refresh(job)
    print(f"Created job {job.id}")
    
    profiler = PipelineProfiler.get_instance()
    profiler.start_pipeline()
    
    pipeline = IncidentPipeline(dataset_path)
    process_service = ProcessService(pipeline)
    print("Starting processing...")
    
    process_service.process_job(job.id)
    
    profiler.end_pipeline()
    
    session.refresh(job)
    profiler.print_report(total_incidents=job.total_incidents or 0)
    
    sum_3r = (job.total_runners or 0) + (job.total_repeaters or 0) + (job.total_rares or 0)
    print(f"Total: {job.total_incidents}")
    print(f"Runner: {job.total_runners}")
    print(f"Repeater: {job.total_repeaters}")
    print(f"Rare: {job.total_rares}")
    print(f"Invariant: {sum_3r} == {job.total_incidents} -> {sum_3r == job.total_incidents}")

if __name__ == "__main__":
    run_benchmark()
