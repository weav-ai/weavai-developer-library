from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Action(BaseModel):
    name: str
    description: str
    event_message: str
    input_schema: Optional[str]
    identifier: str
    llm_model_name: Optional[str] = None
    type: str
    folder_name_keywords: List[str] = Field(default_factory=list)
    folder_ids: List[str] = Field(default_factory=list)
    enable_context_relevancy_filtering: bool = True


class ActionTypes(BaseModel):
    type: str
    json_schema: Dict[str, Any]
