from flask import Flask
from flask_login import login_manager, current_user

from server.extensions import db
from server.extensions import bcrypt
from server.extensions import jwt_manager

from dotenv import load_dotenv
import os
from datetime import timedelta


from models.user_model import User

from routes.auth.auth_routes import auth_bp


load_dotenv()
def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt_manager.init_app(app)


    app.register_blueprint(auth_bp)
    return app

if __name__ == "__main__":
    create_app().run(
        debug=True
    )