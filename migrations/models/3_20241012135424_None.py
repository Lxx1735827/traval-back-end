from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `site` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(20) NOT NULL  COMMENT '景点名字',
    `city` VARCHAR(20) NOT NULL  COMMENT '城市',
    `longitude` DECIMAL(9,6) NOT NULL  COMMENT '经度',
    `latitude` DECIMAL(9,6) NOT NULL  COMMENT '纬度'
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `strategy` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `strategy` VARCHAR(2048) NOT NULL  COMMENT '攻略，日期加地点'
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `user` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `number` VARCHAR(11) NOT NULL  COMMENT '电话号码',
    `username` VARCHAR(20) NOT NULL  COMMENT '用户名' DEFAULT 'username',
    `password` VARCHAR(11) NOT NULL  COMMENT '密码',
    `avatar` VARCHAR(255) NOT NULL  COMMENT '头像' DEFAULT 'static/默认头像.png'
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
