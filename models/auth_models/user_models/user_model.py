from server.extensions import db
from server.extensions import bcrypt

from sqlalchemy import TIMESTAMP

import uuid


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column (db.String(100), unique=True,nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    is_deleted = db.Column(db.Boolean , default=False, nullable=False)
    deleted_at = db.Column(db.TIMESTAMP(timezone=True), nullable=True)

    # Seta o Hash para que a senha seja enviada para entidade de forma protegida
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    # Pega a password passada pelo user e compara com o hash
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)