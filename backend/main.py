from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.api.websockets import router as ws_router
from app.db.database import create_db_and_tables
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Video Detection API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS middleware configured for http://localhost:3000")

# Include routers
app.include_router(router)
app.include_router(ws_router)
logger.info("Routers registered")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up application...")
    create_db_and_tables()
    logger.info("Database tables created (if not exist)")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application...")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server via uvicorn...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
