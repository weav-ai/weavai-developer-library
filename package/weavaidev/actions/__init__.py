import requests
from weavaidev import Config
from weavaidev.actions.exceptions import ActionOperationsException
from weavaidev.actions.models import Action
from weavaidev.config_models import (
    AUTHENTICATION_FAILED_MESSAGE,
    ServiceEndpoints,
    ServiceType,
    get_base_url,
)


class ActionOperations:
    def __init__(self, config: Config):
        self.config = config
        self.endpoints = ServiceEndpoints()
        self.base_url = get_base_url(config=config, service=ServiceType.AGENT)

    def get_action_types(self):
        """
        Retrieves the available action types from the configured API endpoint.

        Constructs the URL using the base URL and the endpoint for fetching action types.
        Sends a GET request to this URL, with an authorization token included in the headers.

        Returns:
            List[Dict]: A JSON response containing the action types.

        Raises:
            ActionOperationsException: Raised if the request fails with a 401 (Unauthorized),
            404 (Not Found), or any other error status. Provides details on the status code,
            message, and response data for debugging.
        """
        url = f"{self.base_url}/{self.endpoints.GET_ACTION_TYPES}"
        response = requests.get(
            url=url,
            headers={"Authorization": f"Bearer {self.config.auth_token._secret_value}"},
        )
        if response.status_code == 401:
            raise ActionOperationsException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 404:
            raise ActionOperationsException(
                status_code=response.status_code,
                message="Failed to find actions",
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise ActionOperationsException(
                status_code=response.status_code,
                message="Failed to get actions",
                response_data=response.json(),
            )
        return response.json()

    def get_action_type_configuration(self, action_type: str) -> Action:
        """
        Fetches the configuration details for a specified action type from the API.

        Args:
            action_type (str): The unique identifier for the action type to retrieve its configuration.

        Returns:
            Action: An `Action` instance populated with configuration data from the API response.

        Raises:
            ActionOperationsException: Raised if the request fails with a 401 (Unauthorized),
                404 (Not Found), or other non-200 status codes. The exception provides the
                status code, an error message, and the response data for debugging purposes.
                Specific error messages include:
                - Authentication failure if the status code is 401.
                - "Failed to find action {action_type}" if the action type is not found (404).
                - "Failed to get action configuration" for any other errors.
        """
        url = f"{self.base_url}/{self.endpoints.GET_ACTION_TYPE_CONFIGURATIONS}".format(
            ACTION_TYPE=action_type
        )
        response = requests.get(
            url=url,
            headers={"Authorization": f"Bearer {self.config.auth_token._secret_value}"},
        )
        if response.status_code == 401:
            raise ActionOperationsException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 404:
            raise ActionOperationsException(
                status_code=response.status_code,
                message=f"Failed to find action {action_type}",
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise ActionOperationsException(
                status_code=response.status_code,
                message="Failed to get action configuration",
                response_data=response.json(),
            )
        return Action.model_validate(response.json())
