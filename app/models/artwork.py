from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class ArtworkStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"


class EditionType(str, Enum):
    OPEN = "OPEN"
    LIMITED = "LIMITED"


class Artwork(BaseModel):
    id: str
    title: str
    location: str | None = None
    year: int = Field(ge=1800, le=datetime.now().year)
    status: ArtworkStatus
    edition_type: EditionType

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Artwork title cannot be empty.")

        return value
