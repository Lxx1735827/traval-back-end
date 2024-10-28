from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `site` MODIFY COLUMN `name` VARCHAR(100) NOT NULL  COMMENT '景点名字';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `site` MODIFY COLUMN `name` VARCHAR(50) NOT NULL  COMMENT '景点名字';"""
