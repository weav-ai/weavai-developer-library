import urllib.parse
from io import StringIO
from typing import Union

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
from weavaidev.forms.exceptions import FormProcessingException
from weavaidev.forms.models import (
    CreateFormRequest,
    CreateFormResponse,
    DownloadQueryResultRequest,
    DownloadQueryResultResponse,
    ExecuteFormAnalyticsRequest,
    ExecuteFormAnalyticsResponse,
    FilterFormInstanceRequest,
    FilterFormInstanceResponse,
    FilterFormRequest,
    FilterFormResponse,
    GetFormDefinitonResponse,
    UpdateFormDefinitonRequest,
)


class FormOperations:
    def __init__(self, config: Config):
        self.config = config
        self.endpoints = ServiceEndpoints()
        self.base_url = get_base_url(config=config, service=ServiceType.DOCUMENT)

    def create_form(self, form_data: CreateFormRequest) -> CreateFormResponse:
        """Creates a new form with the specified fields and metadata.

        Args:
            form_data (CreateFormRequest): The request body containing the following parameters:
                - name (str): The name of the form.
                - category (str): The category for the form.
                - description (Optional[str]): The description of the form. Defaults to an empty string.
                - is_shared (Optional[bool]): A flag indicating whether the form is shared. Defaults to False.
                - is_searchable (Optional[bool]): A flag indicating whether the form is searchable. Defaults to False.
                - fields (Optional[List[FormField]]): A list of fields that define the form structure. Defaults to an empty list.

        Raises:
            FormProcessingException: Raised if authentication fails (status code 401), validation fails (status code 422),
                or any other error occurs during form creation.

        Returns:
            CreateFormResponse: A response object containing the created form's details, including name, category, description, fields, and other metadata.
        """
        url = f"{self.base_url}/{self.endpoints.CREATE_FORM}"
        response = requests.post(
            url=url,
            json=form_data.model_dump(),
            headers={"Authorization": f"Bearer {self.config.auth_token}"},
        )
        if response.status_code == 401:
            raise FormProcessingException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 422:
            raise FormProcessingException(
                status_code=response.status_code,
                message=VALIDATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise FormProcessingException(
                status_code=response.status_code,
                message="Failed to create form",
                response_data=response.json(),
            )
        final_response = response.json()
        final_response["id"] = final_response.pop("_id")
        return CreateFormResponse.model_validate(final_response)

    def filter_form(self, form_data: FilterFormRequest) -> FilterFormResponse:
        """Filters forms based on the provided query and scope.

        Args:
            form_data (FilterFormRequest): The request body containing the following parameters:
                - query (str): The search query used to filter forms.
                - scope (Literal["all_forms", "my_forms"]): The scope for filtering forms (all forms or only the user's forms).
                - is_searchable (Optional[bool]): A flag to filter only searchable forms. Defaults to False.

        Raises:
            FormProcessingException: Raised if authentication fails (status code 401), or if any other error occurs while filtering forms.

        Returns:
            FilterFormResponse: A response object containing the filtered forms based on the query and scope.
        """
        url = f"{self.base_url}/{self.endpoints.FILTER_FORM}"
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
            headers={"Authorization": f"Bearer {self.config.auth_token}"},
        )
        if response.status_code == 401:
            raise FormProcessingException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 404:
            raise FormProcessingException(
                status_code=response.status_code,
                message="Could not find form",
                response_data="Could not find form",
            )
        elif response.status_code != 200:
            raise FormProcessingException(
                status_code=response.status_code,
                message="Failed to filter form data",
                response_data=response.json(),
            )
        response = response.json()
        for item in response:
            if "_id" in item:
                item["id"] = item.pop("_id")
        return FilterFormResponse(forms=response)

    def execute_form_analytics(
        self, form_id: str, form_data: ExecuteFormAnalyticsRequest
    ) -> ExecuteFormAnalyticsResponse:
        """Executes analytics on a specified form using the provided query.

        Args:
            form_id (str): The ID of the form on which analytics are being executed.
            form_data (ExecuteFormAnalyticsRequest): The request body containing the query, pagination details (skip, limit), and other parameters.

        Raises:
            FormProcessingException: Raised if authentication fails (status code 401), validation fails (status code 422),
                or if any other error occurs while executing form analytics.

        Returns:
            ExecuteFormAnalyticsResponse: A response object containing the results of the form analytics, including the summary, total count, and columns.
        """
        url = f"{self.base_url}/{self.endpoints.EXECUTE_FORM_ANALYTICS.format(FORM_ID=form_id)}"
        final_data = {data[0]: data[1] for data in form_data if data[1]}
        response = requests.post(
            url=url,
            json=final_data,
            headers={
                "Authorization": f"Bearer {self.config.auth_token}",
                "Content-Type": "application/json",
            },
        )
        if response.status_code == 401:
            raise FormProcessingException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 422:
            raise FormProcessingException(
                status_code=response.status_code,
                message=VALIDATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise FormProcessingException(
                status_code=response.status_code,
                message="Failed to execute form analytics",
                response_data=response.json(),
            )
        return ExecuteFormAnalyticsResponse.model_validate(response.json())

    def filter_form_instances(
        self, form_data: FilterFormInstanceRequest
    ) -> FilterFormInstanceResponse:
        """Filters form instances based on the provided parameters such as scope, status, category, and query.

        Args:
            form_data (FilterFormInstanceRequest): The request body containing the following parameters:
                - scope (Literal["all_documents", "current_document", "my_documents", "shared_documents"]): The scope for filtering form instances.
                - status (Optional[Literal["NOT_STARTED", "IN_PROGRESS", "DONE", "FAILED"]]): The status of the form instance. Defaults to None.
                - category (Optional[str]): The category of the form instance. Defaults to an empty string.
                - query (Optional[str]): A search query to filter form instances. Defaults to an empty string.
                - form_id (Optional[str]): The ID of the form. Defaults to an empty string.
                - doc_id (Optional[str]): The document ID associated with the form instance. Defaults to an empty string.
                - only_latest (Optional[bool]): A flag to return only the latest form instances. Defaults to False.
                - skip (Optional[int]): The number of records to skip for pagination. Defaults to 0.
                - limit (Optional[int]): The maximum number of records to return. Defaults to 25.
                - all (Optional[bool]): A flag to return all form instances. Defaults to True.

        Raises:
            FormProcessingException: Raised if authentication fails (status code 401), or if any other error occurs while filtering form instances.

        Returns:
            FilterFormInstanceResponse: A response object containing the filtered form instances.
        """
        url = f"{self.base_url}/{self.endpoints.FILTER_FORM_INSTANCES}"
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
            ("all", form_data.all),
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
            headers={"Authorization": f"Bearer {self.config.auth_token}"},
        )
        if response.status_code == 401:
            raise FormProcessingException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 404:
            raise FormProcessingException(
                status_code=response.status_code,
                message="Could not find form",
                response_data="Could not find form",
            )
        elif response.status_code != 200:
            raise FormProcessingException(
                status_code=response.status_code,
                message="Failed to filter form instances",
                response_data=response.json(),
            )
        return FilterFormInstanceResponse.model_validate(response.json())

    def get_form_definition(self, form_id: str) -> GetFormDefinitonResponse:
        """Retrieves the definition of a specific form by its ID.

        Args:
            form_id (str): The ID of the form whose definition is being fetched.

        Raises:
            FormProcessingException: Raised if authentication fails (status code 401), or if the form definition is not found (status code 404).

        Returns:
            GetFormDefinitonResponse: A response object containing the form definition, including name, category, fields, and other metadata.
        """
        url = f"{self.base_url}/{self.endpoints.GET_FORM_DEFINITON.format(FORM_ID=form_id)}"
        response = requests.get(
            url=url,
            headers={"Authorization": f"Bearer {self.config.auth_token}"},
        )
        if response.status_code == 401:
            raise FormProcessingException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 404:
            raise FormProcessingException(
                status_code=response.status_code,
                message="Form definition not found",
                response_data="Form definition not found.",
            )
        elif response.status_code != 200:
            raise FormProcessingException(
                status_code=response.status_code,
                message="Failed to get form definition",
                response_data=response.json(),
            )
        final_response = response.json()
        final_response["id"] = final_response.pop("_id")
        return GetFormDefinitonResponse.model_validate(final_response)

    def update_form_definition(
        self, form_id: str, form_data: UpdateFormDefinitonRequest
    ) -> GetFormDefinitonResponse:
        """Updates the definition of an existing form.

        Args:
            form_id (str): The ID of the form to be updated.
            form_data (UpdateFormDefinitonRequest): The request body containing the updated form details such as name, category, fields, and other metadata.

        Raises:
            FormProcessingException: Raised if authentication fails (status code 401), validation fails (status code 422), or if any other error occurs while updating the form definition.

        Returns:
            GetFormDefinitonResponse: A response object containing the updated form definition.
        """
        url = f"{self.base_url}/{self.endpoints.UPDATE_FORM_DEFINITON.format(FORM_ID=form_id)}"
        response = requests.put(
            url=url,
            json=form_data.model_dump(),
            headers={"Authorization": f"Bearer {self.config.auth_token}"},
        )
        if response.status_code == 401:
            raise FormProcessingException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 422:
            raise FormProcessingException(
                status_code=response.status_code,
                message=VALIDATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise FormProcessingException(
                status_code=response.status_code,
                message="Failed to update form instances",
                response_data=response.json(),
            )
        final_response = response.json()
        final_response["id"] = final_response.pop("_id")
        return GetFormDefinitonResponse.model_validate(final_response)

    def delete_form_definition(self, form_id: str) -> GetFormDefinitonResponse:
        """Deletes a specific form by its ID.

        Args:
            form_id (str): The ID of the form to be deleted.

        Raises:
            FormProcessingException: Raised if authentication fails (status code 401), or if any other error occurs while deleting the form.

        Returns:
            GetFormDefinitonResponse: A response object confirming the deletion of the form.
        """
        url = f"{self.base_url}/{self.endpoints.DELETE_FORM_DEFINITON.format(FORM_ID=form_id)}"
        response = requests.delete(
            url=url,
            headers={"Authorization": f"Bearer {self.config.auth_token}"},
        )
        if response.status_code == 401:
            raise FormProcessingException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise FormProcessingException(
                status_code=response.status_code,
                message="Failed to delete form definition",
                response_data=response.json(),
            )
        final_response = response.json()
        final_response["id"] = final_response.pop("_id")
        return GetFormDefinitonResponse.model_validate(final_response)

    def download_query_result(
        self, form_id: str, download_format: str, form_data: DownloadQueryResultRequest
    ) -> Union[DownloadQueryResultResponse, pd.DataFrame]:
        """Downloads the result of a form query in the specified format.

        Args:
            form_id (str): The ID of the form whose query results are being downloaded.
            download_format (str): The format in which to download the query result (e.g., CSV, JSON).
            form_data (DownloadQueryResultRequest): The request body containing the query for retrieving the form results.

        Raises:
            FormProcessingException: Raised if authentication fails (status code 401), validation fails (status code 422),
                or if any other error occurs while downloading the query result.

        Returns:
            Union[DownloadQueryResultResponse, pd.DataFrame]: The query result as a response object or as a pandas DataFrame if CSV format is requested.
        """
        url = f"{self.base_url}/{self.endpoints.DOWNLOAD_QUERY_RESULT.format(FORM_ID=form_id)}"
        params = [("download_format", download_format)]
        response = requests.post(
            url=url,
            params=params,
            json={"query": form_data.query},
            headers={
                "Authorization": f"Bearer {self.config.auth_token}",
                "Content-Type": "application/json",
            },
        )

        if response.status_code == 401:
            raise FormProcessingException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 422:
            raise FormProcessingException(
                status_code=response.status_code,
                message=VALIDATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise FormProcessingException(
                status_code=response.status_code,
                message="Failed to download form definition",
                response_data=response.json(),
            )
        if download_format != "CSV":
            return DownloadQueryResultResponse.model_validate(response.json())
        data = StringIO(response.text)
        return pd.read_csv(data)
