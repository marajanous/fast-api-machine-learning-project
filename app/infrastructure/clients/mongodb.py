import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings

logger = logging.getLogger(__name__)

class MongoClientManager:
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.db = None

    def connect(self):
        """Inicializace asynchronního připojení k MongoDB."""
        try:
            logger.info("Připojování k MongoDB...")
            self.client = AsyncIOMotorClient(settings.mongo_uri)
            self.db = self.client["mlops_database"]
            logger.info("MongoDB připojení úspěšně inicializováno.")
        except Exception as e:
            logger.error(f"Kritická chyba při připojování k MongoDB: {e}")
            raise e

    def close(self):
        """Korektní uzavření spojení při vypínání serveru."""
        if self.client:
            self.client.close()
            logger.info("MongoDB připojení bylo uzavřeno.")

mongo_manager = MongoClientManager()