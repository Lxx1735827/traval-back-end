TORTOISE_ORM = {
    "connections": {
        # 使用 aiomysql 连接 MySQL
        "default": "mysql://root:2022141461051@localhost:3306/travel"
    },
    "apps": {
        "models": {
            "models": ["src.model", "aerich.models"],  # aerich 是用于迁移的模型
            "default_connection": "default",
        },
    },
}

# 替换以下内容
TOKEN = "W3CTo3RZ4BGv1D2RpwVwpNTmkVRLBoql"  # 您的 Bearer 令牌
USERID = "lWdLGdyOUqWl"  # 您的用户 ID

# 构造请求的 URL
URL = 'https://yuanqi.tencent.com/openapi/v1/agent/chat/completions'

# 构造请求头
HEADERS = {
    'X-Source': 'openapi',
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {TOKEN}',
}
