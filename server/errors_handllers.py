from flask import jsonify 
from pydantic import ValidationError
from utils.exceptions import AppException
from utils.error import AppError 

def _register_error_handlers(app):
    # erro de validação do Pydantic (body malformado) → 400
    @app.errorhandler(ValidationError)
    def handle_validation(e):
        return jsonify({
            "message": "Erro de validação, por favor confira os campos",
            "errors": AppError.from_pydantic(e),
        }), 400

    # qualquer exceção tipada do domínio → o status que ela carrega
    @app.errorhandler(AppException)
    def handle_app_exception(e):
        return jsonify({
            "message": e.message,
            "errors": [AppError.from_value_error(e)],
        }), e.status_code

    # rede final: qualquer erro inesperado → 500
    @app.errorhandler(Exception)
    def handle_unexpected(e):
        app.logger.error(f"Erro inesperado: {e}", exc_info=True)
        return jsonify({
            "message": "Erro interno do servidor",
        }), 500