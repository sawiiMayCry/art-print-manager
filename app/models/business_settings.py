from pydantic import BaseModel


class BusinessSettings(BaseModel):
    business_name: str
    currency: str
    certificate_prefix: str
