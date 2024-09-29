from pydantic import BaseModel
from typing import List, Literal, Optional, Dict, Any
from datetime import datetime


class CreateFormRequest(BaseModel):
    name: str
    category: str
    description: str
    is_shared: bool
    is_searchable: bool


class CreateFormResponse(BaseModel):
    name: str
    category: str
    description: str
    fields: List[str]
    is_shared: bool
    is_searchable: bool
    id: str
    user_id: str
    created_at: datetime


class FilterFormRequest(BaseModel):
    query: str
    scope: Literal["all_forms", "my_forms"]
    is_searchable: Optional[bool] = None


class FilterFormResponse(BaseModel):
    query: str
    scope: Literal["all_forms", "my_forms"]
    is_searchable: Optional[bool] = None


class Field(BaseModel):
    name: str
    field_type: str
    description: str
    is_array: bool
    fill_by_search: bool


class Form(BaseModel):
    name: str
    category: str
    description: Optional[str]
    fields: List[Field]
    is_shared: bool
    is_searchable: bool
    _id: str
    user_id: str
    created_at: str


class FilterFormResponse(BaseModel):
    forms: List[Form]


class ExecuteFormAnalyticsRequest(BaseModel):
    query: str = (
        "{\n    'reason_for_no_pymongo_pipeline': 'No user request provided'\n}"
    )
    skip: int = 0
    limit: int = 25


class FilterFormInstanceRequest(BaseModel):
    scope: Literal[
        "all_documents", "current_document", "my_documents", "shared_documents"
    ]
    status: Literal["", "NOT_STARTED", "IN_PROGRESS", "DONE", "FAILED"]
    category: Optional[str]
    query: Optional[str]
    form_id: Optional[str]
    doc_id: Optional[str]
    only_latest: bool = False
    skip: int = 0
    limit: int = 25


class WeavMetadata(BaseModel):
    modified_at: str
    status: str


class FormInstance(BaseModel):
    Name: Optional[str] = ""
    weav_metadata: Optional[WeavMetadata] = ""


class FormInstanceDetail(BaseModel):
    form_instance: Optional[FormInstance] = None
    doc_id: str
    form_id: str
    file_name: str
    status: str
    category: str
    in_folders: Optional[List[str]] = []
    owner_id: str


class FilterFormInstanceResponse(BaseModel):
    total: int
    form_instances: Optional[List[FormInstanceDetail]] = []


class Field(BaseModel):
    name: str
    field_type: str
    description: str
    is_array: bool
    fill_by_search: bool


class GetFormDefinitonResponse(BaseModel):
    name: str
    category: str
    description: str
    fields: Optional[List[Field]] = []
    is_shared: bool
    is_searchable: bool
    id: str
    user_id: str
    created_at: str


class UpdateFormDefinitonRequest(BaseModel):
    name: Optional[str]
    category: Optional[str]
    description: Optional[str]
    is_shared: Optional[bool]
    is_searchable: Optional[bool]


class DownloadQueryResultRequest(BaseModel):
    query: Optional[str]


class Metadata(BaseModel):
    _id: str
    file_name: str
    in_folders: List[str]


class Result(BaseModel):
    testEnitity1: datetime
    metadata: Metadata


class ExecuteFormAnalyticsResponse(BaseModel):
    summary: Optional[str]
    results: List[Result]
    total_count: int
    columns: List[str]


class StepStatus(BaseModel):
    status: str
    modified_at: datetime
    error: Optional[str]
    response: Optional[Dict[str, Any]] = {}


class Page(BaseModel):
    page_number: int
    media_type: str
    download_url: str
    page_text: Optional[str]
    status: str
    step_status: Optional[Dict[str, StepStatus]] = {}
    classification: Dict[str, Any]


class FormInstances(BaseModel):
    additionalProp1: Optional[Dict[str, Any]] = {}
    additionalProp2: Optional[Dict[str, Any]] = {}
    additionalProp3: Optional[Dict[str, Any]] = {}


class CreateDocumentResponse(BaseModel):
    id: str
    media_type: str
    download_url: str
    pages: List[Page]
    status: str
    file_name: str
    created_at: datetime
    size: int
    source: str
    category: Optional[str] = ""
    summary: Optional[str] = ""
    redacted_summary: Optional[str] = ""
    summary_status: Optional[str] = ""
    step_status: Optional[Dict[str, StepStatus]] = {}
    in_folders: Optional[List[str]] = []
    tags: List[str]
    ai_tags: List[Any]
    user_id: str
    tenant_id: str
    form_instances: Optional[FormInstances] = None


class StepStatusDetail(BaseModel):
    status: Optional[str]
    modified_at: Optional[datetime]
    error: Optional[str]
    response: Optional[Dict[str, Any]]


class Classification(BaseModel):
    page_class: str
    page_sections: List[str]
    page_no: Any


class EntityDetail(BaseModel):
    polygon: List[Any]
    key: str
    value: str
    label: str
    is_sensitive: bool


class ExtractedEntity(BaseModel):
    entity_group: str
    entities: List[EntityDetail]


class PageHierarchy(BaseModel):
    text: str
    type: str


class GetPageStatusResponse(BaseModel):
    page_number: int
    media_type: str
    download_url: str
    page_text: str
    status: str
    step_status: Optional[Dict[str, StepStatusDetail]] = {}
    classification: Optional[Classification]
    extracted_entities: List[ExtractedEntity]
    sensitive_words: List[Dict[str, Any]]
    summary: str
    redacted_summary: str
    page_hierarchy: Optional[List[PageHierarchy]]


class Word(BaseModel):
    content: str
    polygon: List[Dict[str, float]]
    span: Dict[str, Any]
    confidence: float


class GetPageTextResponse(BaseModel):
    page_number: int
    media_type: str
    page_text: str
    status: str
    classification: Classification
    extracted_entities: List[ExtractedEntity]
    redacted_summary: str
    words: List[Word]


class ProcessStatus(BaseModel):
    pages_done: int
    pages_failed: int


class PageLevelStatusResponse(BaseModel):
    ocr: ProcessStatus
    classification: ProcessStatus
    entity_extraction: ProcessStatus
    vectorization: ProcessStatus


class DocumentSummaryResponse(BaseModel):
    summary_status: str
    summary: Optional[str]
    redacted_summary: Optional[str]
