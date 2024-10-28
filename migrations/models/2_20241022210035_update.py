from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `site` MODIFY COLUMN `description` VARCHAR(2000)   COMMENT '景点简介';
        ALTER TABLE `site` MODIFY COLUMN `open_time` VARCHAR(2000)   COMMENT '景点开放时间';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `site` MODIFY COLUMN `description` VARCHAR(1000)   COMMENT '景点简介';
        ALTER TABLE `site` MODIFY COLUMN `open_time` VARCHAR(1000)   COMMENT '景点开放时间';"""
