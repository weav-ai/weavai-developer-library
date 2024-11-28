from typing import Optional

import requests
from weavaidev import Config
from weavaidev.config_models import (
    AUTHENTICATION_FAILED_MESSAGE,
    VALIDATION_FAILED_MESSAGE,
    ServiceEndpoints,
    ServiceType,
    get_base_url,
)
from weavaidev.folders.exceptions import FolderProcessingException
from weavaidev.folders.models import (
    CreateFolderRequest,
    CreateFolderResponse,
    WritableFoldersResponse,
)


class FolderOperations:
    def __init__(self, config: Config):
        self.config = config
        self.endpoints = ServiceEndpoints()
        self.base_url = get_base_url(config=config, service=ServiceType.DOCUMENT)

    def create_folder(
        self, name: str, category: Optional[str] = "", description: Optional[str] = ""
    ) -> CreateFolderResponse:
        """Creates a new folder based on the provided request.

        This method sends a request to create a folder with the specified name, category, and description.

        Args:
            - name (str): The name of the folder to be created.
            - category (Optional[str]): The category for the folder. Defaults to an empty string.
            - description (Optional[str]): The description of the folder. Defaults to an empty string.

        Raises:
            FolderProcessingException: Raised if authentication fails (status code 401).
            FolderProcessingException: Raised if folder validation fails (status code 422).
            FolderProcessingException: Raised if any other error occurs while creating the folder.

        Returns:
            CreateFolderResponse: A response object containing details about the created folder, including its ID, documents, and workflow.
        """
        url = f"{self.base_url}/{self.endpoints.CREATE_FOLDER}"
        folder_request = CreateFolderRequest(
            name=name, category=category, description=description
        )
        headers = {
            "Authorization": f"Bearer {self.config.auth_token._secret_value}",
            "Accept": "application/json",
        }
        response = requests.post(url, headers=headers, json=folder_request.model_dump())

        if response.status_code == 401:
            raise FolderProcessingException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 422:
            raise FolderProcessingException(
                status_code=response.status_code,
                message=VALIDATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise FolderProcessingException(
                status_code=response.status_code,
                message="Failed to create folder",
                response_data=response.json(),
            )

        final_response = response.json()
        final_response["id"] = final_response.pop("_id")
        return CreateFolderResponse.model_validate(final_response)

    def get_writable_folders(self) -> WritableFoldersResponse:
        """Fetches a list of writable folders that the user has access to.

        This method retrieves folders where the user has write access, returning folder names and IDs.

        Raises:
            FolderProcessingException: Raised if authentication fails (status code 401).
            FolderProcessingException: Raised if the request fails (status code 422 or any other non-200 status).

        Returns:
            WritableFoldersResponse: A response object containing a list of folders the user can write to.
        """
        url = f"{self.base_url}/{self.endpoints.GET_WRITABLE_FOLDERS}"
        headers = {
            "Authorization": f"Bearer {self.config.auth_token._secret_value}",
            "Accept": "application/json",
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 401:
            raise FolderProcessingException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 422:
            raise FolderProcessingException(
                status_code=response.status_code,
                message=VALIDATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise FolderProcessingException(
                status_code=response.status_code,
                message="Failed to get writable folder",
                response_data=response.json(),
            )

        return WritableFoldersResponse(folders=response.json())

    def get_folder_definition(self, folder_id: str) -> CreateFolderResponse:
        """Fetches the definition of a specific folder.

        This method retrieves detailed information about a folder, including its documents, workflow, and metadata.

        Args:
            folder_id (str): The ID of the folder for which the definition is being fetched.

        Raises:
            FolderProcessingException: Raised if authentication fails (status code 401).
            FolderProcessingException: Raised if folder validation fails (status code 422).
            FolderProcessingException: Raised if any other error occurs while retrieving the folder definition.

        Returns:
            CreateFolderResponse: A response object containing the details of the folder, including its documents, workflow, and metadata.
        """
        url = f"{self.base_url}/{self.endpoints.GET_FOLDER_DEFINITION.format(FOLDER_ID=folder_id)}"
        headers = {
            "Authorization": f"Bearer {self.config.auth_token._secret_value}",
            "Accept": "application/json",
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 401:
            raise FolderProcessingException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 422:
            raise FolderProcessingException(
                status_code=response.status_code,
                message=VALIDATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 404:
            raise FolderProcessingException(
                status_code=response.status_code,
                message="Failed to find folder",
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise FolderProcessingException(
                status_code=response.status_code,
                message="Failed to get folder definition",
                response_data=response.json(),
            )
        final_response = response.json()
        final_response["id"] = final_response.pop("_id")
        return CreateFolderResponse.model_validate(final_response)
