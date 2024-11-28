from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class CreateFolderRequest(BaseModel):
    name: str
    category: Optional[str] = ""
    description: Optional[str] = ""


class Workflow(BaseModel):
    workflow_id: str
    form_id: Optional[str] = ""
    workflow_params: Optional[Dict[str, Any]] = {}


class CreateFolderResponse(BaseModel):
    id: str
    documents: Optional[Any] = None
    document_ids: Optional[List[str]] = []
    shared_with_users: Optional[Dict[str, Any]] = {}
    shared_with_groups: Optional[Dict[str, Any]] = {}
    name: str
    category: Optional[str] = ""
    description: Optional[str] = ""
    created_at: Optional[str] = ""
    modified_at: Optional[str] = ""
    user_id: Optional[str] = ""
    tenant_id: Optional[str] = ""
    workflow: Workflow


class WritableFolderData(BaseModel):
    name: str
    id: str


class WritableFoldersResponse(BaseModel):
    folders: Optional[List[WritableFolderData]] = []
