from typing import Any, Dict, Optional

import requests
from loguru import logger
from weavaidev import Config
from weavaidev.config_models import (
    AUTHENTICATION_FAILED_MESSAGE,
    ServiceEndpoints,
    ServiceType,
    get_base_url,
)
from weavaidev.workflows.exceptions import WorkflowException
from weavaidev.workflows.models import (
    DocumentWorkflowRunsResponse,
    GetAllWorkflowsResponse,
    RunWorkflowResponse,
    SkipStepsInWorkflowRequest,
    Workflow,
    WorkflowRequest,
    WorkflowStatusResponse,
)


class WorkflowOperations:
    def __init__(self, config: Config):
        self.config = config
        self.endpoints = ServiceEndpoints()
        self.base_url = get_base_url(config=config, service=ServiceType.WORKFLOWS)

    def get_all_workflows(
        self, show_internal_steps: bool = False
    ) -> GetAllWorkflowsResponse:
        """Fetches all workflows from the system.

        This method retrieves a list of workflows based on the provided parameters.
        The workflows can optionally include internal steps if `show_internal_steps`
        is set to True.

        Args:
            show_internal_steps (bool, optional): A flag to indicate whether internal
                steps should be shown in the workflows. Defaults to False.

        Raises:
            WorkflowException: Raised if the authentication fails (status code 401).
            WorkflowException: Raised if any other error occurs while fetching the
                workflows, with an appropriate error message and response data.

        Returns:
            GetAllWorkflowsResponse: A response object containing the list of
            workflows. The workflows are retrieved in JSON format.
        """
        url = f"{self.base_url}/{self.endpoints.GET_ALL_WORKFLOWS}"
        response = requests.get(
            url=url,
            params=[("show_internal_steps", show_internal_steps)],
            headers={"Authorization": f"Bearer {self.config.auth_token._secret_value}"},
        )
        if response.status_code == 401:
            raise WorkflowException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise WorkflowException(
                status_code=response.status_code,
                message="Failed to get workflows",
                response_data=response.json(),
            )
        return GetAllWorkflowsResponse(workflows=response.json())

    def get_single_workflow(
        self, workflow_name: str, show_internal_steps: bool = False
    ) -> Workflow:
        """Fetches a single workflow by its name.

        This method retrieves a specific workflow based on the given `workflow_name`.
        It can optionally include internal steps if `show_internal_steps` is set to True.

        Args:
            workflow_name (str): The name of the workflow to fetch.
            show_internal_steps (bool, optional): A flag to indicate whether internal
                steps should be shown in the workflow. Defaults to False.

        Raises:
            WorkflowException: Raised if authentication fails (status code 401).
            WorkflowException: Raised if any other error occurs while fetching the
                workflow, with an appropriate error message and response data.

        Returns:
            Workflow: A validated `Workflow` object containing details of the requested
            workflow. The workflow is returned in JSON format and validated using the
            `Workflow` model.
        """
        url = f"{self.base_url}{self.endpoints.GET_SINGLE_WORKFLOW.format(WORKFLOW_NAME=workflow_name)}"
        response = requests.get(
            url=url,
            params=[("show_internal_steps", show_internal_steps)],
            headers={"Authorization": f"Bearer {self.config.auth_token._secret_value}"},
        )
        logger.info(f"{response.status_code}")
        if response.status_code == 401:
            raise WorkflowException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 404:
            raise WorkflowException(
                status_code=response.status_code,
                message="Could not find workflow",
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise WorkflowException(
                status_code=response.status_code,
                message=f"Failed to get workflow {workflow_name}",
                response_data=response.json(),
            )

        return Workflow.model_validate(response.json())

    def skip_steps_in_workflow(self, workflow_name: str, *tasks: str) -> Workflow:
        """Skips specified tasks in a given workflow.

        This method allows you to skip certain tasks in a workflow by providing
        the workflow name and the tasks to be skipped.

        Args:
            workflow_name (str): The name of the workflow where tasks need to be skipped.
            *tasks (str): A variable number of task names that should be skipped within
                the specified workflow.

        Raises:
            WorkflowException: Raised if authentication fails (status code 401).
            WorkflowException: Raised if any other error occurs while attempting to skip
                tasks in the workflow, with an appropriate error message and response data.

        Returns:
            Workflow: A validated `Workflow` object representing the updated state of the
            workflow after skipping the specified tasks. The response is returned in JSON format
            and validated using the `Workflow` model.
        """
        request_data = SkipStepsInWorkflowRequest(tasks=list(tasks))
        url = f"{self.base_url}/{self.endpoints.SKIP_TASK_IN_WORKFLOW.format(WORKFLOW_NAME=workflow_name)}"
        response = requests.post(
            url=url,
            json=request_data.tasks,
            headers={"Authorization": f"Bearer {self.config.auth_token._secret_value}"},
        )
        if response.status_code == 401:
            raise WorkflowException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 404:
            raise WorkflowException(
                status_code=response.status_code,
                message="Could not find workflow",
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise WorkflowException(
                status_code=response.status_code,
                message=f"Failed to skip steps in workflow {workflow_name}",
                response_data=response.json(),
            )
        return Workflow.model_validate(response.json())

    def rerun_workflow(
        self, workflow_name: str, doc_id: str, data: Dict[str, Any]
    ) -> RunWorkflowResponse:
        """Re-runs a specific workflow with new data.

        This method re-runs a workflow by its name, using a specific document ID and
        additional data. It allows the workflow to be executed again with modified
        or updated inputs.

        Args:
            workflow_name (str): The name of the workflow to be re-run.
            doc_id (str): The document ID associated with the workflow run.
            data (Dict[str, Any]): A dictionary containing the data required to re-run
                the workflow. This could include parameters or inputs necessary for
                the workflow execution.

        Raises:
            WorkflowException: Raised if authentication fails (status code 401).
            WorkflowException: Raised if any other error occurs while attempting to
                re-run the workflow, with an appropriate error message and response data.

        Returns:
            RunWorkflowResponse: A response object representing the outcome of the
            workflow re-run. The response is returned in JSON format and validated
            using the `RunWorkflowResponse` model.
        """
        request_data = WorkflowRequest(doc_id=doc_id, data=data)
        url = f"{self.base_url}/{self.endpoints.RERUN_WORKFLOW.format(WORKFLOW_NAME=workflow_name)}"
        response = requests.post(
            url=url,
            json=request_data.model_dump(),
            headers={"Authorization": f"Bearer {self.config.auth_token._secret_value}"},
        )
        if response.status_code == 401:
            raise WorkflowException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 404:
            raise WorkflowException(
                status_code=response.status_code,
                message="Could not find workflow",
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise WorkflowException(
                status_code=response.status_code,
                message=f"Failed to re-run workflow {workflow_name}",
                response_data=response.json(),
            )
        return RunWorkflowResponse.model_validate(response.json())

    def run_workflow(
        self, workflow_name: str, doc_id: str, data: Dict[str, Any]
    ) -> RunWorkflowResponse:
        """Executes a specific workflow with the provided data.

        This method triggers the execution of a workflow by its name, using the
        given document ID and associated data. The workflow is run with the
        specified inputs provided in the `data` dictionary.

        Args:
            workflow_name (str): The name of the workflow to be executed.
            doc_id (str): The document ID that is linked to the workflow execution.
            data (Dict[str, Any]): A dictionary containing the data necessary to
                run the workflow, including inputs or parameters required for execution.

        Raises:
            WorkflowException: Raised if authentication fails (status code 401).
            WorkflowException: Raised if any other error occurs during the execution
                of the workflow, with an appropriate error message and response data.

        Returns:
            RunWorkflowResponse: A response object representing the outcome of the
            workflow execution. The response is returned in JSON format and validated
            using the `RunWorkflowResponse` model.
        """
        request_data = WorkflowRequest(doc_id=doc_id, data=data)
        url = f"{self.base_url}/{self.endpoints.RUN_WORKFLOW.format(WORKFLOW_NAME=workflow_name)}"
        response = requests.post(
            url=url,
            json=request_data.model_dump(),
            headers={"Authorization": f"Bearer {self.config.auth_token._secret_value}"},
        )
        if response.status_code == 401:
            raise WorkflowException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 404:
            raise WorkflowException(
                status_code=response.status_code,
                message="Could not find workflow",
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise WorkflowException(
                status_code=response.status_code,
                message=f"Failed to run workflow {workflow_name}",
                response_data=response.json(),
            )
        return RunWorkflowResponse.model_validate(response.json())

    def get_workflow_status(
        self,
        workflow_id: str,
        workflow_run_id: str,
        show_internal_steps: Optional[bool] = False,
    ) -> WorkflowStatusResponse:
        """Fetches the status of a specific workflow run.

        This method retrieves the current status of a workflow execution based on
        the provided workflow ID and workflow run ID. It can optionally show
        internal steps if `show_internal_steps` is set to True.

        Args:
            workflow_id (str): The ID of the workflow to check the status of.
            workflow_run_id (str): The ID of the specific workflow run whose status
                needs to be fetched.
            show_internal_steps (Optional[bool], optional): A flag to indicate
                whether internal steps of the workflow should be shown. Defaults to False.

        Raises:
            WorkflowException: Raised if authentication fails (status code 401).
            WorkflowException: Raised if any other error occurs while fetching the
                workflow status, with an appropriate error message and response data.

        Returns:
            WorkflowStatusResponse: A response object containing the status of the
            workflow execution, including any available details about the workflow's
            progress. The response is returned in JSON format and validated using
            the `WorkflowStatusResponse` model.
        """
        url = f"{self.base_url}/{self.endpoints.WORKFLOW_STATUS.format(WORKFLOW_ID=workflow_id,WORKFLOW_RUN_ID=workflow_run_id)}"
        response = requests.get(
            url=url,
            params=[("show_internal_steps", show_internal_steps)],
            headers={"Authorization": f"Bearer {self.config.auth_token._secret_value}"},
        )
        if response.status_code == 401:
            raise WorkflowException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise WorkflowException(
                status_code=response.status_code,
                message="Failed to get workflows",
                response_data=response.json(),
            )
        return WorkflowStatusResponse.model_validate(response.json())

    def get_workflow_runs_for_document(
        self,
        doc_id: str,
        state: str = "success",
        query: str = "",
        skip: int = 0,
        limit: int = 25,
    ) -> DocumentWorkflowRunsResponse:
        """Fetches workflow runs for a specific document.

        This method retrieves workflow runs related to a given document ID, with
        optional filtering by state, query string, and pagination settings.

        Args:
            doc_id (str): The document ID for which workflow runs are to be fetched.
            state (str, optional): Filter the workflow runs by their state (e.g., "success",
                "failed"). Defaults to "success".
            query (str, optional): A search query to filter the workflow runs. Defaults to "".
            skip (int, optional): The number of records to skip for pagination. Defaults to 0.
            limit (int, optional): The maximum number of records to return. Defaults to 25.

        Raises:
            WorkflowException: Raised if authentication fails (status code 401).
            WorkflowException: Raised if any other error occurs while fetching the workflow
                runs, with an appropriate error message and response data.

        Returns:
            DocumentWorkflowRunsResponse: A response object containing the workflow runs
            for the specified document. The response is returned in JSON format and validated
            using the `DocumentWorkflowRunsResponse` model.
        """
        params = [
            ("doc_id", doc_id),
            ("state", state),
            ("query", query),
            ("skip", skip),
            ("limit", limit),
        ]
        filtered_params = [
            (name, value) for name, value in params if value not in ("", None)
        ]
        url = f"{self.base_url}/{self.endpoints.WORKFLOW_RUNS}"
        response = requests.get(
            url=url,
            params=filtered_params,
            headers={"Authorization": f"Bearer {self.config.auth_token._secret_value}"},
        )
        if response.status_code == 401:
            raise WorkflowException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 404:
            raise WorkflowException(
                status_code=response.status_code,
                message="Could not find document",
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise WorkflowException(
                status_code=response.status_code,
                message=f"Failed to get workflow runs for {doc_id}",
                response_data=response.json(),
            )
        return DocumentWorkflowRunsResponse.model_validate(response.json())
