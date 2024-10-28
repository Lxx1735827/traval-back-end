from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `restaurant` DROP COLUMN `review_5`;
        ALTER TABLE `restaurant` DROP COLUMN `review_1`;
        ALTER TABLE `restaurant` DROP COLUMN `review_4`;
        ALTER TABLE `restaurant` DROP COLUMN `review_2`;
        ALTER TABLE `restaurant` DROP COLUMN `review_3`;
        ALTER TABLE `site` DROP COLUMN `review_5`;
        ALTER TABLE `site` DROP COLUMN `review_1`;
        ALTER TABLE `site` DROP COLUMN `review_4`;
        ALTER TABLE `site` DROP COLUMN `review_2`;
        ALTER TABLE `site` DROP COLUMN `review_3`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `site` ADD `review_5` LONGTEXT   COMMENT '景点评论';
        ALTER TABLE `site` ADD `review_1` LONGTEXT   COMMENT '景点评论';
        ALTER TABLE `site` ADD `review_4` LONGTEXT   COMMENT '景点评论';
        ALTER TABLE `site` ADD `review_2` LONGTEXT   COMMENT '景点评论';
        ALTER TABLE `site` ADD `review_3` LONGTEXT   COMMENT '景点评论';
        ALTER TABLE `restaurant` ADD `review_5` LONGTEXT   COMMENT '餐厅评论';
        ALTER TABLE `restaurant` ADD `review_1` LONGTEXT   COMMENT '餐厅评论';
        ALTER TABLE `restaurant` ADD `review_4` LONGTEXT   COMMENT '餐厅评论';
        ALTER TABLE `restaurant` ADD `review_2` LONGTEXT   COMMENT '餐厅评论';
        ALTER TABLE `restaurant` ADD `review_3` LONGTEXT   COMMENT '餐厅评论';"""
