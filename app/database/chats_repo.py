import sys
import os
# Add project root to path when running directly
if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, project_root)

import uuid
import datetime
from app.database.base import BaseRepo

class chatsRepo(BaseRepo):
     def __init__(self):
        super().__init__() #getting supabase client from BaseRepo

     def create_chat(self, user_id=None, title=None, updated_at=None):
        if updated_at is None:
            updated_at = datetime.datetime.now().isoformat()

        chat_data = {
            "chat_id": str(uuid.uuid4()),
            "user_id": user_id,
            "chat_title": title,
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": updated_at,
            "messages": {}
        }

        try:
            response = self.client.table("chats_table").insert(chat_data).execute()
            return response
        except Exception as e:
            print(e)
            return None

     def get_chat_by_id(self, chat_id=None, title=None):
        try:
            if chat_id:
                data_on_chat = self.client.table("chats_table").select("*").eq("chat_id", chat_id).execute()
                return data_on_chat.data[0] if data_on_chat.data else None
            elif title:
                data_on_chat = self.client.table("chats_table").select("*").eq("chat_title", title).execute()
                return data_on_chat.data[0] if data_on_chat.data else None
        except Exception as e:
            print(e)
            return None

     def get_all_chats(self, user_id):
        try:
            data_on_chat = self.client.table("chats_table").select("*").eq("user_id", user_id).execute()
            return data_on_chat.data if data_on_chat.data else None
        except Exception as e:
            print(e)
            return None

     def get_chat_messages(self, chat_id=None):
        """
        Retrieves all messages for a specific chat in chronological order.
        Returns a list of messages with role and content.
        """
        try:
            chat = self.get_chat_by_id(chat_id=chat_id)
            if not chat:
                print(f"Chat with id {chat_id} not found")
                return None

            messages = chat.get("messages", {})

            # Convert messages dict to a list of message objects
            message_list = []
            for message_id, message_data in messages.items():
                message_list.append({
                    "message_id": message_id,
                    "role": message_data.get("role"),
                    "content": message_data.get("content")
                })

            return message_list
        except Exception as e:
            print(f"Error retrieving chat messages: {e}")
            return None

     def update_chat(self, chat_id=None, message_id=None):
        """
        Updates the chat's messages field with a new message from messages_table.
        Retrieves the message by message_id and appends it to the chat's messages in OpenAI format.
        """
        try:
            if message_id:
                pass
            else: 
                print("Sorry Enter a message_ID to retreive the data ")
            # Get the message from messages_table
            message_data = self.client.table("messages_table").select("role, content").eq("message_id", message_id).execute()

            if not message_data.data:
                print(f"Message with id {message_id} not found")
                return None

            message = message_data.data[0]

            # Get current chat data
            chat = self.get_chat_by_id(chat_id=chat_id)
            if not chat:
                print(f"Chat with id {chat_id} not found")
                return None

            # Get existing messages or initialize as empty dict
            messages = chat.get("messages", {})

            # Create new message in OpenAI format
            new_message = {
                "role": message["role"],
                "content": message["content"]
            }

            # Add message to messages dict with message_id as key
            messages[message_id] = new_message

            # Update chat with new messages and updated_at timestamp
            update_data = {
                "messages": messages,
                "updated_at": datetime.datetime.now().isoformat()
            }

            response = self.client.table("chats_table").update(update_data).eq("chat_id", chat_id).execute()
            print("Updated Chat Successfully")
            return response

        except Exception as e:
            print(f"Error updating chat: {e}")
            return None