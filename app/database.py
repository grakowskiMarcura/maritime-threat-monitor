from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os

load_dotenv()
# --- PostgreSQL Connection (for structured data) ---
# It reads the connection URL from the .env file
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This is a base class that our database models will inherit from
Base = declarative_base()


# --- MongoDB Connection (for unstructured data/logs) ---
MONGO_DATABASE_URL = os.getenv("MONGO_URL")

# Create a client to connect to MongoDB
mongo_client =  MongoClient(MONGO_DATABASE_URL, server_api=ServerApi('1'))

# Get a specific database from MongoDB (e.g., "threat_db")
mongo_db = mongo_client.maritime_threat_monitor

# Send a ping to confirm a successful connection
#try:
#    mongo_client.admin.command('ping')
#    print("Pinged your deployment. You successfully connected to MongoDB!")
#except Exception as e:
#    print(e)