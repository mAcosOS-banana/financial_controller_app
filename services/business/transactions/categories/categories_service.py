from validators.buisness.transactions.categories.categories_schemas import CreateCategorySchema, UpdateCategorySchema

from server.extensions import db

from utils.context_manager import db_transaction
from utils.exceptions import NotFoundError, ConflictError, UnauthorizedError, BadRequestError
from planning.planning_service import PlanningService

from models.buisness_models.transactions_models.categories import Category

class CategoryService():

    @staticmethod
    def create(creator_id : str, data : CreateCategorySchema, planning_id : str):        
        if planning_id is None:
            raise UnauthorizedError("Não é permitido criar categorias sem atribuir um planning")
        
        planning = PlanningService.get_authorized(planning_id, creator_id)
        exists = Category.query.filter_by(name=data.name, planning_id= planning_id).first()
        if exists:
            raise ConflictError("Categoria já existe nesse planning")
    
        with db_transaction():
            category = Category(
                name = data.name,
                color = data.color,
                planning_id = planning_id,

                created_by = creator_id
            )
            db.session.add(category)
        return category
    
    @staticmethod
    def update(updater_id : str, data : UpdateCategorySchema, planning_id : str, category_id : str):
        if planning_id is None:
            raise UnauthorizedError("Não é permitido atualizar categorias que não estejam em um planning.")
        
        planning = PlanningService.get_authorized(planning_id, updater_id)
        category = Category.query.get(category_id)
        
        if not category:
            raise NotFoundError("Categoria não encontrada.")
        if category.planning_id != planning_id: 
            raise UnauthorizedError("Categoria não pertence a este planning")
        
        update_data = data.model_dump(exclude_unset=True)
        if "name" in update_data:
            exists = (Category.query
                .filter_by(name=update_data["name"], planning_id=planning_id)
                .filter(Category.id != category_id)
                .first())
            
            if exists:
                raise ConflictError(f"Categoria com o nome {data.name} já existe no planning.")
            
        with db_transaction():
            for field, value in update_data.items():
                setattr(category, field, value)
            category.updated_by = updater_id
        return category

    

    @staticmethod
    def delete(planning_id : str, category_id : str, updater_id : str): 
        if planning_id is None:
            raise BadRequestError("Não é permitido deletar uma categoria sem informar o planning.")
        
        planning = PlanningService.get_authorized(planning_id, updater_id)
        category = Category.query.get(category_id)

        if category.planning_id != planning_id:
            raise NotFoundError("Categoria não pertence a este planning")
        if not category:
            raise NotFoundError("Categoria não encontrada")
        if category.is_deleted:
            raise ConflictError("Categoria já foi excluída")
        
        with db_transaction():
            category.is_deleted = True
            category.deleted_at = db.func.now()
            category.updated_by = updater_id
        
        return category

        