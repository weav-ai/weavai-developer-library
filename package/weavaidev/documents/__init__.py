import os
from io import StringIO
from typing import Any, Dict, Literal, Optional, Union

import pandas as pd
import requests
from weavaidev import Config
from weavaidev.config_models import (
    AUTHENTICATION_FAILED_MESSAGE,
    VALIDATION_FAILED_MESSAGE,
    ServiceEndpoints,
    ServiceType,
    get_base_url,
)
from weavaidev.documents.exceptions import DocumentProcessingException
from weavaidev.documents.models import (
    CreateDocumentResponse,
    DocumentCategoriesResponse,
    DocumentHierarchyResponse,
    DocumentSummaryResponse,
    DocumentTagResponse,
    GetPageStatusResponse,
    GetPageTextResponse,
    PageLevelStatusResponse,
)


class DocumentOperations:
    def __init__(self, config: Config):
        self.config = config
        self.endpoints = ServiceEndpoints()
        self.base_url = get_base_url(config=config, service=ServiceType.DOCUMENT)

    def create_document(
        self, file_path: str, folder_id: Optional[str] = ""
    ) -> CreateDocumentResponse:
        """Uploads a document to the system and creates a new document record.

        Args:
            file_path (str): The path to the document file that is being uploaded.
            folder_id (Optional[str]): The ID of the folder in which to place the document, if any. Defaults to an empty string.

        Raises:
            FileNotFoundError: Raised if the specified file path does not exist.
            DocumentProcessingException: Raised if authentication fails (status code 401),
                validation fails (status code 422), or any other error occurs during document creation.

        Returns:
            CreateDocumentResponse: A response object containing the details of the created document, including ID, pages, status, etc.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{file_path}' not found.")
        url = f"{self.base_url}/{self.endpoints.CREATE_DOCUMENT}"
        files = {"file_uploaded": open(file_path, "rb")}
        data = {"folder_id": folder_id} if folder_id else {}
        headers = {
            "Authorization": f"Bearer {self.config.auth_token}",
            "Accept": "application/json",
        }
        response = requests.post(url, headers=headers, files=files, data=data)

        if response.status_code == 401:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 422:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message=VALIDATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to create document",
                response_data=response.json(),
            )

        final_response = response.json()
        final_response["id"] = final_response.pop("_id")
        return CreateDocumentResponse.model_validate(final_response)

    def get_page(
        self, document_id: str, page_number: int, bounding_boxes: Optional[bool] = False
    ) -> GetPageStatusResponse:
        """Fetches the status and details of a specific page from a document.

        Args:
            document_id (str): The ID of the document from which the page is fetched.
            page_number (int): The page number within the document.
            bounding_boxes (Optional[bool]): A flag to include bounding boxes for text on the page. Defaults to False.

        Raises:
            DocumentProcessingException: Raised if authentication fails (status code 401),
                validation fails (status code 422), or if the document or page is not found (status code 404).

        Returns:
            GetPageStatusResponse: A response object containing the status and details of the specified page, including step statuses, classification, and extracted entities.
        """
        url = f"{self.base_url}/{self.endpoints.GET_PAGE}".format(
            DOC_ID=document_id, PAGE_NUMBER=page_number
        )
        headers = {
            "Authorization": f"Bearer {self.config.auth_token}",
        }
        response = requests.get(
            url, headers=headers, params=[("bounding_boxes", bounding_boxes)]
        )

        if response.status_code == 401:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 422:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message=VALIDATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 404:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to find document",
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to get page",
                response_data=response.json(),
            )

        return GetPageStatusResponse.model_validate(response.json())

    def get_page_text_and_words(
        self, document_id: str, page_number: int
    ) -> GetPageTextResponse:
        """Retrieves the text and word-level details of a specific page from a document.

        Args:
            document_id (str): The ID of the document from which the page is fetched.
            page_number (int): The page number within the document.

        Raises:
            DocumentProcessingException: Raised if authentication fails (status code 401),
                validation fails (status code 422), or if the document or page is not found (status code 404).

        Returns:
            GetPageTextResponse: A response object containing the text, words, extracted entities, and classification details for the specified page.
        """
        url = f"{self.base_url}/{self.endpoints.GET_PAGE_TEXT_AND_WORDS}".format(
            DOC_ID=document_id, PAGE_NUMBER=page_number
        )
        headers = {
            "Authorization": f"Bearer {self.config.auth_token}",
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 401:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 422:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message=VALIDATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 404:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to find document",
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to get page",
                response_data=response.json(),
            )
        return GetPageTextResponse.model_validate(response.json())

    def get_page_level_status(self, document_id: str) -> PageLevelStatusResponse:
        """Fetches the page-level status for a document, including OCR, classification, and entity extraction progress.

        Args:
            document_id (str): The ID of the document for which page-level status is being fetched.

        Raises:
            DocumentProcessingException: Raised if authentication fails (status code 401),
                validation fails (status code 422), or if the document is not found (status code 404).

        Returns:
            PageLevelStatusResponse: A response object containing the status of various processes (OCR, classification, entity extraction) for the document's pages.
        """
        url = f"{self.base_url}/{self.endpoints.GET_PAGE_LEVEL_STATUS}".format(
            DOC_ID=document_id
        )
        headers = {
            "Authorization": f"Bearer {self.config.auth_token}",
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 401:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 422:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message=VALIDATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 404:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to find document",
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to get page level status",
                response_data=response.json(),
            )
        return PageLevelStatusResponse.model_validate(response.json())

    def get_document_summary_status(self, document_id: str) -> DocumentSummaryResponse:
        """Retrieves the summary and redacted summary status for a document.

        Args:
            document_id (str): The ID of the document for which the summary is being fetched.

        Raises:
            DocumentProcessingException: Raised if authentication fails (status code 401),
                validation fails (status code 422), or if the document is not found (status code 404).

        Returns:
            DocumentSummaryResponse: A response object containing the summary, redacted summary, and summary status of the document.
        """
        url = f"{self.base_url}/{self.endpoints.GET_DOCUMENT_SUMMARY_STATUS}".format(
            DOC_ID=document_id
        )
        headers = {
            "Authorization": f"Bearer {self.config.auth_token}",
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 401:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 422:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message=VALIDATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 404:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to find document",
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to get summary status",
                response_data=response.json(),
            )
        return DocumentSummaryResponse.model_validate(response.json())

    def get_document(
        self, document_id: str, fill_pages: Optional[bool] = False
    ) -> CreateDocumentResponse:
        """Fetches the details of a document, including its pages and metadata.

        Args:
            document_id (str): The ID of the document to fetch.
            fill_pages (Optional[bool]): A flag indicating whether to include detailed page data in the response. Defaults to False.

        Raises:
            DocumentProcessingException: Raised if authentication fails (status code 401),
                validation fails (status code 422), or if the document is not found (status code 404).

        Returns:
            CreateDocumentResponse: A response object containing the document's details, including metadata, pages, and status.
        """
        url = f"{self.base_url}/{self.endpoints.GET_DOCUMENT}".format(
            DOC_ID=document_id
        )
        headers = {
            "Authorization": f"Bearer {self.config.auth_token}",
        }
        params = [("fill_pages", fill_pages)]
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 401:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 422:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message=VALIDATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 404:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to find document",
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to get document",
                response_data=response.json(),
            )
        final_response = response.json()
        final_response["id"] = final_response.pop("_id")
        return CreateDocumentResponse.model_validate(final_response)

    def get_document_hierarchy(self, document_id: str) -> DocumentHierarchyResponse:
        """Retrieves the hierarchical structure of the document.

        Args:
            document_id (str): The ID of the document for which the hierarchy is being fetched.

        Raises:
            DocumentProcessingException: Raised if authentication fails (status code 401),
                validation fails (status code 422), or if the document is not found (status code 404).

        Returns:
            DocumentHierarchyResponse: A response object containing the hierarchy of the document, typically used for understanding document structure.
        """
        url = f"{self.base_url}/{self.endpoints.GET_DOCUMENT_HIERARCHY}".format(
            DOC_ID=document_id
        )
        headers = {
            "Authorization": f"Bearer {self.config.auth_token}",
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 401:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 422:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message=VALIDATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 404:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to find document",
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to get document hierarchy",
                response_data=response.json(),
            )

        return DocumentHierarchyResponse.model_validate(response.json())

    def download_form_instance(
        self, document_id: str, download_format: Literal["JSON", "CSV"] = "JSON"
    ) -> Union[Dict[str, Any], pd.DataFrame]:
        """Downloads a form instance from a document in the specified format.

        Args:
            document_id (str): The ID of the document for which the form instance is being downloaded.
            download_format (Literal[str]): The format in which the form instance should be downloaded (e.g., CSV, JSON).

        Raises:
            DocumentProcessingException: Raised if authentication fails (status code 401),
                validation fails (status code 422), or if the document or form instance is not found (status code 404).

        Returns:
            Union[Dict[str, Any], pd.DataFrame]: The form instance data in the specified format. If CSV format is requested, it returns a pandas DataFrame.
        """
        url = f"{self.base_url}/{self.endpoints.DOWNLOAD_FORM_INSTANCE}".format(
            DOC_ID=document_id
        )
        headers = {
            "Authorization": f"Bearer {self.config.auth_token}",
        }
        params = [("download_format", download_format)]
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 401:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 422:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message=VALIDATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 404:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to find document",
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to download form instance",
                response_data=response.json(),
            )

        if download_format != "CSV":
            return response.json()
        data = StringIO(response.text)
        return pd.read_csv(data)

    def get_document_categories(self) -> DocumentCategoriesResponse:
        """Fetches all available document categories.

        Raises:
            DocumentProcessingException: Raised if authentication fails (status code 401),
                validation fails (status code 422), or if the request fails.

        Returns:
            DocumentCategoriesResponse: A response object containing a list of available document categories.
        """
        url = f"{self.base_url}/{self.endpoints.GET_DOCUMENT_CATEGORIES}"
        headers = {
            "Authorization": f"Bearer {self.config.auth_token}",
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 401:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 422:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message=VALIDATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 404:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to find document",
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to get document categories",
                response_data=response.json(),
            )
        return DocumentCategoriesResponse(**response.json())

    def get_document_tags(self) -> DocumentTagResponse:
        """Retrieves all available document tags.

        Raises:
            DocumentProcessingException: Raised if authentication fails (status code 401),
                validation fails (status code 422), or if the request fails.

        Returns:
            DocumentTagResponse: A response object containing a list of available tags for documents.
        """
        url = f"{self.base_url}/{self.endpoints.GET_DOCUMENT_TAGS}"
        headers = {
            "Authorization": f"Bearer {self.config.auth_token}",
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 401:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 422:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message=VALIDATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 404:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to find document",
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to get document tags",
                response_data=response.json(),
            )
        return DocumentTagResponse(**response.json())

    def trigger_document_summary(self, document_id: str) -> DocumentSummaryResponse:
        """Triggers the generation of a document summary.

        Args:
            document_id (str): The ID of the document for which the summary is being generated.

        Raises:
            DocumentProcessingException: Raised if authentication fails (status code 401),
                validation fails (status code 422), or if the document is not found (status code 404).

        Returns:
            DocumentSummaryResponse: A response object containing the summary and redacted summary of the document.
        """
        url = f"{self.base_url}/{self.endpoints.TRIGGER_DOCUMENT_SUMMARY.format(DOC_ID=document_id)}"
        headers = {
            "Authorization": f"Bearer {self.config.auth_token}",
        }

        response = requests.post(url, headers=headers)

        if response.status_code == 401:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 422:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message=VALIDATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 404:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to find document",
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to trigger document summary",
                response_data=response.json(),
            )
        return DocumentSummaryResponse.model_validate(response.json())
