"""
Linux 监控系统后端
基于 FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from contextlib import asynccontextmanager

from api import metrics_router, websocket_router, metrics_publisher
from db import init_db
from monitor import collector


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print("初始化数据库...")
    init_db()
    
    # 启动指标发布任务
    print("启动指标发布任务...")
    task = asyncio.create_task(metrics_publisher())
    
    yield
    
    # 关闭时
    task.cancel()
    print("应用已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="Linux Monitor API",
    description="Linux 运行监控系统后端 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
app.include_router(metrics_router)
app.include_router(websocket_router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "Linux Monitor API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
