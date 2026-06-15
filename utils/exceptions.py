class AppException(Exception):
    status_code = 400
    def __init__(self, message):
        self.message = message
        super().__init__(message)

class NotFoundError(AppException):
    status_code = 404

class ForbiddenError(AppException):
    status_code = 403

class ConflictError(AppException):
    status_code = 409

class UnauthorizedError(AppException):
    status_code = 401
    
class BadRequestError(AppException):
    status_code = 400