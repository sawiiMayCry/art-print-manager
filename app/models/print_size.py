from pydantic import BaseModel, Field


class PrintSize(BaseModel):
    id: str
    code: str
    width_mm: int = Field(gt=0)
    height_mm: int = Field(gt=0)