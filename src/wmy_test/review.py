from src.schema import *
from tortoise import Tortoise, run_async

async def transfer_reviews():
    await Tortoise.init(
        db_url="mysql://root:082231@localhost:3306/travel",
        modules={'models': ["src.model", "aerich.models"]}
    )
    await Tortoise.generate_schemas()
    # Fetch all sites and restaurants
    sites = await Site.all()
    restaurants = await Restaurant.all()

    # Prepare reviews for insertion
    reviews_to_insert = []

    # Process sites
    for site in sites:
        for i in range(1, 6):  # Iterate through review_1 to review_5
            review_content = getattr(site, f'review_{i}')
            if review_content and review_content != "不错，推荐":
                reviews_to_insert.append(
                    Review(
                        entity_id=site.id,
                        entity_type="景点",
                        user_id=1,  # Set this according to your logic
                        content=review_content,
                        created_at=datetime.utcnow()
                    )
                )
        # Clear review attributes
        for i in range(1, 6):
            setattr(site, f'review_{i}', None)
    await Site.bulk_update(sites, fields=['review_1', 'review_2', 'review_3', 'review_4', 'review_5'])

    # Process restaurants
    for restaurant in restaurants:
        for i in range(1, 6):
            review_content = getattr(restaurant, f'review_{i}')
            if review_content and review_content != "不错，推荐":
                reviews_to_insert.append(
                    Review(
                        entity_id=restaurant.id,
                        entity_type="餐厅",
                        user_id=1,  # Set this according to your logic
                        content=review_content,
                        created_at=datetime.utcnow()
                    )
                )
        # Clear review attributes
        for i in range(1, 6):
            setattr(restaurant, f'review_{i}', None)
    await Restaurant.bulk_update(restaurants, fields=['review_1', 'review_2', 'review_3', 'review_4', 'review_5'])

    # Bulk create reviews
    await Review.bulk_create(reviews_to_insert)


if __name__ == "__main__":
    run_async(transfer_reviews())
