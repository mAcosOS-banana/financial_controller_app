from typing import Any

class AppError:

    def __init__(self, type: str, msg : str, loc : list[Any] = [], input : Any = None):
        self.type = type
        self.msg = msg
        self.loc = loc
        self.input = input


    def to_dict(self):
        return {
            "type":self.type,
            "loc": self.loc,
            "msg": self.msg,
            "input" : self.input,
        }
    
    @staticmethod
    def from_value_error(e: ValueError, loc: list = []):
        return AppError(
            type= "value_error",
            msg= str(e),
            loc=loc
        ).to_dict()
    
    @staticmethod
    def from_pydantic(e):
        return e.errors()