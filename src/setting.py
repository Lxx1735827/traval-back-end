TORTOISE_ORM = {
    "connections": {
        # 使用 aiomysql 连接 MySQL
        "default": "mysql://2022141461051:2022141461051@localhost:3306/travel"
    },
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],  # aerich 是用于迁移的模型
            "default_connection": "default",
        },
    },
}