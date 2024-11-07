from pydantic import BaseModel
from typing import Literal,Any

class RobotBind(BaseModel):
    code: str
    handler: str
    auth_user_id:str 
    name:str
    use_subscriptin: Literal["N","Y"]
    proprtes: Any
    use_placment: Literal["N","Y"]
    placment_handler: str | None
    return_proprtes: Any

