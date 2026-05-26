class DomainException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class UserAlreadyExistsException(DomainException):
    pass

class InvalidCredentialsException(DomainException):
    pass

class InvalidDatasetFormatException(DomainException):
    pass

class DatasetNotFoundException(DomainException):
    def __init__(self, filename: str):
        self.filename = filename
        super().__init__(f"Dataset with name '{filename}' was not found.")