from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from .database import Base

class Threat(Base):
    __tablename__ = "threats"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    region = Column(String)
    category = Column(String)
    description = Column(String)    
    potential_impact = Column(String, nullable=True)  # New field for potential impact
    # Automatically set the creation time on the database side
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Optional URL for more information
    source_urls = Column(JSON)
    date_mentioned = Column(String)  # Date when the threat was mentioned in the sources

