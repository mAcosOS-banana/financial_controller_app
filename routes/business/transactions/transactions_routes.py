from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from validators.buisness.transactions.transactions_reponses_schemas import (
    ResponseCreateTransaction,
    ResponseUpdateTransaction,
    ResponseTransactionListSchema,
    ResponseDeleteTrasactionSchema,
    ResponseGetTransactionSchema
)

from validators.buisness.transactions.transactions_schema import (
    CreateTransactionSchema,
    UpdateTransactionSchema
)

from pydantic import ValidationError

from services.business.transactions.transactions_service import TransactionsService

from utils.error import AppError
from utils.exceptions import AppException
from utils.schemas.pagination import PaginationMeta

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


@transactions_bp.route("transactions/<string:transaction_id>",methods=["GET"])
@jwt_required()
def get(transaction_id : str):
    user_id = get_jwt_identity()
    transaction = TransactionsService.get(
        user_id=user_id,
        transaction_id= transaction_id
    )

    response_validated_model = ResponseGetTransactionSchema.model_validate({
        "message" : "Transação encontrada.",
        "data": transaction
    })

    return jsonify(response_validated_model.model_dump()), 200

@transactions_bp.route("/<string:planning_id>/transactions", methods=["GET"])
@jwt_required()
def list(planning_id : str):
    user_id = get_jwt_identity()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    search = request.args.get("search", None, type=str)
    pagination = TransactionsService.list_by_planning(
        user_id=user_id,
        planning_id=planning_id,
        page= page,
        per_page=per_page,
        search=search
    )

    response_model_validated = ResponseTransactionListSchema.model_validate({
        "message" : "Transações encontradas:",
        "data": pagination.items,
        "pagination": PaginationMeta.from_pagination(pagination=pagination, per_page=per_page)
    })

    return jsonify(response_model_validated.model_dump()), 200