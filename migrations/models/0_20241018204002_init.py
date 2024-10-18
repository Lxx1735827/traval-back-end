from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `site` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(20) NOT NULL  COMMENT '景点名字',
    `city` VARCHAR(20) NOT NULL  COMMENT '城市',
    `description` VARCHAR(1000) NOT NULL  COMMENT '景点描述',
    `picture` VARCHAR(40) NOT NULL  COMMENT '景点图片' DEFAULT 'static/site/默认图片.png',
    `location` VARCHAR(40) NOT NULL  COMMENT '景点地址',
    `longitude` DECIMAL(9,6) NOT NULL  COMMENT '经度',
    `latitude` DECIMAL(9,6) NOT NULL  COMMENT '纬度'
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `user` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `number` VARCHAR(11) NOT NULL  COMMENT '电话号码',
    `username` VARCHAR(20) NOT NULL  COMMENT '用户名' DEFAULT 'username',
    `password` VARCHAR(11) NOT NULL  COMMENT '密码',
    `avatar` VARCHAR(255) NOT NULL  COMMENT '头像' DEFAULT 'static/site/默认头像.png'
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `conversation` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `content` VARCHAR(10000) NOT NULL  COMMENT '历史对话',
    `user_id` INT,
    CONSTRAINT `fk_conversa_user_84883661` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE SET NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `strategy` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `strategy` VARCHAR(2048) NOT NULL  COMMENT '攻略，日期加地点',
    `user_id` INT,
    CONSTRAINT `fk_strategy_user_8cb2e272` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE SET NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `user_site` (
    `site_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    FOREIGN KEY (`site_id`) REFERENCES `site` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uidx_user_site_site_id_4e82d5` (`site_id`, `user_id`)
) CHARACTER SET utf8mb4 COMMENT='喜欢该景点的用户';
CREATE TABLE IF NOT EXISTS `user_site` (
    `user_id` INT NOT NULL,
    `site_id` INT NOT NULL,
    FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`site_id`) REFERENCES `site` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uidx_user_site_user_id_45bc6d` (`user_id`, `site_id`)
) CHARACTER SET utf8mb4 COMMENT='用户收藏的景点';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
