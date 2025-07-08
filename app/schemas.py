from pydantic import BaseModel
from datetime import datetime
from typing import List

# Base properties for a threat
class ThreatBase(BaseModel):
    title: str
    region: str
    category: str
    description: str
    source_urls: str

# Properties needed to create a new threat
class ThreatCreate(ThreatBase):
    source_urls: List[str] # The agent provides this, we might store it in MongoDB

# Properties to be returned when reading a threat from the API
class Threat(ThreatBase):
    id: int
    created_at: datetime

    # This allows the model to be created from a database object
    class Config:
        from_attributes = True