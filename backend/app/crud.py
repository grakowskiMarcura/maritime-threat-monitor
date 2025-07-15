from sqlalchemy.orm import Session
from . import models, schemas
from .database import mongo_db

# --- PostgreSQL Functions ---

def get_threats(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieves a list of threats from the PostgreSQL database, newest first.
    """
    return db.query(models.Threat).order_by(models.Threat.created_at.desc()).offset(skip).limit(limit).all()

def create_threat(db: Session, threat_data: schemas.ThreatCreate):
    """
    Creates a new threat in the PostgreSQL database and logs the source URLs in MongoDB.
    Returns the newly created threat object.
    """
    # Create the main threat record in PostgreSQL
    db_threat = models.Threat(
        title=threat_data.title,
        region=threat_data.region,
        category=threat_data.category,
        description=threat_data.description,
        potential_impact=threat_data.potential_impact,  # New field for potential impact
        source_urls=threat_data.source_urls,  # Optional URL for more information
        date_mentioned=threat_data.date_mentioned  # Assuming this field exists in the Threat model
    )
    db.add(db_threat)
    db.commit()
    db.refresh(db_threat)

    # --- MongoDB Logging (Example) ---
    # Log the full report, including source URLs, to MongoDB for archival
    log_entry = {
        "postgres_id": db_threat.id,
        "title": threat_data.title,
        "source_urls": threat_data.source_urls,
        "created_at": db_threat.created_at,
        "region": threat_data.region,
        "category": threat_data.category,
        "description": threat_data.description,
        "potential_impact": threat_data.potential_impact,  # New field for potential impact
        "date_mentioned": threat_data.date_mentioned  # Assuming this field exists in the Threat model
    }
    # We use 'await' because Motor is an async library
    mongo_db.threat_logs.insert_one(log_entry)

    return db_threat