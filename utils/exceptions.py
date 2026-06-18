class AppException(Exception):
    status_code = 400
    message = "Erro na aplicação"      # padrão da base

    def __init__(self, message=None):
        if message is not None:
            self.message = message
        super().__init__(self.message)


class NotFoundError(AppException):
    message = "Não encontrado"
    status_code = 404

class ForbiddenError(AppException):
    message = "Acesso negado"
    status_code = 403

class ConflictError(AppException):
    message = "Conflito interno"
    status_code = 409

class UnauthorizedError(AppException):
    message = "Não autorizado"
    status_code = 401
    
class BadRequestError(AppException):
    message = "Bad request"
    status_code = 400