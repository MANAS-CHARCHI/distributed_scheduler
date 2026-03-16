from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import scheduler
from database.db import Base, engine
Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="My FastAPI App",
    description="REST API with SQLAlchemy + FastAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scheduler.router, prefix="/api/v1")

@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}