from fastapi import FastAPI
from setting import *
import uvicorn
from src.api.user import user
from src.api.site import site
from src.api.ai import ai
from src.api.restaurant import restaurant
from src.api.review import review
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI()
app.include_router(user, prefix="/user", tags=["user"])
app.include_router(site, prefix="/site", tags=["site"])
app.include_router(ai, prefix="/ai", tags=["ai"])
app.include_router(restaurant, prefix="/restaurant", tags=["restaurant"])
app.include_router(review, prefix="/review", tags=["review"])


# 定义一个继承自BaseHTTPMiddleware的自定义中间件类
class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        return response

# 使用装饰器定义一个中间件函数
@app.middleware("http")
async def custom_middleware(request, call_next):
    response = await call_next(request)
    return response


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
# 将 static 目录中的文件作为静态文件提供
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(CustomMiddleware)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)