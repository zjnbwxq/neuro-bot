from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import users, characters, auth
from .database import engine, Base

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

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 包含路由
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(characters.router)
