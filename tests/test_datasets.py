import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.routers.datasets import get_mongo_manager, get_minio_manager

class TestDatasetsUpload(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        
        class MockMongoManager:
            @property
            def db(self):
                class MockCollection:
                    async def insert_one(self, document): return True
                return {"datasets": MockCollection()}

        class MockMinioManager:
            @property
            def client(self):
                class MockMinioClient:
                    def head_bucket(self, Bucket): return True
                    def upload_fileobj(self, Fileobj, Bucket, Key): return True
                return MockMinioClient()

        app.dependency_overrides[get_mongo_manager] = lambda: MockMongoManager()
        app.dependency_overrides[get_minio_manager] = lambda: MockMinioManager()

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_upload_csv_dataset_success(self):
        file_payload = {
            "file": ("test_data.csv", b"col1,col2\n1,2", "text/csv")
        }
        response = self.client.post("/datasets/upload", files=file_payload)
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["status"], "success")

if __name__ == "__main__":
    unittest.main()