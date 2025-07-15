import asyncio
from contextlib import asynccontextmanager # Import this!
from fastapi import FastAPI, Depends, HTTPException, status, Header
import os
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import List

from . import crud, models, schemas
from .database import SessionLocal, engine
from .services import rag_agent
from .services.teams_notifier import send_threat_to_teams



SECRET_KEY = os.getenv("API_SECRET_KEY")

async def verify_secret_key(x_api_key: str = Header(..., description="API Secret Key")):
    """
    Dependency to verify the secret key provided in the X-API-Key header.
    """
    if x_api_key != SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return x_api_key


# This queue will hold new threats to be sent to clients as notifications
notification_queue = asyncio.Queue()

# Global scheduler instance (will be initialized in lifespan)
# We need to declare it here so it's accessible within `lifespan` and can be started/stopped
scheduler: AsyncIOScheduler = None 

# --- Database Dependency (remains the same) ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Background Task (The Agent Runner - remains the same) ---
async def run_threat_discovery_and_save():
    print("Scheduler triggered: Starting RAG agent to discover threats...")
    db: Session = next(get_db()) # Use next() to get a session outside a request context
    try:
        threat_reports = await rag_agent.find_maritime_threats()
        if not threat_reports:
            print("Agent finished: No new threats found.")
            return

        for report in threat_reports:
            # Here you should add logic to check if the threat is a duplicate
            # For now, we'll create all of them.
            new_threat_orm = crud.create_threat(db=db, threat_data=report)
            #print(f"New threat saved to DB: {new_threat_orm.title}")
            
            # Convert the DB object to a Pydantic schema for the notification
            # No from_orm needed if schema is created directly, but if Threat.from_orm
            # handles ORM to Pydantic conversion, keep it.
            # Assuming schemas.Threat.from_orm is correct from your pydantic warning fixes
            new_threat_schema = schemas.Threat.model_validate(new_threat_orm) 
            # Put the new threat into the notification queue
            await notification_queue.put(new_threat_schema)

            # --- ADD THIS LINE ---
            # Send the notification to the Teams channel            
            await send_threat_to_teams(new_threat_schema)
            # --------------------

    finally:
        db.close()


# --- Lifespan Event Handler ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Logic ---
    print("Application startup initiated.")
    
    # 1. Create database tables (if they don't exist)
    # This happens *once* when the application starts
    print("Creating database tables...")
    models.Base.metadata.create_all(bind=engine)
    print("Database tables created/verified.")

    # 2. Initialize and start the scheduler
    # Access the global scheduler variable
    global scheduler 
    scheduler = AsyncIOScheduler()
    #scheduler.add_job(run_threat_discovery_and_save, 'interval', minutes=1)
    scheduler.add_job(run_threat_discovery_and_save,   trigger=CronTrigger(hour=6, minute=0, timezone='UTC'))

    scheduler.start()
    print("Scheduler started. RAG agent will run periodically.")

    print("Pinged your deployment. You successfully connected to MongoDB!") # Your MongoDB message

    print("Application startup complete.")
    yield # Application starts serving requests after this point

    # --- Shutdown Logic (runs when the application is gracefully shutting down) ---
    print("Application shutdown initiated.")
    if scheduler.running:
        scheduler.shutdown()
        print("Scheduler stopped.")
    
    # Add any other cleanup logic here, e.g., closing MongoDB connection
    # if it's managed directly in this file and needs explicit closing.
    # For SQLAlchemy, the engine usually manages connections, but if you had a
    # global MongoDB client, you'd close it here.

    print("Application shutdown complete.")


# Initialize FastAPI application with the lifespan handler
app = FastAPI(title="Maritime Geopolitical Threats API", lifespan=lifespan)

# --- CORS Middleware (remains the same) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, change this to your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints (remains the same) ---

@app.get("/")
def read_root():
    return {"message": "Welcome to the Maritime Threats API"}

@app.get("/api/threats/", response_model=List[schemas.Threat])
def get_all_threats(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Endpoint to get a list of all threats from the database.
    """
    threats = crud.get_threats(db, skip=skip, limit=limit)
    return threats

# --- Real-Time Notification Endpoint (remains the same) ---
from sse_starlette.sse import EventSourceResponse
import json

async def notification_generator():
    """
    Yields new threats from the queue as they arrive.
    This keeps the connection open with the client.
    """
    while True:
        try:
            # Wait for a new threat to appear in the queue
            new_threat = await notification_queue.get()
            # Send the threat data as a JSON string
            yield json.dumps(new_threat.dict())
        except asyncio.CancelledError:
            # The client disconnected
            print("Client disconnected.")
            break

@app.get("/api/notifications")
async def stream_notifications():
    """
    Endpoint for clients to subscribe to real-time threat notifications.
    """
    return EventSourceResponse(notification_generator())


@app.get("/api/discover-threats", dependencies=[Depends(verify_secret_key)])
async def discover_threats():
    """
    Endpoint to trigger the threat discovery process.
    Protected by a secret key.
    """
    await run_threat_discovery_and_save()
    return {"message": "Threat discovery initiated."}