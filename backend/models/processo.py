from dataclasses import dataclass
from typing import Optional


@dataclass
class Processo:
    pid: str
    arrival: int
    burst: int
    deadline: Optional[int] = None
    priority: int = 1
    num_pages: int = 0
