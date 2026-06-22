from utils.schemas.pagination import PaginationMeta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from routes.business.planning.planning_routes import planning_bp
from services.business.categories.categories_service import CategoryService

from validators.buisness.categories.categories_responses_schemas import (
    ResponseCreateCategorySchema,
    ResponseUpdateCategorySchema,
    ResponseListCategorySchema,
    ResponseGetCategorySchema,
    ResponseDeleteCategorySchema
)

from validators.buisness.categories.categories_schemas import (
    CreateCategorySchema,
    UpdateCategorySchema
)

categories_bp = Blueprint("categories", __name__, url_prefix="/plannings")


@categories_bp.route("/<string:planning_id>/categories", methods=["POST"])
@jwt_required()
def create(planning_id : str):
    creator_id = get_jwt_identity()
    data = CreateCategorySchema.model_validate(request.get_json())
    category = CategoryService.create(creator_id=creator_id, data=data, planning_id=planning_id)

    response_model_validated = ResponseCreateCategorySchema.model_validate({
        "message" : "Categoria criada com sucesso.",
        "data" : category
    })

    return jsonify(response_model_validated.model_dump()), 201


@categories_bp.route("/<string:planning_id>/categories/<string:category_id>", methods=["PATCH"])
@jwt_required()
def update(planning_id: str, category_id : str):
    updater_id = get_jwt_identity()
    data = UpdateCategorySchema.model_validate(request.get_json())
    category = CategoryService.update(updater_id=updater_id, data=data, planning_id=planning_id, category_id=category_id)

    response_model_validated = ResponseUpdateCategorySchema.model_validate({
        "message": "Categoria atualizada com sucesso.",
        "data": category
    })

    return jsonify(response_model_validated.model_dump()), 200



@categories_bp.route("/<string:planning_id>/categories/<string:category_id>", methods=["DELETE"])
@jwt_required()
def delete(planning_id: str, category_id : str):
    updater_id = get_jwt_identity()
    category = CategoryService.delete(category_id=category_id, planning_id=planning_id,updater_id=updater_id)

    response_model_validated = ResponseDeleteCategorySchema.model_validate({
        "message" : "Categoria excluída com sucesso.",
        "data" : category
    })

    return  jsonify(response_model_validated.model_dump()), 200



@categories_bp.route("/<string:planning_id>/categories/<string:category_id>", methods=["GET"])
@jwt_required()
def get(planning_id: str, category_id : str):
    user_id = get_jwt_identity()
    category = CategoryService.get(category_id=category_id, planning_id=planning_id, user_id=user_id)

    response_model_validated = ResponseGetCategorySchema.model_validate({
        "message": "Categoria encontrada:",
        "data": category
    })

    return  jsonify(response_model_validated.model_dump()), 200


@categories_bp.route("/<string:planning_id>/categories", methods=["GET"])
@jwt_required()
def list(planning_id : str):
    user_id = get_jwt_identity()
    pagination = CategoryService.list_by_planning( planning_id=planning_id, user_id=user_id)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    search = request.args.get("search", None, type=str)

    response_model_validated = ResponseListCategorySchema.model_validate({
        "message" : "Categorias encontradas:",
        "data" : pagination.item,
        "pagination" : PaginationMeta.from_pagination(pagination, per_page)
    })


    return jsonify(response_model_validated.model_dump()), 200