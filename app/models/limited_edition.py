from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class EditionCopyStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    SOLD = "SOLD"
    RETIRED = "RETIRED"


class LimitedEditionInput(BaseModel):
    artwork_id: str
    edition_size: int = Field(gt=0)


class LimitedEdition(LimitedEditionInput):
    id: str = Field(default_factory=lambda: str(uuid4()))


class EditionCopy(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    limited_edition_id: str
    edition_number: int
    status: EditionCopyStatus = EditionCopyStatus.AVAILABLE