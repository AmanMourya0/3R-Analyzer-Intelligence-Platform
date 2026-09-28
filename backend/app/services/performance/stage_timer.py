import time
from contextlib import contextmanager
from typing import Dict, List, Optional
from pydantic import BaseModel

class StageTiming(BaseModel):
    stage_name: str
    start_time: float
    end_time: float
    duration_seconds: float
    records_processed: Optional[int] = None
    percentage_of_total: float = 0.0

class PipelineProfiler:
    _instance = None
    
    def __init__(self):
        self.timings: List[StageTiming] = []
        self.total_start_time: float = 0.0
        self.total_end_time: float = 0.0
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = PipelineProfiler()
        return cls._instance
    
    def start_pipeline(self):
        self.timings = []
        self.total_start_time = time.time()
        
    def end_pipeline(self):
        self.total_end_time = time.time()
        total_duration = self.total_end_time - self.total_start_time
        if total_duration > 0:
            for timing in self.timings:
                timing.percentage_of_total = (timing.duration_seconds / total_duration) * 100
                
    def add_timing(self, timing: StageTiming):
        self.timings.append(timing)

    def print_report(self, total_incidents: int = 0):
        total_duration = self.total_end_time - self.total_start_time
        print("\n" + "="*50)
        print("BASELINE PERFORMANCE REPORT")
        print("="*50)
        print(f"Dataset: {total_incidents} incidents")
        print(f"Total: ~{total_duration:.2f} sec\n")
        
        for t in self.timings:
            print(f"{t.stage_name:<25}: {t.duration_seconds:>7.2f} sec ({t.percentage_of_total:>5.1f}%) [Records: {t.records_processed if t.records_processed is not None else 'N/A'}]")
        print("="*50 + "\n")


@contextmanager
def stage_timer(stage_name: str, records_processed: Optional[int] = None):
    start_time = time.time()
    try:
        yield
    finally:
        end_time = time.time()
        duration_seconds = end_time - start_time
        timing = StageTiming(
            stage_name=stage_name,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration_seconds,
            records_processed=records_processed
        )
        profiler = PipelineProfiler.get_instance()
        profiler.add_timing(timing)
        from app.utils.logger import logger
        logger.info(f"job_id={getattr(profiler, 'current_job_id', 'unknown')} stage={stage_name} status=COMPLETED duration_ms={int(duration_seconds * 1000)} incident_count={records_processed or 0}")
