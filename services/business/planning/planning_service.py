from models.buisness_models.planning_models.planning import Planning

from DTOs.buisness.planning.planning_schema import CreatePlanningSchema, UpdatePlanningSchema

class PlanningService:

    @staticmethod
    def create(data : CreatePlanningSchema, creator_id : str):
        

    @staticmethod
    def update(data : UpdatePlanningSchema, updater_id : str):
        pass

    @staticmethod
    def delete(plannig_id : str, updater_id : str):
        pass