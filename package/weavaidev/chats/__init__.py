import requests
from weavaidev import Config
from weavaidev.chats.exceptions import ChatServiceException
from weavaidev.chats.models import (
    ChatHistoryResponse,
    ChatLogsResponse,
    ChatRequest,
    ChatResponse,
    GetChatLogsRequest,
)
from weavaidev.config_models import (
    AUTHENTICATION_FAILED_MESSAGE,
    ServiceEndpoints,
    ServiceType,
    get_base_url,
)


class ChatOperations:
    def __init__(self, config: Config):
        self.config = config
        self.endpoints = ServiceEndpoints()
        self.base_url = get_base_url(config=config, service=ServiceType.CHATS)

    def get_chat_logs(
        self,
        skip: int = 0,
        limit: int = 25,
        start_datetime: str = "",
        end_datetime: str = "",
        is_sop_chat: bool = False,
    ) -> ChatLogsResponse:
        """Fetches chat logs based on the provided request.

        This method retrieves chat logs filtered by the provided parameters such as date range,
        pagination settings, and whether the chat is part of a standard operating procedure (SOP).

        Args:
            - skip (int): The number of records to skip for pagination. Defaults to 0.
            - limit (int): The maximum number of records to return. Defaults to 25.
            - start_datetime (Optional[str]): The start date and time to filter chat logs. Defaults to an empty string.
            - end_datetime (Optional[str]): The end date and time to filter chat logs. Defaults to an empty string.
            - is_sop_chat (bool): A flag to filter SOP chats.

        Raises:
            ChatServiceException: Raised if authentication fails (status code 401).
            ChatServiceException: Raised if any other error occurs while fetching chat logs.

        Returns:
            ChatLogsResponse: A response object containing the list of messages and total record count.
        """
        url = f"{self.base_url}/{self.endpoints.CHAT_LOGS}"
        chat_logs_request = GetChatLogsRequest(
            skip=skip,
            limit=limit,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            is_sop_chat=is_sop_chat,
        )

        params = [
            ("skip", chat_logs_request.skip),
            ("limit", chat_logs_request.limit),
            ("start_datetime", chat_logs_request.start_datetime),
            ("end_datetime", chat_logs_request.end_datetime),
            ("is_sop_chat", chat_logs_request.is_sop_chat),
        ]
        filtered_params = [(k, v) for k, v in params if v is not None and v != ""]

        response = requests.get(
            url=url,
            params=filtered_params,
            headers={"Authorization": f"Bearer {self.config.auth_token}"},
        )
        if response.status_code == 401:
            raise ChatServiceException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise ChatServiceException(
                status_code=response.status_code,
                message="Failed to retrieve chat logs",
                response_data=response.json(),
            )
        return ChatLogsResponse(**response.json())

    def get_chat_history(self, chat_id: str) -> ChatHistoryResponse:
        """Fetches the chat history for a specific chat session.

        This method retrieves the entire chat history for the given `chat_id`.

        Args:
            chat_id (str): The unique identifier of the chat session for which the history
                is being retrieved.

        Raises:
            ChatServiceException: Raised if authentication fails (status code 401).
            ChatServiceException: Raised if any other error occurs while fetching the chat history.

        Returns:
            ChatHistoryResponse: A response object containing the list of messages for the chat session.
        """
        url = f"{self.base_url}/{self.endpoints.CHAT_HISTORY}"
        params = [("chat_id", chat_id)]

        response = requests.get(
            url=url,
            params=params,
            headers={"Authorization": f"Bearer {self.config.auth_token}"},
        )
        if response.status_code == 401:
            raise ChatServiceException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 404:
            raise ChatServiceException(
                status_code=response.status_code,
                message="Could not find chat",
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise ChatServiceException(
                status_code=response.status_code,
                message="Failed to retrieve chat logs",
                response_data=response.json(),
            )
        return ChatHistoryResponse(**response.json())

    def chat(
        self, user_input: str, chat_id: str, file_id: str, stream: bool = False
    ) -> ChatResponse:
        """Sends a chat message to the service and returns the response.

        This method allows the user to send a message to the chat service and receive a response
        based on the user input, chat session, and other provided details.

        Args:
            - user_input (str): The user's input text for the chat.
            - file_id (str): The identifier of the file associated with the chat.
            - chat_id (str): The unique identifier of the chat session.
            - stream (bool, optional): A flag indicating whether the response should be streamed. Defaults to False.

        Raises:
            ChatServiceException: Raised if authentication fails (status code 401).
            ChatServiceException: Raised if any other error occurs while sending the chat message.

        Returns:
            ChatResponse: A response object containing the details of the chat message, search results, and tags.
        """
        chat_request = ChatRequest(
            user_input=user_input, chat_id=chat_id, stream=stream, file_id=file_id
        )
        url = f"{self.base_url}/{self.endpoints.CHAT}"
        response = requests.post(
            url=url,
            json=chat_request.model_dump(),
            headers={"Authorization": f"Bearer {self.config.auth_token}"},
        )
        if response.status_code == 401:
            raise ChatServiceException(
                status_code=response.status_code,
                message=AUTHENTICATION_FAILED_MESSAGE,
                response_data=response.json(),
            )
        elif response.status_code == 404:
            raise ChatServiceException(
                status_code=response.status_code,
                message="Could not find chat",
                response_data=response.json(),
            )
        elif response.status_code != 200:
            raise ChatServiceException(
                status_code=response.status_code,
                message="Failed to send chat",
                response_data=response.json(),
            )
        return ChatResponse(**response.json())
