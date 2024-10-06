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