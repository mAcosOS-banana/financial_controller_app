from server.extensions import db
import uuid
from sqlalchemy import TIMESTAMP, UniqueConstraint

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    name = db.Column(db.String(50),nullable=False)
    color = db.Column(db.String(7),nullable=False)

    planning_id = db.Column(db.String(32), db.ForeignKey("plannings.id"), nullable=True)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    
    created_by = db.Column(db.String(32), db.ForeignKey("users.id"), nullable=False)
    updated_by = db.Column(db.String(100), db.ForeignKey("users.id"), nullable=False)

    created_at = db.Column(db.TIMESTAMP(timezone=True), default=db.func.now(), nullable=False)
    updated_at = db.Column(db.TIMESTAMP(timezone=True), default=db.func.now(), onupdate=db.func.now(), nullable=False)
    deleted_at = db.Column(db.TIMESTAMP(timezone=True), nullable=True)

    creator = db.relationship("User", foreign_keys=[created_by])
    upadater = db.relationship("User", foreign_keys=[updated_by])

    transactions = db.relationship("Transaction", backref="category")
    planning = db.relationship("Planning", backref="categories")

    __table_args__ = (
        UniqueConstraint("name", "planning_id", name="uq_category_name_planning"),
    )
