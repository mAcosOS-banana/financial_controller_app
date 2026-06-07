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
    
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=db.func.now())
    deleted_at = db.Column(db.TIMESTAMP(timezone=True), nullable=True)
    
    members = db.relationship("User", secondary=planning_user, backref="plannings")
    transactions = db.relationship("Transaction", backref= "planning")