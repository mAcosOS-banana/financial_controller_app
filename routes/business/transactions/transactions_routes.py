from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from validators.buisness.transactions.transactions_reponses_schemas import (
    ResponseCreateTransaction,
    ResponseUpdateTransaction,
    ResponseTransactionListSchema,
    ResponseDeleteTrasactionSchema
)

from validators.buisness.transactions.transactions_schema import (
    CreateTransactionSchema,
    UpdateTransactionSchema
)

from pydantic import ValidationError

from services.business.transactions.transactions_service import TransactionsService

from utils.error import AppError
from utils.exceptions import AppException


transactions_bp = Blueprint("transactions", __name__, url_prefix="/plannings")

@transactions_bp.route("/<string:planning_id>/transactions", methods=["POST"])
@jwt_required()
def create(planning_id : str):
    creator_id = get_jwt_identity()
    data = CreateTransactionSchema.model_validate(request.get_json())
    transaction = TransactionsService.create(planning_id=planning_id, data=data, creator_id=creator_id)
    response_model_validated = ResponseCreateTransaction.model_validate({
        "message": "Transação criada com sucesso.",
        "data" : transaction
    })    


    return jsonify(response_model_validated.model_dump()), 201


@transactions_bp.route("/transactions/<string:transaction_id>", methods=["PATCH"])
@jwt_required()
def update(transaction_id : str):
    updater_id = get_jwt_identity()
    data = UpdateTransactionSchema.model_validate(request.get_json())
    transaction = TransactionsService.update(transaction_id=transaction_id, updater_id=updater_id, data=data)

    response_model_validated = ResponseUpdateTransaction.model_validate({
        "message": "Transação atualizada com sucesso.",
        "data" : transaction
    })

    return jsonify(response_model_validated.model_dump()), 200



@transactions_bp.route("/transactions/<string:transaction_id>", methods=["DELETE"])
@jwt_required()
def delete(transaction_id : str):
    updater_id = get_jwt_identity()
    transaction = TransactionsService.delete(transaction_id=transaction_id, updater_id=updater_id)

    response_model_validated = ResponseDeleteTrasactionSchema.model_validate({
        "message" : "Transação foi excluida com sucesso.",
        "data" : transaction
    })

    return jsonify(response_model_validated.model_dump()), 200