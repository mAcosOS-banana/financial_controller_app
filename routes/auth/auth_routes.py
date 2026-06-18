from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token
)
from services.auth.auth_service import AuthenticationService

from validators.auth.register.register_schemas import RegisterSchema
from validators.auth.register.register_reponses_schemas import RegisterSuccessResponseSchema , RegisterFailResponseSchema

from validators.auth.login.login_schemas import LoginSchema
from validators.auth.login.login_responses_schemas import LoginSuccessResponseSchema, LoginFailResponseSchema
from validators.auth.getter.get_me_response_schema import ResponseUserSchema

from pydantic import ValidationError

from utils.error import AppError
from utils.exceptions import AppException

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = RegisterSchema.model_validate(request.get_json())
    user , token, refresh = AuthenticationService.register(data)
    response_validate_model = RegisterSuccessResponseSchema.model_validate({
        "message" : "Usuário criado com sucesso!",
        "data": {
            "user_id" : user.id,
            "access_token" : token
        }
    })

    return jsonify(response_validate_model.model_dump()) , 201
    

@auth_bp.route("/login", methods=["POST"])
def login():
    data = LoginSchema.model_validate(request.get_json())
    access_token, refresh_token = AuthenticationService.login(data)

    response_validated = LoginSuccessResponseSchema.model_validate({
        "message" : "Login bem-sucedido",
        "data":{
            "access_token": access_token,
            "refresh_token" : refresh_token
        }
    })
    
    return jsonify(response_validated.model_dump()), 200
    
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    new_token = create_access_token(identity=user_id)
    return jsonify({"access_token" : new_token}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = AuthenticationService.me(user_id)
    validated_response = ResponseUserSchema.model_validate({
            "user_id" : user.id ,
            "name" : user.name,
            "email" : user.email
        })
        
    return jsonify(validated_response.model_dump()), 200

