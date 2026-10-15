from dataclasses import dataclass,field
from pathlib import Path
@dataclass(frozen=True)
class Command:
 kind:str
 page_id:str
 payload:dict
@dataclass(frozen=True)
class SessionSnapshot:
 source:Path
 data:bytes=field(repr=False)
 commands:tuple[Command,...]=()
 generation:int=0
@dataclass(frozen=True)
class JobRequest:
 id:str
 kind:str
 snapshot:SessionSnapshot|None
 options:dict
 output:Path
@dataclass(frozen=True)
class JobEvent:
 id:str
 generation:int
 state:str
 progress:float=0
 message:str=''
 output:Path|None=None
 data:dict|None=None

