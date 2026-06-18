from models.buisness_models.planning_models.planning import Planning
from models.auth_models.user_models.user_model import User

from utils.exceptions import ConflictError, NotFoundError, ForbiddenError

from validators.buisness.planning.planning_schema import CreatePlanningSchema, UpdatePlanningSchema
from utils.context_manager import db_transaction

from server.extensions import db

class PlanningService:
    @staticmethod
    def get_authorized(planning_id : str, user_id : str):
        planning = Planning.query.get(planning_id)
        if not planning:
            raise NotFoundError("Planning não encontrado.")
        if planning.is_deleted:
              raise ConflictError("Planning já foi excluído")
        if not user_id in [m.id for m in planning.members]:
            raise ForbiddenError("Usuário não pertence ou não tem acesso ao planning")
        return planning

    @staticmethod
    def create(data : CreatePlanningSchema, creator_id : str):
        members = User.query.filter(User.id.in_(data.members)).all()
        if len(members) != len(set(data.members)):
            raise NotFoundError("Um ou mais usuários não foram encontrados")
        
        creator = User.query.get(creator_id)

        if creator not in members:
            members.append(creator)

        with db_transaction():
            planning = Planning(
                name= data.name,
                description= data.description,
                members = members,
                created_by= creator_id,
                updated_by= creator_id
            )
            db.session.add(planning)
        return planning
    

    @staticmethod
    def update(planning_id: str, data : UpdatePlanningSchema, updater_id : str):
        planning = PlanningService.get_authorized(planning_id=planning_id, user_id=updater_id)

        update_data = data.model_dump(exclude_unset=True)
        members_id = update_data.pop("members", None)
    

        with db_transaction():
            for field, value in update_data.items():
                setattr(planning, field, value)

            if members_id is not None:
                if planning.created_by not in members_id:
                    members_id.append(planning.created_by)
                
                planning.members = User.query.filter(
                    User.id.in_(members_id)
                ).all()

            planning.updated_by = updater_id
        return planning        


    @staticmethod
    def delete(planning_id : str, updater_id : str):
        planning = PlanningService.get_authorized(user_id=updater_id, planning_id=planning_id)

 
        with db_transaction():
            planning.is_deleted = True
            planning.deleted_at = db.func.now()
            planning.updated_by = updater_id

        return planning