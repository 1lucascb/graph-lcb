from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, TypeAlias


# ============================================================
# Enums
# ============================================================

class RecordType(str, Enum):
    ENTITY = "ENTITY"
    RELATIONSHIP = "RELATIONSHIP"


class EntityKind(str, Enum):
    FILE = "FILE"
    MODULE = "MODULE"
    PACKAGE = "PACKAGE"

    CLASS = "CLASS"
    INTERFACE = "INTERFACE"
    ENUM = "ENUM"
    STRUCT = "STRUCT"
    TYPE_ALIAS = "TYPE_ALIAS"

    FUNCTION = "FUNCTION"
    METHOD = "METHOD"
    VARIABLE = "VARIABLE"
    CONSTANT = "CONSTANT"
    PROPERTY = "PROPERTY"
    FIELD = "FIELD"

    DEPENDENCY = "DEPENDENCY"
    BUILD_TARGET = "BUILD_TARGET"


class RelationshipKind(str, Enum):
    DECLARES = "DECLARES"
    CONTAINS = "CONTAINS"

    CALLS = "CALLS"
    IMPORTS = "IMPORTS"

    INHERITS = "INHERITS"
    IMPLEMENTS = "IMPLEMENTS"

    DECORATED_BY = "DECORATED_BY"
    TESTS = "TESTS"
    DEPENDS_ON = "DEPENDS_ON"


# ============================================================
# Shared contracts
# ============================================================

@dataclass(frozen=True, slots=True)
class SourceLocation:
    """
    Source positions:
    - Lines are one-based.
    - Columns are zero-based UTF-8 byte offsets.
    - End positions are exclusive.
    """

    start_line: int
    start_column: int
    end_line: int
    end_column: int

    def __post_init__(self) -> None:
        if self.start_line < 1 or self.end_line < 1:
            raise ValueError("Line numbers must be one-based")

        if self.start_column < 0 or self.end_column < 0:
            raise ValueError("Columns cannot be negative")

        if (self.end_line, self.end_column) < (
            self.start_line,
            self.start_column,
        ):
            raise ValueError("End position cannot precede start position")



@dataclass(frozen=True, slots=True)
class Entity:
    id: str
    kind: str
    name: str
    file: str

    location: SourceLocation | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    record_type: RecordType = field(
        default=RecordType.ENTITY,
        init=False,
    )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation of this extraction record."""
        return _json_compatible(asdict(self))


@dataclass(frozen=True, slots=True)
class Relationship:
    source: str
    target: str | None
    kind: str
    file: str

    location: SourceLocation | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    record_type: RecordType = field(
        default=RecordType.RELATIONSHIP,
        init=False,
    )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation of this extraction record."""
        return _json_compatible(asdict(self))


ExtractionRecord: TypeAlias = Entity | Relationship


def _json_compatible(value: Any) -> Any:
    """Convert nested enums and dataclasses to standard JSON values."""
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: _json_compatible(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_compatible(item) for item in value]
    if isinstance(value, tuple):
        return [_json_compatible(item) for item in value]
    return value
