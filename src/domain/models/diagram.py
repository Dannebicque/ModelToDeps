from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List
import uuid


class NodeType(str, Enum):
    INPUT = "input"
    OUTPUT = "output"
    CONDITION = "condition"
    ACTION = "action"
    COMMENT = "comment"


@dataclass
class Node:
    id: str
    type: NodeType
    label: str
    x: float
    y: float
    properties: Dict[str, str] = field(default_factory=dict)  # ex: "equation", "tag", etc.

    @staticmethod
    def create(node_type: NodeType, label: str, x: float, y: float) -> "Node":
        return Node(id=str(uuid.uuid4()), type=node_type, label=label, x=x, y=y)


@dataclass
class Connection:
    id: str
    source_id: str
    target_id: str
    label: str = ""  # ex: "TRUE path", "FALSE path"

    @staticmethod
    def create(source_id: str, target_id: str, label: str = "") -> "Connection":
        return Connection(id=str(uuid.uuid4()), source_id=source_id, target_id=target_id)


class DiagramType(str, Enum):
    ARCHITECTURE = "architecture"
    IO_MAPPING = "io_mapping"
    LOGIC = "logic"
    SAFETY = "safety"
    SEQUENCE = "sequence"
    OTHER = "other"


@dataclass
class Diagram:
    id: str
    name: str
    diagram_type: DiagramType
    nodes: List[Node] = field(default_factory=list)
    connections: List[Connection] = field(default_factory=list)
