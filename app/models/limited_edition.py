from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class EditionCopyStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    SOLD = "SOLD"
    RETIRED = "RETIRED"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            normalized = value.strip().upper()

            for status in cls:
                if status.value == normalized:
                    return status

        return None


class LimitedEditionInput(BaseModel):
    artwork_id: str
    edition_size: int = Field(gt=0)


class LimitedEdition(LimitedEditionInput):
    id: str = Field(default_factory=lambda: str(uuid4()))


class EditionCopy(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    limited_edition_id: str
    edition_number: int = Field(gt=0)
    status: EditionCopyStatus = EditionCopyStatus.AVAILABLE


class EditionCopyStatusUpdate(BaseModel):
    status: EditionCopyStatus


class EditionSummary(BaseModel):
    id: str
    artwork_id: str
    edition_size: int
    available: int
    reserved: int
    sold: int
    retired: int
