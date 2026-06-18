from validators.buisness.transactions.transactions_schema import (
    CreateTransactionSchema,
    UpdateTransactionSchema
)

from sqlalchemy.orm import joinedload

from models.buisness_models.planning_models.planning import Planning

from utils.context_manager import db_transaction
from utils.exceptions import ConflictError, NotFoundError, ForbiddenError, UnauthorizedError

from services.business.planning.planning_service import PlanningService

from models.buisness_models.transactions_models.transactions import Transaction
from models.buisness_models.transactions_models.categories import Category

from server.extensions import db

class TransactionsService:
    
    
    @staticmethod
    def _get_authorized_transaction(transaction_id: str, user_id: str) -> Transaction:
        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            raise NotFoundError("Transação não encontrada")
        if transaction.is_deleted:
            raise ConflictError("Transação já foi excluída.")
        if user_id not in [m.id for m in transaction.planning.members]:
            raise ForbiddenError("Você não tem acesso a essa transação")
        return transaction


    @staticmethod
    def create(planning_id : str, data : CreateTransactionSchema, creator_id : str):
        PlanningService.get_authorized(planning_id=planning_id, user_id=creator_id)
    
        category = Category.query.get(data.category_id)
        if not category:
            raise NotFoundError("Categoria não encontrada")
        if category.planning_id is not None and category.planning_id != planning_id:
            raise UnauthorizedError("Categoria inválida para este planning")
        print(creator_id)
        with db_transaction():
            transaction = Transaction(
                title = data.title,
                description = data.description,
                category_id= data.category_id,
                type = data.type,
                value = data.value,

                due_date = data.due_date,
                paid_at = data.paid_at, 
                planning_id = planning_id,
                created_by = creator_id,
                updated_by = creator_id
            )
            db.session.add(transaction)
        return transaction
   
   
    @staticmethod
    def update(transaction_id: str, data : UpdateTransactionSchema, updater_id : str):
        transaction = TransactionsService._get_authorized_transaction(transaction_id= transaction_id, user_id=updater_id)
        
        update_data = data.model_dump(exclude_unset=True)

        if "category_id" in update_data:
            category = Category.query.get(data.category_id)
            if not category:
                raise NotFoundError("Categoria não encontrada.")
            if category.planning_id is not None and category.planning_id != transaction.planning_id:
                raise UnauthorizedError("Categoria inválida para este planning")

        with db_transaction():
            for field, value in update_data.items():
                setattr(transaction, field, value)
            transaction.updated_by = updater_id
            
        
        return transaction


    @staticmethod   
    def delete(transaction_id : str, updater_id : str):
        transaction = TransactionsService._get_authorized_transaction(transaction_id= transaction_id, user_id=updater_id)
        
        if not transaction:
            raise NotFoundError("Transação não encontrada")
        if updater_id not in [m.id for m in transaction.planning.members]:
            raise ForbiddenError("Você não tem acesso a essa transação")
        if transaction.is_deleted:
            raise ConflictError("Transação já foi excluída") 
        
        with db_transaction():
            transaction.updated_by = updater_id
            transaction.is_deleted = True
            transaction.deleted_at = db.func.now()
        
        return transaction      
    

    @staticmethod
    def get(user_id : str, transaction_id : str):
        transaction = TransactionsService._get_authorized_transaction(
            transaction_id=transaction_id,
            user_id=user_id
        )

        return transaction
    

    @staticmethod
    def list_by_planning(planning_id: str, user_id: str, page=1, per_page=20):
        PlanningService.get_authorized(planning_id=planning_id, user_id=user_id)


        pagination = (Transaction.query
            .filter_by(planning_id=planning_id, is_deleted=False)
            .options(joinedload(Transaction.creator), joinedload(Transaction.updater))
            .order_by(Transaction.due_date.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )   


        return pagination
        

