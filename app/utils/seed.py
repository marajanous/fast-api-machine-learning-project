import asyncio
import logging


from app.infrastructure.clients.mongodb import _client
from app.infrastructure.clients.minio import minio_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_everything():
    logger.info("Starting database initialization and seeding...")

    try:
        logger.info("Initializing MinIO manager...")
        minio_manager.connect()

        await asyncio.sleep(1)

        s3_client = minio_manager.client
        if s3_client is None:
            raise RuntimeError("MinIO S3 client (.client) is still None after connection.")

        bucket_name = "datasets"
        
        response = s3_client.list_buckets()
        existing_buckets = [b['Name'] for b in response.get('Buckets', [])]

        if bucket_name in existing_buckets:
            logger.info(f"Bucket '{bucket_name}' already exists in MinIO.")
        else:
            s3_client.create_bucket(Bucket=bucket_name)
            logger.info(f"Bucket '{bucket_name}' successfully created in MinIO.")
            
    except Exception as e:
        logger.error(f"Error during MinIO initialization: {e}")

  
    try:
        logger.info("Initializing MongoDB client...")
        _client.connect()

        await asyncio.sleep(1)

        db = _client.db
        if db is None:
            raise RuntimeError("MongoDB database (.db) is still None after connection.")

        existing_dataset = await db["datasets"].find_one({"filename": "seed_demo_data.csv"})
        
        if not existing_dataset:
            demo_metadata = {
                "filename": "seed_demo_data.csv",
                "content_type": "text/csv",
                "status": "uploaded",
                "description": "Automatically generated seed data for testing the API interface."
            }
            await db["datasets"].insert_one(demo_metadata)
            logger.info("MongoDB successfully seeded with demo data (seed_demo_data.csv).")
        else:
            logger.info("MongoDB already contains seed data, skipping...")
            
    except Exception as e:
        logger.error(f"Error during MongoDB seeding: {e}")

    logger.info(" Database initialization and seeding is complete!")

if __name__ == "__main__":
    asyncio.run(seed_everything())