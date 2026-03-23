from pydantic import BaseModel
from typing import Optional, Dict

class AuthRequest(BaseModel):
    username: str
    password: Optional[str] = None
    mac_address: Optional[str] = None

class AuthResponse(BaseModel):
    control: Dict[str, str] = {}
    reply: Dict[str, str] = {}

class AcctRequest(BaseModel):
    status_type: str
    session_id: str
    username: str
    nas_ip: str
    mac_address: str
    input_octets: Optional[int] = 0
    output_octets: Optional[int] = 0
    session_time: Optional[int] = 0
    
class GenericResponse(BaseModel):
    status: str
    message: str
