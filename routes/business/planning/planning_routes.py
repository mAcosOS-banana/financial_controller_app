from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from validators.buisness.planning.planning_responses_schemas import (
    ReponseGetPlanningSchema,
    ResponseCreatePlannigSchema,
    ResponseDeletePlanningSchema,
    ResponseListPlanningSchema,
    ResponseFailPlannigSchema,
    ResponseUpdatePlannigSchema
)

from validators.buisness.planning.planning_schema import (
    CreatePlanningSchema,
    UpdatePlanningSchema
)

from pydantic import ValidationError

from services.business.planning.planning_service import PlanningService

from utils.error import AppError
from utils.exceptions import AppException

planning_bp = Blueprint("plannings", __name__, url_prefix="/plannings")


@planning_bp.route("", methods=["POST"])
@jwt_required()
def create():
    creator_id = get_jwt_identity()
    data = CreatePlanningSchema.model_validate(request.get_json())
    planning = PlanningService.create(data=data, creator_id=creator_id)

    response_model_validated = ResponseCreatePlannigSchema.model_validate({
        "message": "Planning foi criado com sucesso.",
        "data": planning
    })
    return jsonify(response_model_validated.model_dump()), 201

@planning_bp.route("/<string:planning_id>", methods=["PATCH"])
@jwt_required()
def update(planning_id : str):
    updater_id = get_jwt_identity()
    data = UpdatePlanningSchema.model_validate(request.get_json())
    planning = PlanningService.update(planning_id=planning_id, updater_id=updater_id, data=data)
    
    response_model_validated= ResponseUpdatePlannigSchema.model_validate({
        "message": "Planning atualizado com sucesso.",
        "data": planning
    })

    return jsonify(response_model_validated.model_dump()), 200

    
@planning_bp.route("/<string:planning_id>", methods=["DELETE"])
@jwt_required()
def delete(planning_id):
    updater_id = get_jwt_identity()
    planning = PlanningService.delete(planning_id=planning_id, updater_id=updater_id)

    response_model_validated= ResponseDeletePlanningSchema.model_validate({
        "message" : "Planning deletado com sucesso.",
        "data": planning
    })

    return jsonify(response_model_validated.model_dump()), 200
