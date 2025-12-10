from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import uuid


class NodeType(str, Enum):
    INPUT = "input"
    OUTPUT = "output"
    CONDITION = "condition"
    ACTION = "action"
    COMMENT = "comment"
    SENSOR = "sensor"
    TASK = "task"


class NodeShape(str, Enum):
    ELLIPSE = "ellipse"
    RECTANGLE = "rectangle"


class BorderStyle(str, Enum):
    SINGLE = "single"
    DOUBLE = "double"


class ConnectionType(str, Enum):
    DEFAULT = "default"
    FLOW = "flow"
    CONDITION = "condition"
    FEEDBACK = "feedback"


@dataclass
class NodeAppearance:
    shape: NodeShape = NodeShape.RECTANGLE
    border: BorderStyle = BorderStyle.SINGLE
    fill_color: str = "#f5f5f5"
    border_color: str = "#2d2d2d"
    text_color: str = "#111111"

    @staticmethod
    def from_dict(data: Optional[Dict[str, str]]) -> "NodeAppearance":
        if not data:
            return NodeAppearance()
        return NodeAppearance(
            shape=NodeShape(data.get("shape", NodeShape.RECTANGLE.value)),
            border=BorderStyle(data.get("border", BorderStyle.SINGLE.value)),
            fill_color=data.get("fill_color", "#f5f5f5"),
            border_color=data.get("border_color", "#2d2d2d"),
            text_color=data.get("text_color", "#111111"),
        )

    def to_dict(self) -> Dict[str, str]:
        return {
            "shape": self.shape.value,
            "border": self.border.value,
            "fill_color": self.fill_color,
            "border_color": self.border_color,
            "text_color": self.text_color,
        }


@dataclass
class Node:
    id: str
    type: NodeType
    label: str
    x: float
    y: float
    appearance: NodeAppearance = field(default_factory=NodeAppearance)
    properties: Dict[str, str] = field(default_factory=dict)  # ex: "equation", "tag", etc.

    @staticmethod
    def create(
        node_type: NodeType,
        label: str,
        x: float,
        y: float,
        *,
        appearance: Optional[NodeAppearance] = None,
        properties: Optional[Dict[str, str]] = None,
    ) -> "Node":
        return Node(
            id=str(uuid.uuid4()),
            type=node_type,
            label=label,
            x=x,
            y=y,
            appearance=appearance or NodeAppearance(),
            properties=properties or {},
        )


@dataclass
class Connection:
    id: str
    source_id: str
    target_id: str
    label: str = ""  # ex: "TRUE path", "FALSE path"
    type: ConnectionType = ConnectionType.DEFAULT

    @staticmethod
    def create(
        source_id: str,
        target_id: str,
        label: str = "",
        connection_type: ConnectionType = ConnectionType.DEFAULT,
    ) -> "Connection":
        return Connection(
            id=str(uuid.uuid4()),
            source_id=source_id,
            target_id=target_id,
            label=label,
            type=connection_type,
        )


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


@dataclass
class DiagramComponent:
    """Definition d'un composant visuel disponible dans la palette."""

    id: str
    display_name: str
    node_type: NodeType
    appearance: NodeAppearance
    default_properties: Dict[str, str] = field(default_factory=dict)
