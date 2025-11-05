"""
Database Operations for users
"""
import sys
import os
# Add project root to path when running directly
if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, project_root)

import uuid
import datetime
import time
from app.database.base import BaseRepo


class UsersRepository(BaseRepo):
    """
    Repository for user-related database operations
    """
    def __init__(self):
        super().__init__() #getting supabase client from BaseRepo 

    def create_user(self, email, name):
        """Create user with retry logic"""
        user_data = {
            "user_id": str(uuid.uuid4()),           # str: "abc-123-def-456"
            "email": email,                          # str
            "name": name,                            # str
            "created_at": datetime.datetime.now().isoformat() # str: "2024-01-15T10:30:00"
        }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.table("user_table").insert(user_data).execute()
                return response
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Retry {attempt + 1}/{max_retries} - Error creating user: {e}")
                    time.sleep(1 * (attempt + 1))
                else:
                    raise Exception(f"Failed to create user after {max_retries} attempts: {e}")

    def get_by_id(self, user_id):
        """Get user by user_id"""
        try:
            data_on_user = self.client.table("user_table").select("*").eq("user_id", user_id).execute()
            return data_on_user.data[0] if data_on_user.data else None
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None

    def get_by_email(self, email):
        """Get user by email with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                data_on_user = self.client.table("user_table").select("*").eq("email", email).execute()
                return data_on_user.data[0] if data_on_user.data else None
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Retry {attempt + 1}/{max_retries} - Error getting user by email: {e}")
                    time.sleep(1 * (attempt + 1))
                else:
                    print(f"Error getting user by email after {max_retries} attempts: {e}")
                    return None

    def get_by_name(self, name):
        """Get user by name"""
        try:
            data_on_user = self.client.table("user_table").select("*").eq("name", name).execute()
            return data_on_user.data[0] if data_on_user.data else None
        except Exception as e:
            print(f"Error getting user by name: {e}")
            return None
        
