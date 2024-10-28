from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `site` MODIFY COLUMN `ticket` VARCHAR(1500)   COMMENT '景点门票';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `site` MODIFY COLUMN `ticket` VARCHAR(1000)   COMMENT '景点门票';"""
