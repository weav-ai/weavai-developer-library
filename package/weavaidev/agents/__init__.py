import contextlib
from typing import List

import requests
from pydantic import ValidationError
from weavaidev import Config
from weavaidev.agents.exceptions import AgentServiceException
from weavaidev.agents.models import (
    AgentConfiguration,
    AgentConfigurations,
    GetAgentRequest,
    GetAgentResponse,
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

    def get_all_agents(self) -> AgentConfigurations:
        """Fetches all available agent types.

        This method sends a request to retrieve the different types of agents that
        are available in the system.

        Raises:
            AgentServiceException: Raised if authentication fails (status code 401).
            AgentServiceException: Raised if any other error occurs while fetching agent types.

        Returns:
            AgentConfigurations: A response object containing a list of available agent configurations.
        """
        url = f"{self.base_url}/{self.endpoints.GET_AGENT_CONFIGURATIONS}"
        response = requests.get(
            url=url,
            headers={"Authorization": f"Bearer {self.config.auth_token._secret_value}"},
        )
        if response.status_code == 401:
            raise AgentServiceException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        if response.status_code == 404:
            raise AgentServiceException(
                status_code=response.status_code,
                message="Failed to find agent configurations",
                response_data=None,
            )
        elif response.status_code != 200:
            raise AgentServiceException(
                status_code=response.status_code,
                message="Failed to get agent types",
                response_data=response.json(),
            )
        response_json = response.json()

        transformed_data = [
            {("id" if k == "_id" else k): v for k, v in d.items()}
            for d in response_json
        ]
        return AgentConfigurations(configurations=transformed_data)

    def get_agent_response(
        self, user_input: str, chat_id: str, agent_id: str, stream: bool = False
    ) -> List[GetAgentResponse]:
        """Fetches the response from an agent based on the user input.

        This method sends a request to retrieve the response of a specified agent
        for a given user input, chat ID, and other parameters.

        Args:
            - user_input (str): The user's input to which the agent responds.
            - chat_id (str): The unique identifier for the chat session.
            - stream (bool): A flag indicating whether the response should be streamed.
            - agent_id (str): The unique identifier of agent to use for generating the response.

        Raises:
            AgentServiceException: Raised if authentication fails (status code 401).
            AgentServiceException: Raised if form validation fails (status code 422).
            AgentServiceException: Raised if any other error occurs while getting the agent response.

        Returns:
            List[GetAgentResponse]: A list of agent responses parsed from server-sent events (SSE).
        """
        url = f"{self.base_url}/{self.endpoints.GET_AGENT_RESPONSE}"
        get_agent_request_body = GetAgentRequest(
            user_input=user_input, chat_id=chat_id, stream=stream, agent_id=agent_id
        )
        response = requests.post(
            url=url,
            json=get_agent_request_body.model_dump(),
            headers={"Authorization": f"Bearer {self.config.auth_token._secret_value}"},
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

    def get_agent(self, agent_id: str) -> AgentConfiguration:
        """
        Fetches the configuration details for a specified agent from the API.

        Args:
            agent_id (str): The unique identifier for the agent to retrieve its configuration details.

        Returns:
            AgentConfiguration: An instance of `AgentConfiguration` populated with data from the API response.

        Raises:
            AgentServiceException: Raised if the request fails with a 401 (Unauthorized),
                404 (Not Found), or other non-200 status codes. Specific error cases include:
                - Authentication failure if the status code is 401, with the message defined in `AUTHENTICATION_FAILED_MESSAGE`.
                - "Failed to find agent with ID {agent_id}" if the agent ID is not found (404).
                - "Failed to get agent history" for any other unexpected error codes.

        Notes:
            - If the request succeeds, the response's first item (assumed to contain the agent data) is transformed by renaming
            `_id` to `id` to fit the `AgentConfiguration` model requirements.
            - The method expects the response data to contain a list where the first item holds the agent configuration data.
        """

        url = f"{self.base_url}/{self.endpoints.GET_AGENT.format(AGENT_ID=agent_id)}"
        response = requests.get(
            url=url,
            headers={"Authorization": f"Bearer {self.config.auth_token._secret_value}"},
        )
        if response.status_code == 401:
            raise AgentServiceException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 404:
            raise AgentServiceException(
                status_code=response.status_code,
                message=f"Failed to find agent with ID {agent_id}",
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise AgentServiceException(
                status_code=response.status_code,
                message="Failed to get agent history",
                response_data=response.json(),
            )
        response_json = response.json()[0]
        response_json["id"] = response_json.pop("_id")
        return AgentConfiguration.model_validate(response_json)
