from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class StepStatus(BaseModel):
    status: str
    modified_at: datetime
    error: Optional[str] = ""
    response: Optional[Dict[str, Any]] = {}


class Page(BaseModel):
    page_number: int
    media_type: str
    download_url: str
    page_text: Optional[str] = ""
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
    status: Optional[str] = ""
    modified_at: Optional[datetime] = None
    error: Optional[str] = ""
    response: Optional[Dict[str, Any]] = {}


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
    classification: Optional[Classification] = None
    extracted_entities: Optional[List[ExtractedEntity]] = []
    sensitive_words: List[Dict[str, Any]]
    summary: Optional[str] = ""
    redacted_summary: Optional[str] = ""
    page_hierarchy: Optional[List[PageHierarchy]] = None


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
    summary: Optional[str] = ""
    redacted_summary: Optional[str] = ""


class DocumentHierarchyResponse(BaseModel):
    hierarchy: List[Any] = []


class DocumentCategoriesResponse(BaseModel):
    categories: List[str] = []


class DocumentTagResponse(BaseModel):
    tags: List[List[str]] = [[]]
