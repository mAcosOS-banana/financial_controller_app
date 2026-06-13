from DTOs.buisness.transactions.transactions_schema import (
    CreateTransactionSchema,
    UpdateTransactionSchema
)

from models.buisness_models.planning_models.planning import Planning

from utils.context_manager import db_transaction
from models.buisness_models.transactions_models.transactions import Transaction
from models.buisness_models.transactions_models.categories import Category

from server.extensions import db

class TransactionsService:
    
    @staticmethod
    def create(planning_id : str, data : CreateTransactionSchema, creator_id : str):


        planning = Planning.query.get(planning_id)
        if not planning or planning.is_deleted:
            raise ValueError("Planning não entrado.")
        if not creator_id in [m.id for m in planning.members]:
            raise ValueError("Usuário não pertence ou não tem acesso ao planning")
        
        category = Category.query.get(data.category_id)
        if not category:
            raise ValueError("Categoria não existe")
        if category.planning_id is not None and category.planning_id != planning_id:
            raise ValueError("Categoria inválida para este planning")

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
                created_by = creator_id
            )
            db.session.add(transaction)
        return transaction
   
    @staticmethod
    def update(transaction_id: str, data : UpdateTransactionSchema, updater_id : str):
        transaction = Transaction.query.get(transaction_id)
        if not transaction or transaction.is_deleted:
            raise ValueError("Transação não econtrada")
        
        if updater_id not in [m.id for m in transaction.planning.members]:
            raise ValueError("Você não tem acesso a essa transação")
        
        update_data = data.model_dump(exclude_unset=True)
        if "category_id" in update_data:
            category = Category.query.get(data.category_id)
            if not category:
                raise ValueError("Categoria não encontrada.")
            if category.planning_id is not None and category.planning_id != transaction.planning_id:
                raise ValueError("Categoria inválida para este planning")

        with db_transaction():
            for field, value in update_data.items():
                setattr(transaction, field, value)
            transaction.updated_by = updater_id
            
        
        return transaction
        
    @staticmethod   
    def delete(transaction_id : str, updater_id : str):
        transaction = Transaction.query.get(transaction_id)
        
        if not transaction:
            raise ValueError("Transação não encontrada")
        if updater_id not in [m.id for m in transaction.planning.members]:
            raise ValueError("Você não tem acesso a essa transação")
        if transaction.is_deleted:
            raise ValueError("Transação já foi excluída") 
        
        with db_transaction():
            transaction.updated_by = updater_id
            transaction.is_deleted = True
            transaction.deleted_at = db.func.now()
        
        return transaction      

