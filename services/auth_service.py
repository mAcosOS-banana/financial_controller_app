from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity

from server.extensions import db
from models.user_model import User

from utils.context_manager import db_trasaction

from DTOs.auth.register.register_schemas import RegisterSchema 
from DTOs.auth.login.login_schemas import LoginSchema 

from pydantic import ValidationError

class AuthenticationService:

    @staticmethod
    def register(data : RegisterSchema):
        if User.query.filter_by(email=data.email).first():
            raise ValueError("Email já cadastrado. Por favor tende novamente ou recupere a senha.")
        
        with db_trasaction():
            user = User(name=data.name, email=data.email)
            user.set_password(data.password)
            db.session.add(user)
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return user, access_token, refresh_token

    @staticmethod
    def login(data : LoginSchema):
        user = User.query.filter_by(email=data.email).first()
        if not user or not user.check_password(data.password):
            raise ValueError("Credenciais Inválidas.")
        
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return access_token, refresh_token
    
    @staticmethod
    def me(user_id):
        user = User.query.get(user_id)
        
        return user

