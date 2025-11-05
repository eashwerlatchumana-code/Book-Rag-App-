import sys
import os
# Add project root to path when running directly
if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, project_root)

import uuid
import datetime
from app.database.base import BaseRepo

class MessagesRepo(BaseRepo):
    def __init__(self):
        super().__init__() #getting supabase client from BaseRepo

    def add_message(self, chat_id=None, role=None, content=None):
        chat_data = {
            "message_id": str(uuid.uuid4()),
            "chat_id": chat_id,
            "role": role,
            "content" : content,
            "created_at": datetime.datetime.now().isoformat(),
        }
        try:
            response = self.client.table("messages_table").insert(chat_data).execute()
            return response 
        except Exception as e:
            print(e)
            return None
    def get_message_by_id(self, message_id=None):
        try:
            if message_id:
                data_on_chat = self.client.table("messages_table").select("*").eq("message_id", message_id).execute()
                return data_on_chat.data[0] if data_on_chat.data else None
        except Exception as E:
            print(f"Couldn't Load chat, this is what the system says: {E}")

    def get_messages_by_chat_id(self, chat_id=None):
        """
        Get all messages for a specific chat_id.

        Parameters:
        -----------
        chat_id : str
            The chat_id to retrieve messages for

        Returns:
        --------
        list : List of message records, or None if error
        """
        try:
            if chat_id:
                data = self.client.table("messages_table").select("*").eq("chat_id", chat_id).execute()
                return data.data if data.data else []
        except Exception as E:
            print(f"Couldn't load messages for chat_id {chat_id}: {E}")
            return None