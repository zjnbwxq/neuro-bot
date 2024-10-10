import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import users, characters, auth, farm
from .database import setup_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Neuro Farm API",
    description="API for Neuro Farm game",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# 设置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://neuro-farm.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建数据库表和初始化数据
@app.on_event("startup")
async def startup_event():
    logger.info("Application is starting up...")
    await setup_database()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application is shutting down...")

@app.get("/api/test")
async def test_route():
    return {"message": "This is a test route"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# 包含路由
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(characters.router, prefix="/api/characters", tags=["characters"])
app.include_router(farm.router, prefix="/api/farms", tags=["farms"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
