from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `userrestaurant` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `restaurant_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_userrest_restaura_15d0ca10` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurant` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_userrest_user_cddb178a` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `userrestaurant`;"""
