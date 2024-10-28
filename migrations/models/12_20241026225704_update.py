from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `review` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `entity_id` INT NOT NULL  COMMENT '景点或餐厅ID',
    `entity_type` VARCHAR(50) NOT NULL  COMMENT '类型',
    `user_id` INT NOT NULL  COMMENT '用户ID',
    `content` LONGTEXT   COMMENT '评论内容',
    `created_at` DATETIME(6) NOT NULL  COMMENT '记录时间'
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `review`;"""
