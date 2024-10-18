from .workflows.service import WorkflowService
from .agents.service import AgentService
from .chats.service import ChatService
from .documents.service import FormOperations, DocumentOperations, FolderOperations
from .config_models import LoadConfigurations, ServiceType

workflows = WorkflowService(
    configs=LoadConfigurations().set_config(service=ServiceType.WORKFLOWS)
)
documents = DocumentOperations(
    configs=LoadConfigurations().set_config(service=ServiceType.DOCUMENT)
)
forms = FormOperations(
    configs=LoadConfigurations().set_config(service=ServiceType.DOCUMENT)
)
folders = FolderOperations(
    configs=LoadConfigurations().set_config(service=ServiceType.DOCUMENT)
)
chats = ChatService(configs=LoadConfigurations().set_config(service=ServiceType.CHATS))
agents = AgentService(
    configs=LoadConfigurations().set_config(service=ServiceType.AGENT)
)
