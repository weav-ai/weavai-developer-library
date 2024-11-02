import contextlib
from typing import List

import requests
from pydantic import ValidationError
from weavaidev import Config
from weavaidev.agents.exceptions import AgentServiceException
from weavaidev.agents.models import (
    ChatHistoryResponse,
    GetAgentRequest,
    GetAgentResponse,
    GetAllAgentsResponse,
)
from weavaidev.config_models import (
    AUTHENTICATION_FAILED_MESSAGE,
    VALIDATION_FAILED_MESSAGE,
    ServiceEndpoints,
    ServiceType,
    get_base_url,
)


class AgentOperations:
    def __init__(self, config: Config):
        self.config = config
        self.endpoints = ServiceEndpoints()
        self.base_url = get_base_url(config=config, service=ServiceType.AGENT)

    def get_agent_types(self) -> GetAllAgentsResponse:
        """Fetches all available agent types.

        This method sends a request to retrieve the different types of agents that
        are available in the system.

        Raises:
            AgentServiceException: Raised if authentication fails (status code 401).
            AgentServiceException: Raised if any other error occurs while fetching agent types.

        Returns:
            GetAllAgentsResponse: A response object containing a list of available agent types.
        """
        url = f"{self.base_url}/{self.endpoints.GET_AGENT_TYPES}"
        response = requests.get(
            url=url, headers={"Authorization": f"Bearer {self.config.auth_token}"}
        )
        if response.status_code == 401:
            raise AgentServiceException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise AgentServiceException(
                status_code=response.status_code,
                message="Failed to get agent types",
                response_data=response.json(),
            )
        return GetAllAgentsResponse(response=response.json())

    def get_agent_response(
        self, user_input: str, chat_id: str, agent_type: str, stream: bool = False
    ) -> List[GetAgentResponse]:
        """Fetches the response from an agent based on the user input.

        This method sends a request to retrieve the response of a specified agent
        for a given user input, chat ID, and other parameters.

        Args:
            - user_input (str): The user's input to which the agent responds.
            - chat_id (str): The unique identifier for the chat session.
            - stream (bool): A flag indicating whether the response should be streamed.
            - agent_type (str): The type of agent to use for generating the response.

        Raises:
            AgentServiceException: Raised if authentication fails (status code 401).
            AgentServiceException: Raised if form validation fails (status code 422).
            AgentServiceException: Raised if any other error occurs while getting the agent response.

        Returns:
            List[GetAgentResponse]: A list of agent responses parsed from server-sent events (SSE).
        """
        url = f"{self.base_url}/{self.endpoints.GET_AGENT_RESPONSE}"
        get_agent_request_body = GetAgentRequest(
            user_input=user_input, chat_id=chat_id, stream=stream, agent_type=agent_type
        )
        response = requests.post(
            url=url,
            json=get_agent_request_body.model_dump(),
            headers={"Authorization": f"Bearer {self.config.auth_token}"},
        )
        if response.status_code == 401:
            raise AgentServiceException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 422:
            raise AgentServiceException(
                status_code=response.status_code,
                message=VALIDATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise AgentServiceException(
                status_code=response.status_code,
                message="Failed to get agent types",
                response_data=response.json(),
            )

        def parse_sse_event(event_string: str) -> GetAgentResponse:
            lines = event_string.splitlines()
            event_data = {}

            for line in lines:
                if line.startswith("data:"):
                    event_data["data"] = line[len("data: ") :].strip()
                elif line.startswith("id:"):
                    event_data["id"] = line[len("id: ") :].strip()
                elif line.startswith("event:"):
                    event_data["event"] = line[len("event: ") :].strip()
                elif line.startswith("retry:"):
                    event_data["retry"] = int(line[len("retry: ") :].strip())

            with contextlib.suppress(ValidationError):
                return GetAgentResponse(**event_data)

        resp = []
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8")
                event = parse_sse_event(decoded_line)
                resp.append(event)
        return resp

    def get_chat_history(self, chat_id: str) -> ChatHistoryResponse:
        """Fetches the chat history for a specific chat session.

        This method retrieves the entire chat history for the given `chat_id`.

        Args:
            chat_id (str): The unique identifier of the chat session for which the history
                is being retrieved.

        Raises:
            AgentServiceException: Raised if authentication fails (status code 401).
            AgentServiceException: Raised if any other error occurs while fetching the chat history.

        Returns:
            ChatHistoryResponse: A response object containing a list of messages for the chat session.
        """
        url = (
            f"{self.base_url}/{self.endpoints.GET_CHAT_HISTORY.format(CHAT_ID=chat_id)}"
        )
        response = requests.get(
            url=url,
            headers={"Authorization": f"Bearer {self.config.auth_token}"},
        )
        if response.status_code == 401:
            raise AgentServiceException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise AgentServiceException(
                status_code=response.status_code,
                message="Failed to get chat history",
                response_data=response.json(),
            )
        return ChatHistoryResponse(**response.json())

    def delete_chat_history(self, chat_id: str) -> str:
        """Deletes the chat history for a specific chat session.

        This method sends a request to delete the chat history for the given `chat_id`.

        Args:
            chat_id (str): The unique identifier of the chat session to be deleted.

        Raises:
            AgentServiceException: Raised if authentication fails (status code 401).
            AgentServiceException: Raised if form validation fails (status code 422).
            AgentServiceException: Raised if any other error occurs while deleting the chat history.

        Returns:
            str: A string message indicating the success of the operation.
        """
        url = f"{self.base_url}/{self.endpoints.DELETE_CHAT_HISTORY}"
        response = requests.delete(
            url=url,
            json={"chat_id": chat_id},
            headers={"Authorization": f"Bearer {self.config.auth_token}"},
        )
        if response.status_code == 401:
            raise AgentServiceException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 422:
            raise AgentServiceException(
                status_code=response.status_code,
                message=VALIDATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise AgentServiceException(
                status_code=response.status_code,
                message="Failed to get chat history",
                response_data=response.json(),
            )
        return "Success"
