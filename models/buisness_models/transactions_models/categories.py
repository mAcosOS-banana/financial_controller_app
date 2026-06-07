from server.extensions import db
import uuid
from sqlalchemy import TIMESTAMP
class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    name = db.Column(db.String(50),nullable=False)
    color = db.Column(db.String(7),nullable=False)

    created_by = db.Column(db.String(32), db.ForeignKey("users.id"), nullable=False)
    updated_by = db.Column(db.String(100), db.ForeignKey("users.id"), nullable=False)

    created_at = db.Column(db.TIMESTAMP(timezone=True), default=db.func.now(), nullable=False)
    updated_at = db.Column(db.TIMESTAMP(timezone=True), default=db.func.now(), onupdate=db.func.now(), nullable=False)

    creator = db.relationship("User", foreign_keys=[created_by])
    upadater = db.relationship("User", foreign_keys=[updated_by])

    transaction = db.relationship("Transaction", backref="category")