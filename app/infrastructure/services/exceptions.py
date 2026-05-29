from app.infrastructure.services.domain_exception import DomainException

class UserAlreadyExistsException(DomainException):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User with email '{email}' already exists.")