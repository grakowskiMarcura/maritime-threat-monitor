from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

# Base properties for a threat
class ThreatBase(BaseModel):
    title: str
    region: str
    category: str
    description: str
    potential_impact: str = Field(default=None, description="The potential impact of the threat on the maritime industry.")
    source_urls: list[str] = Field(default_factory=list) # Ensure it's a list of strings
    date_mentioned: str

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