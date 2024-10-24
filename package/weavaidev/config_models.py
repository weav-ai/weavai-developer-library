from enum import Enum

from weavaidev import Config

VALIDATION_FAILED_MESSAGE = "Validation failed, ensure data entered is correct"
AUTHENTICATION_FAILED_MESSAGE = "Authentication failed, please check AUTH token"

BOOL_CHOICES = ["True", "t", "true", "False", "f", "false"]


class EnvTypes(str, Enum):
    LOCAL = "local"
    OTHER = "other"


class ServiceType(str, Enum):
    WORKFLOWS = "workflows"
    AGENT = "agent"
    DOCUMENT = "document"
    CHATS = "chats"


url_mapping = {
    EnvTypes.LOCAL: {
        ServiceType.WORKFLOWS: "http://localhost:7036",
        ServiceType.AGENT: "http://localhost:7031",
        ServiceType.DOCUMENT: "http://localhost:7015",
        ServiceType.CHATS: "http://localhost:7030",
    },
    EnvTypes.OTHER: {
        ServiceType.AGENT: "/agent-prototype",
        ServiceType.WORKFLOWS: "workflow-service",
        ServiceType.DOCUMENT: "/file-service",
        ServiceType.CHATS: "/chat-service",
    },
}


def get_base_url(config: Config, service: ServiceType):
    if config.env == EnvTypes.LOCAL:
        return url_mapping.get(EnvTypes.LOCAL, "Unknown environment").get(service)
    endpoint = url_mapping.get(EnvTypes.OTHER, "Unknown environment").get(service)
    return f"{config.env}{endpoint}"


class ServiceEndpoints:
    def __init__(self):
        self.GET_ALL_WORKFLOWS = "/workflows/?"
        self.GET_SINGLE_WORKFLOW = "/workflows/{WORKFLOW_NAME}"
        self.SKIP_TASK_IN_WORKFLOW = "/workflows/{WORKFLOW_NAME}/skip_tasks"
        self.RERUN_WORKFLOW = "workflows/{WORKFLOW_NAME}/re_run"
        self.RUN_WORKFLOW = "/workflows/{WORKFLOW_NAME}/run"
        self.WORKFLOW_STATUS = "/workflows/{WORKFLOW_ID}/{WORKFLOW_RUN_ID}/status"
        self.WORKFLOW_RUNS = "/workflows/workflow_runs"
        self.GET_AGENT_TYPES = "agent/types"
        self.GET_AGENT_RESPONSE = "agent"
        self.GET_CHAT_HISTORY = "agent/chat_history?chat_id={CHAT_ID}"
        self.DELETE_CHAT_HISTORY = "agent/delete/chat"
        self.CREATE_FORM = "forms/"
        self.FILTER_FORM = "forms/"
        self.EXECUTE_FORM_ANALYTICS = "forms/{FORM_ID}/analytics/"
        self.FILTER_FORM_INSTANCES = "forms/instances/"
        self.GET_FORM_DEFINITON = "forms/{FORM_ID}"
        self.UPDATE_FORM_DEFINITON = "/forms/{FORM_ID}"
        self.DELETE_FORM_DEFINITON = "/forms/{FORM_ID}"
        self.DOWNLOAD_QUERY_RESULT = "forms/{FORM_ID}/analytics/download"
        self.CREATE_DOCUMENT = "/documents/"
        self.GET_PAGE = "documents/{DOC_ID}/pages/{PAGE_NUMBER}"
        self.GET_PAGE_TEXT_AND_WORDS = "documents/{DOC_ID}/pages/{PAGE_NUMBER}/words"
        self.GET_PAGE_LEVEL_STATUS = "documents/{DOC_ID}/pages/status"
        self.GET_DOCUMENT_SUMMARY_STATUS = "documents/{DOC_ID}/summary"
        self.GET_DOCUMENT = "documents/{DOC_ID}"
        self.GET_DOCUMENT_HIERARCHY = "documents/{DOC_ID}/hierarchy"
        self.DOWNLOAD_FORM_INSTANCE = "documents/{DOC_ID}/form/"
        self.GET_DOCUMENT_CATEGORIES = "documents/categories/"
        self.GET_DOCUMENT_TAGS = "documents/tags/"
        self.TRIGGER_DOCUMENT_SUMMARY = "documents/{DOC_ID}/summary"
        self.CHAT_LOGS = "/chat_logs/"
        self.CHAT_HISTORY = "/chat_history"
        self.CHAT = "/chat"
        self.CREATE_FOLDER = "/folders/"
        self.GET_WRITABLE_FOLDERS = "/folders/writable-folders/"
        self.GET_FOLDER_DEFINITION = "/folders/{FOLDER_ID}"
