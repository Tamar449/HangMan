class ApiError(Exception):
    def __init__(self, num=400, message='An error occurred while contacting the server.'):
        message = f'error {num} \n{message}'
        self.message = message
        super().__init__(message)
