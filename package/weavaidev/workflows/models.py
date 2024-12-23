from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel


class WorkflowTask(BaseModel):
    name: str
    is_active: bool
    downstream_tasks: List[str]


class Workflow(BaseModel):
    name: str
    tasks: List[WorkflowTask]
    params: List[str]


class GetAllWorkflowsResponse(BaseModel):
    workflows: List[Workflow]


class SkipStepsInWorkflowRequest(BaseModel):
    tasks: List[str]


class WorkflowRequest(BaseModel):
    doc_id: str
    data: Optional[Any] = {}


class RunWorkflowResponse(BaseModel):
    run_id: str
    workflow_id: str
    document_id: str
    document_name: str
    in_folders: Optional[List[str]] = []
    state: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    created_at: str


class TaskStatusSummary(BaseModel):
    success: int
    running: int
    queued: int
    failed: int
    skipped: int


class Task(BaseModel):
    name: str
    task_status_summary: TaskStatusSummary
    status: str
    failed_task_ids: Optional[List[int]] = []
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class WorkflowStatusResponse(BaseModel):
    status: str
    document_id: str
    tasks: Optional[List[Task]] = []
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class DocumentRun(BaseModel):
    run_id: str
    workflow_id: str
    document_id: str
    document_name: str
    in_folders: List[str]
    state: str
    start_date: str
    end_date: str
    created_at: Optional[str] = ""


class DocumentWorkflowRunsResponse(BaseModel):
    docs: List[DocumentRun]
    total: int
