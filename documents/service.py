from documents.models import (
    CreateFormRequest,
    CreateFormResponse,
    FilterFormRequest,
    ExecuteFormAnalyticsRequest,
    FilterFormInstanceRequest,
    FilterFormInstanceResponse,
    FilterFormResponse,
    GetFormDefinitonResponse,
    UpdateFormDefinitonRequest,
    DownloadQueryResultRequest,
    ExecuteFormAnalyticsResponse,
    CreateDocumentResponse,
    GetPageStatusResponse,
    GetPageTextResponse,
    PageLevelStatusResponse,
    DocumentSummaryResponse,
    DocumentHierarchyResponse,
)
from config_models import ServiceEndpoints, AUTHENTICATION_FAILED_MESSAGE
from documents.exceptions import DocumentProcessingException
import requests
import urllib.parse
from typing import Optional


class FormOperations:
    def __init__(self, configs):
        self.configs = configs
        self.endpoints = ServiceEndpoints()

    def create_form(self, form_data: CreateFormRequest) -> CreateFormResponse:
        url = f"{self.configs.base_url}/{self.endpoints.CREATE_FORM}"
        response = requests.post(
            url=url,
            json=form_data.dict(),
            headers={"Authorization": f"Bearer {self.configs.auth_token}"},
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
                message="Validation failed, ensure data entered is correct",
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to create form",
                response_data=response.json(),
            )
        final_response = response.json()
        final_response["id"] = final_response.pop("_id")
        return CreateFormResponse.parse_obj(final_response)

    def filter_form(self, form_data: FilterFormRequest) -> FilterFormResponse:
        url = f"{self.configs.base_url}/{self.endpoints.FILTER_FORM}"
        params = [
            ("query", form_data.query),
            ("scope", form_data.scope),
            ("is_searchable", form_data.is_searchable),
        ]
        filtered_params = [(k, v) for k, v in params if v is not None and v != ""]
        query_string = "&".join(
            [
                f"{urllib.parse.quote(str(k))}={urllib.parse.quote(str(v))}"
                for k, v in filtered_params
            ]
        )
        response = requests.get(
            url=f"{url}?{query_string}",
            headers={"Authorization": f"Bearer {self.configs.auth_token}"},
        )
        if response.status_code == 401:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 404:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Could not find form",
                response_data="Could not find form",
            )
        elif response.status_code != 200:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to filter form data",
                response_data=response.json(),
            )

        return FilterFormResponse(forms=response.json())

    def execute_form_analytics(
        self, form_id: str, form_data: ExecuteFormAnalyticsRequest
    ) -> ExecuteFormAnalyticsResponse:
        url = f"{self.configs.base_url}/{self.endpoints.EXECUTE_FORM_ANALYTICS.format(FORM_ID=form_id)}"
        final_data = {data[0]: data[1] for data in form_data if data[1]}
        response = requests.post(
            url=url,
            json=final_data,
            headers={
                "Authorization": f"Bearer {self.configs.auth_token}",
                "Content-Type": "application/json",
            },
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
                message="Validation failed, ensure data entered is correct",
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to execute form analytics",
                response_data=response.json(),
            )
        return ExecuteFormAnalyticsResponse.parse_obj(response.json())

    def filter_form_instances(
        self, form_data: FilterFormInstanceRequest
    ) -> FilterFormInstanceResponse:
        url = f"{self.configs.base_url}/{self.endpoints.FILTER_FORM_INSTANCES}"
        params = [
            ("scope", form_data.scope),
            ("status", form_data.status),
            ("category", form_data.category),
            ("query", form_data.query),
            ("form_id", form_data.form_id),
            ("doc_id", form_data.doc_id),
            ("only_latest", form_data.only_latest),
            ("skip", form_data.skip),
            ("limit", form_data.limit),
        ]
        filtered_params = [(k, v) for k, v in params if v is not None and v != ""]
        query_string = "&".join(
            [
                f"{urllib.parse.quote(str(k))}={urllib.parse.quote(str(v))}"
                for k, v in filtered_params
            ]
        )

        response = requests.get(
            url=f"{url}?{query_string}",
            headers={"Authorization": f"Bearer {self.configs.auth_token}"},
        )
        if response.status_code == 401:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 404:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Could not find form",
                response_data="Could not find form",
            )
        elif response.status_code != 200:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to filter form instances",
                response_data=response.json(),
            )
        return FilterFormInstanceResponse.parse_obj(response.json())

    def get_form_definition(self, form_id: str) -> GetFormDefinitonResponse:
        url = f"{self.configs.base_url}/{self.endpoints.GET_FORM_DEFINITON.format(FORM_ID=form_id)}"
        response = requests.get(
            url=url,
            headers={"Authorization": f"Bearer {self.configs.auth_token}"},
        )
        if response.status_code == 401:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 404:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Form definition not found",
                response_data="Form definition not found.",
            )
        elif response.status_code != 200:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to get form definition",
                response_data=response.json(),
            )
        final_response = response.json()
        final_response["id"] = final_response.pop("_id")
        return GetFormDefinitonResponse.parse_obj(final_response)

    def update_form_definition(
        self, form_id: str, form_data: UpdateFormDefinitonRequest
    ) -> GetFormDefinitonResponse:
        url = f"{self.configs.base_url}/{self.endpoints.UPDATE_FORM_DEFINITON.format(FORM_ID=form_id)}"
        response = requests.put(
            url=url,
            json=form_data.dict(),
            headers={"Authorization": f"Bearer {self.configs.auth_token}"},
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
                message="Validation failed, ensure data entered is correct",
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to update form instances",
                response_data=response.json(),
            )
        final_response = response.json()
        final_response["id"] = final_response.pop("_id")
        return GetFormDefinitonResponse.parse_obj(final_response)

    def delete_form_definition(self, form_id: str) -> GetFormDefinitonResponse:
        url = f"{self.configs.base_url}/{self.endpoints.DELETE_FORM_DEFINITON.format(FORM_ID=form_id)}"
        response = requests.delete(
            url=url,
            headers={"Authorization": f"Bearer {self.configs.auth_token}"},
        )
        if response.status_code == 401:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to delete form definition",
                response_data=response.json(),
            )
        final_response = response.json()
        final_response["id"] = final_response.pop("_id")
        return GetFormDefinitonResponse.parse_obj(final_response)

    def download_query_result(
        self, form_id: str, download_format: str, form_data: DownloadQueryResultRequest
    ) -> GetFormDefinitonResponse:
        url = f"{self.configs.base_url}/{self.endpoints.DOWNLOAD_QUERY_RESULT.format(FORM_ID=form_id)}"
        params = [("download_format", download_format)]
        response = requests.post(
            url=url,
            params=params,
            json={"query": form_data.query},
            headers={
                "Authorization": f"Bearer {self.configs.auth_token}",
                "Content-Type": "application/json",
            },
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
                message="Validation failed, ensure data entered is correct",
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise DocumentProcessingException(
                status_code=response.status_code,
                message="Failed to download form definition",
                response_data=response.json(),
            )
        return GetFormDefinitonResponse.parse_obj(response.json())


class DocumentOperations:

    def __init__(self, configs):
        self.configs = configs
        self.endpoints = ServiceEndpoints()

    def create_document(
        self, file_path: str, folder_id: Optional[str] = ""
    ) -> CreateDocumentResponse:
        url = f"{self.configs.base_url}/{self.endpoints.CREATE_DOCUMENT}"
        files = {"file_uploaded": open(file_path, "rb")}
        data = {"folder_id": folder_id} if folder_id else {}
        headers = {
            "Authorization": f"Bearer {self.configs.auth_token}",
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
                message="Validation failed, ensure data entered is correct",
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
        return CreateDocumentResponse.parse_obj(final_response)

    def get_page(
        self, document_id: str, page_number: int, bounding_boxes: Optional[bool] = False
    ) -> GetPageStatusResponse:
        url = f"{self.configs.base_url}/{self.endpoints.GET_PAGE}".format(
            DOC_ID=document_id, PAGE_NUMBER=page_number
        )
        headers = {
            "Authorization": f"Bearer {self.configs.auth_token}",
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
                message="Validation failed, ensure data entered is correct",
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

        return GetPageStatusResponse.parse_obj(response.json())

    def get_page_text_and_words(
        self, document_id: str, page_number: int
    ) -> GetPageTextResponse:
        url = (
            f"{self.configs.base_url}/{self.endpoints.GET_PAGE_TEXT_AND_WORDS}".format(
                DOC_ID=document_id, PAGE_NUMBER=page_number
            )
        )
        headers = {
            "Authorization": f"Bearer {self.configs.auth_token}",
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
                message="Validation failed, ensure data entered is correct",
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
        return GetPageTextResponse.parse_obj(response.json())

    def get_page_level_status(self, document_id: str) -> PageLevelStatusResponse:
        url = f"{self.configs.base_url}/{self.endpoints.GET_PAGE_LEVEL_STATUS}".format(
            DOC_ID=document_id
        )
        headers = {
            "Authorization": f"Bearer {self.configs.auth_token}",
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
                message="Validation failed, ensure data entered is correct",
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
        return PageLevelStatusResponse.parse_obj(response.json())

    def get_document_summary_status(self, document_id: str) -> DocumentSummaryResponse:
        url = f"{self.configs.base_url}/{self.endpoints.GET_DOCUMENT_SUMMARY_STATUS}".format(
            DOC_ID=document_id
        )
        headers = {
            "Authorization": f"Bearer {self.configs.auth_token}",
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
                message="Validation failed, ensure data entered is correct",
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
        return DocumentSummaryResponse.parse_obj(response.json())

    def get_document(
        self, document_id: str, fill_pages: Optional[bool] = False
    ) -> CreateDocumentResponse:
        url = f"{self.configs.base_url}/{self.endpoints.GET_DOCUMENT}".format(
            DOC_ID=document_id
        )
        headers = {
            "Authorization": f"Bearer {self.configs.auth_token}",
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
                message="Validation failed, ensure data entered is correct",
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
        return CreateDocumentResponse.parse_obj(final_response)

    def get_document_hierarchy(self, document_id: str) -> DocumentHierarchyResponse:
        url = f"{self.configs.base_url}/{self.endpoints.GET_DOCUMENT_HIERARCHY}".format(
            DOC_ID=document_id
        )
        headers = {
            "Authorization": f"Bearer {self.configs.auth_token}",
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
                message="Validation failed, ensure data entered is correct",
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

        return DocumentHierarchyResponse.parse_obj(response.json())
