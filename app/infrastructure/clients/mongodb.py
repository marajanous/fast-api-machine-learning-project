import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config.settings import settings

logger = logging.getLogger(__name__)


class MongoClient:
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.db: AsyncIOMotorDatabase = None

    def connect(self):
        try:
            logger.info("Connecting to MongoDB...")
            self.client = AsyncIOMotorClient(settings.mongo_uri)
            self.db = self.client["mlops_database"]
            logger.info("MongoDB connection successfully initialized.")
        except Exception as e:
            logger.error(f"Critical error while connecting to MongoDB: {e}")
            raise e

    def close(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection has been closed.")

_client = MongoClient()

def get_mongo_client_singletone():
    return _client
