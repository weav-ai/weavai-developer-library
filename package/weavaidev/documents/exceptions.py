class DocumentProcessingException(Exception):
    def __init__(self, status_code, message, response_data=None):
        self.status_code = status_code
        self.message = message
        self.response_data = response_data
        error_details = f"Error {status_code}: {message}"
        if response_data:
            error_details += f" - {response_data}"
        super().__init__(error_details)
