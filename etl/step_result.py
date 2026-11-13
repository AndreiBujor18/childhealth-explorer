"""Plain operation outcomes shared by CLI, services and HTML presentation."""
from dataclasses import dataclass
from enum import Enum


class StepStatus(str, Enum):
    OK = 'success'
    FAILED = 'failed'


@dataclass(frozen=True)
class StepResult:
    source: str
    item: str
    status: StepStatus
    message: str
    raw_rows: int = 0
    clean_rows: int = 0
    rejected_rows: int = 0
    rows_loaded: int = 0
    new_rows: int = 0
    updated_rows: int = 0

    @property
    def succeeded(self):
        return self.status == StepStatus.OK


class PipelineError(Exception):
    """Expected pipeline failures; programming exceptions are never swallowed."""
