from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `site` MODIFY COLUMN `ticket` VARCHAR(3000)   COMMENT '景点门票';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `site` MODIFY COLUMN `ticket` VARCHAR(2000)   COMMENT '景点门票';"""
