from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `restaurant` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(100) NOT NULL  COMMENT '餐厅名字',
    `city` VARCHAR(20) NOT NULL  COMMENT '城市',
    `image` VARCHAR(255) NOT NULL  COMMENT '餐厅图片' DEFAULT 'static/restaurant/默认图片.png',
    `location` VARCHAR(255) NOT NULL  COMMENT '餐厅地址',
    `telephone` VARCHAR(20)   COMMENT '餐厅联系电话',
    `longitude` DECIMAL(9,6) NOT NULL  COMMENT '经度',
    `latitude` DECIMAL(9,6) NOT NULL  COMMENT '纬度',
    `review_1` LONGTEXT   COMMENT '餐厅评论',
    `review_2` LONGTEXT   COMMENT '餐厅评论',
    `review_3` LONGTEXT   COMMENT '餐厅评论',
    `review_4` LONGTEXT   COMMENT '餐厅评论',
    `review_5` LONGTEXT   COMMENT '餐厅评论',
    `type` VARCHAR(50) NOT NULL  COMMENT '对象类型' DEFAULT '餐厅'
) CHARACTER SET utf8mb4;
        ALTER TABLE `site` ADD `type` VARCHAR(50) NOT NULL  COMMENT '对象类型' DEFAULT '景点';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `site` DROP COLUMN `type`;
        DROP TABLE IF EXISTS `restaurant`;"""
