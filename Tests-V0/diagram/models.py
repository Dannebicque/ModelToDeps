# python
from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class NodeData:
    id: int
    node_type: str
    x: float
    y: float
    width: float
    height: float
    label: str
    color: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EdgeData:
    source_id: int
    target_id: int
    color: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
