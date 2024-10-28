from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `user_restaurant` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `restaurant_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_user_res_restaura_f0cbd0ff` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurant` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_user_res_user_fc5df791` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
        DROP TABLE IF EXISTS `userrestaurant`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `user_restaurant`;"""
