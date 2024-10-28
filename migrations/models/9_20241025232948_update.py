from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `restaurant` MODIFY COLUMN `telephone` VARCHAR(100)   COMMENT '餐厅联系电话';
        ALTER TABLE `restaurant` MODIFY COLUMN `location` VARCHAR(500) NOT NULL  COMMENT '餐厅地址';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `restaurant` MODIFY COLUMN `telephone` VARCHAR(20)   COMMENT '餐厅联系电话';
        ALTER TABLE `restaurant` MODIFY COLUMN `location` VARCHAR(255) NOT NULL  COMMENT '餐厅地址';"""
