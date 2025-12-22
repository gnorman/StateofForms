from databases import Database
import os

# Load the DATABASE_URL from .env file
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://queryforge:secretpassword@postgres:5432/queryforge_db")

#Create a Database instance
database = Database(DATABASE_URL)