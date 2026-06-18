from server.extensions import db
import uuid
from sqlalchemy import TIMESTAMP

# Tabela relacionamento entre User e Planning
planning_user = db.Table(
    "planning_users",
    db.Column("user_id", db.String(32), db.ForeignKey("users.id"), primary_key=True),
    db.Column("planning_id", db.String(32), db.ForeignKey("plannings.id"), primary_key=True)
)

# Model de Planning com relationship criando backref para transactions e members passando pela tabela relacionamento planning_user
class Planning(db.Model):
    __tablename__ = "plannings"

    id = db.Column(db.String(32), primary_key = True, default=lambda: uuid.uuid4().hex,nullable=False)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(250), nullable=True)
    is_deleted = db.Column(db.Boolean , default=False, nullable=False)
    
    created_by = db.Column(db.String(32), db.ForeignKey("users.id"), nullable=False)
    updated_by = db.Column(db.String(32), db.ForeignKey("users.id"), nullable=False)
    
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=db.func.now())
    updated_at = db.Column(db.TIMESTAMP(timezone=True), default=db.func.now(), onupdate=db.func.now(), nullable=False)
    deleted_at = db.Column(db.TIMESTAMP(timezone=True), nullable=True)
    
    members = db.relationship(
        "User",
        secondary=planning_user,
        primaryjoin="Planning.id == planning_users.c.planning_id",
        secondaryjoin="User.id == planning_users.c.user_id",
        backref="plannings"
    )
    transactions = db.relationship("Transaction", backref= "planning")

    creator = db.relationship("User", foreign_keys=[created_by])
    updater = db.relationship("User", foreign_keys=[updated_by])
    