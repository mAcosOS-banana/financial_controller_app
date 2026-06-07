from server.extensions import db
import uuid
from sqlalchemy import TIMESTAMP


class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.String(32), primary_key=True, default=lambda : uuid.uuid4().hex)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(250), nullable=True)

    category = db.Column(db.String(32), db.ForeignKey("categories.id") ,nullable=False)    
    
    type = db.Column(db.String(10), nullable=False)
    value = db.Column(db.Numeric(20, 2), nullable=False)
    
    due_date= db.Colunm(db.Date, nullable=False)
    paid_at= db.Column(db.Date, nullable=True)
    
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)

    planning_id = db.Column(db.String(32), db.ForeignKey("plannings.id"), nullable=False)
    created_by = db.Column(db.String(32), db.ForeignKey("users.id"), nullable=False)
    updated_by = db.Column(db.String(32), db.ForeignKey("users.id"), nullable=False)

    created_at = db.Column(db.TIMESTAMP(timezone=True), default=db.func.now(), nullable=False)
    updated_at = db.Column(db.TIMESTAMP(timezone=True), default=db.func.now(), onupdate=db.func.now(), nullable=False)
    deleted_at = db.Column(db.TIMESTAMP(timezone=True), nullable=True)

    creator = db.relationship("User", foreign_keys=[created_by])
    updater = db.relationship("User", foreign_keys=[updated_by])
    