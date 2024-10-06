from fastapi import FastAPI
from setting import *
import uvicorn
from api.user import user
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

app = FastAPI()
app.include_router(user, prefix="/user", tags=["user"])

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的源，使用 ["*"] 允许所有源，也可以指定特定域名
    allow_credentials=True,  # 是否允许发送cookie
    allow_methods=["*"],  # 允许的HTTP方法，比如 GET, POST, PUT, DELETE等，使用["*"]允许所有方法
    allow_headers=["*"],  # 允许的HTTP请求头，使用["*"]允许所有的头部
)

# 注册 Tortoise ORM
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,  # 自动生成表
    add_exception_handlers=True,  # 添加异常处理
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)