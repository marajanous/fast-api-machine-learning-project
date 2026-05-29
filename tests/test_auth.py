import unittest
from unittest.mock import AsyncMock, MagicMock
import asyncio

from app.infrastructure.services.auth import AuthenticationService

class TestAuthenticationService(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_users_collection = MagicMock()
        self.mock_db.__getitem__.return_value = self.mock_users_collection
        
        self.auth_service = AuthenticationService(db_client=self.mock_db)
        
        self.test_email = "developer@mlops.cz"
        self.test_password = "secret123"
        self.hashed_password = self.auth_service.hash_password(self.test_password)

    def run_async(self, coro):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)

    def test_register_user_success(self):
        self.mock_users_collection.find_one = AsyncMock(return_value=None)
        self.mock_users_collection.insert_one = AsyncMock()

        result = self.run_async(self.auth_service.register_user(self.test_email, self.test_password))
        
        self.assertEqual(result, self.test_email)
        self.mock_users_collection.insert_one.assert_called_once()

    def test_register_user_already_exists(self):
        self.mock_users_collection.find_one = AsyncMock(return_value={"email": self.test_email})

        result = self.run_async(self.auth_service.register_user(self.test_email, self.test_password))
        
        self.assertIsNone(result)

    def test_login_user_success(self):
        self.mock_users_collection.find_one = AsyncMock(return_value={
            "email": self.test_email,
            "password": self.hashed_password
        })

        success = self.run_async(self.auth_service.login_user(self.test_email, self.test_password))
        self.assertTrue(success)

    def test_login_user_wrong_password(self):
        self.mock_users_collection.find_one = AsyncMock(return_value={
            "email": self.test_email,
            "password": self.hashed_password
        })

        success = self.run_async(self.auth_service.login_user(self.test_email, "wrong_password_here"))
        self.assertFalse(success)

    def test_logout_user(self):
        self.run_async(self.auth_service.logout_user(self.test_email))
        self.assertIn(self.test_email, self.auth_service.logged_out_emails)

if __name__ == "__main__":
    unittest.main()