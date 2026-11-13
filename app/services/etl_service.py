"""Run injected pipeline jobs; no HTTP, SQL or connection creation."""
from dataclasses import dataclass
from threading import Lock
from typing import Callable, Sequence
from etl.step_result import StepResult, StepStatus, PipelineError


@dataclass(frozen=True)
class ExtractJob:
    source: str
    item: str
    run: Callable[[], StepResult]


@dataclass(frozen=True)
class ImportJob:
    source: str
    run: Callable[[], tuple[StepResult, ...]]


@dataclass(frozen=True)
class ActionResult:
    steps: tuple[StepResult, ...]

    @property
    def success_count(self):
        return sum(s.succeeded for s in self.steps)

    @property
    def failure_count(self):
        return len(self.steps) - self.success_count

    @property
    def all_succeeded(self):
        return self.failure_count == 0


class EtlService:
    def __init__(self, extract_jobs: Sequence[ExtractJob], import_jobs: Sequence[ImportJob], lock=None):
        self._extract_jobs = extract_jobs
        self._import_jobs = import_jobs
        self._lock = lock if lock is not None else Lock()

    def _run(self, jobs, *, many):
        if not self._lock.acquire(blocking=False):
            return ActionResult((StepResult('pipeline', 'busy', StepStatus.FAILED,
                                            'Another data action is running. Try again after it finishes.'),))
        try:
            steps = []
            for job in jobs:
                try:
                    result = job.run()
                    steps.extend(result if many else (result,))
                except PipelineError as error:
                    steps.append(StepResult(job.source, getattr(job, 'item', 'import'),
                                            StepStatus.FAILED, str(error)))
            return ActionResult(tuple(steps))
        finally:
            self._lock.release()

    def extract_all(self):
        return self._run(self._extract_jobs, many=False)

    def transform_and_load_all(self):
        return self._run(self._import_jobs, many=True)
