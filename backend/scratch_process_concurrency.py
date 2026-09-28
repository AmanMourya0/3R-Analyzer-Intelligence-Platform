with open("app/repositories/job_repository.py", "r") as f:
    content = f.read()

old_running = "    def list_jobs_paginated("
new_running = """    def has_running_job(self) -> bool:
        return self.session.query(ProcessingJob).filter(ProcessingJob.status == JOB_STATUS_RUNNING).count() > 0

    def list_jobs_paginated("""

if "def has_running_job" not in content:
    content = content.replace(old_running, new_running)
    with open("app/repositories/job_repository.py", "w") as f:
        f.write(content)

with open("app/services/process_service.py", "r") as f:
    content = f.read()

old_process = """            if job.status == JobStatus.RUNNING.value:

                logger.info(
                    "Processing job %s is already running.",
                    job_id
                )

                return"""
new_process = """            if job.status == JobStatus.RUNNING.value:

                logger.info(
                    "Processing job %s is already running.",
                    job_id
                )

                return

            if repository.has_running_job():
                logger.warning("Another job is already running. Failing job %s.", job_id)
                repository.mark_failed(job, "Another AI clustering job is currently active.")
                session.commit()
                return"""

if "Another AI clustering job is currently active." not in content:
    content = content.replace(old_process, new_process)
    with open("app/services/process_service.py", "w") as f:
        f.write(content)
