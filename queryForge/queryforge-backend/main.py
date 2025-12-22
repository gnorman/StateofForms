
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.crypto_routes import router as crypto_router
from routes.stock_routes import router as stock_router
from db import database # Import the database instance
from cache import init_redis, close_redis
from models import metadata
import os
import logging


app = FastAPI()

# CORS middleware setup
origins = os.getenv("CORS_ORIGINS")
if origins:
    origins = origins.split(",")
else:
    origins = [
        "http://localhost:3000",
        "http://localhost:8001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8001",
    ]  # Allow all origins for development; restrict in production

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Or restrict to frontend domain 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to the database on startup and disconnect on shutdown
logger = logging.getLogger("__name__")

@app.on_event("startup")
async def startup():
    await database.connect()
    await init_redis()
    # Create tables if they don't exist
    from sqlalchemy import create_engine
    engine = create_engine(os.getenv("DATABASE_URL", "postgresql://queryforge:secretpassword@postgres:5432/queryforge_db"))
    metadata.create_all(engine)
    logger.info("Database and Redis connected successfully.")

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    await close_redis()
    logger.info("Database and Redis disconnected successfully.")
    
@app.get("/ping-db")
async def ping_db():
    query = "SELECT 1"
    result = await database.fetch_one(query=query)
    return {"db_response": result[0] if result else "No response"}

@app.get("/api/queries/")
async def get_all_queries():
    """Get all crypto and stock queries from the database"""
    from models import crypto_queries, stock_queries
    
    try:
        # Fetch all crypto queries
        crypto_query_stmt = crypto_queries.select()
        crypto_data = await database.fetch_all(crypto_query_stmt)
        
        # Fetch all stock queries
        stock_query_stmt = stock_queries.select()
        stock_data = await database.fetch_all(stock_query_stmt)
        
        # Format response
        return {
            "crypto_queries": [dict(row) for row in crypto_data],
            "stock_queries": [dict(row) for row in stock_data],
            "total_queries": len(crypto_data) + len(stock_data),
            "crypto_count": len(crypto_data),
            "stock_count": len(stock_data)
        }
    except Exception as e:
        logger.error(f"Error fetching queries: {str(e)}")
        return {
            "error": str(e),
            "crypto_queries": [],
            "stock_queries": [],
            "total_queries": 0
        }

# Include routers
app.include_router(crypto_router, prefix="/api/crypto", tags=["crypto"])
app.include_router(stock_router, prefix="/api/stock", tags=["stock"])