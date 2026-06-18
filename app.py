from flask import Flask
from server.errors_handllers import _register_error_handlers
from server.extensions import db
from server.extensions import bcrypt
from server.extensions import jwt_manager
from server.extensions import migrate

from dotenv import load_dotenv
import os
from datetime import timedelta


from models.auth_models.user_models.user_model import User
from models.buisness_models.transactions_models.transactions import Transaction
from models.buisness_models.transactions_models.categories  import Category
from models.buisness_models.planning_models.planning import Planning

from routes.auth.auth_routes import auth_bp
from routes.business.planning.planning_routes import planning_bp
from routes.business.transactions.transactions_routes import transactions_bp

load_dotenv()
def create_app(config_overrides=None):
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

    if config_overrides:                   
        app.config.update(config_overrides)


    db.init_app(app)
    bcrypt.init_app(app)
    jwt_manager.init_app(app)
    migrate.init_app(app, db)

    _register_error_handlers(app)
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(planning_bp)
    app.register_blueprint(transactions_bp)    
    return app


if __name__ == "__main__":
    create_app().run(
        debug=True
    )