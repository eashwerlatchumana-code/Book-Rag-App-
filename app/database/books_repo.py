import sys
import os
# Add project root to path when running directly
if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, project_root)

import uuid
import datetime
from app.database.base import BaseRepo


class BooksRepository(BaseRepo):
    """
    Repository for user-related database operations
    """
    def __init__(self):
        super().__init__() #getting supabase client from BaseRepo

    def upload_file_to_storage(self, user_id: str, file_content: bytes, filename: str, bucket_name: str = "book_storage"):
        """Upload file to Supabase Storage in user's subfolder"""
        storage_path = f"{user_id}/{filename}"

        # Detect content type based on file extension
        content_types = {
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".txt": "text/plain",
            ".epub": "application/epub+zip"
        }

        file_ext = os.path.splitext(filename)[1].lower()
        content_type = content_types.get(file_ext, "application/octet-stream")

        result = self.client.storage.from_(bucket_name).upload(
            path=storage_path,
            file=file_content,
            file_options={"content-type": content_type}
        )

        return {
            "storage_path": storage_path
        }

    def create_book(self, user_id=None, filename=None, author=None, book_title=None, storage_path=None, pinecone_namespace=None):
        if pinecone_namespace is None:
            pinecone_namespace = f"user_{user_id}"
        else:
            pass
        books_data = {
            "book_id": str(uuid.uuid4()),
            "user_id": user_id,
            "book_title": book_title,
            "filename": filename,
            "storage_path": storage_path,
            "author": author,
            "metadata": {},
            "pinecone_namespace": pinecone_namespace,
            "uploaded_at": datetime.datetime.now().isoformat()
        }
        response = self.client.table("books_table").insert(books_data).execute()
        print("Created Success") 
        return response
       
    def get_book_by_id(self, book_id=None, book_title=None, filename=None):
        try:
            if book_id:
                data_on_book = self.client.table("books_table").select("*").eq("book_id", book_id).execute()
                return data_on_book.data[0] if data_on_book.data else None
            elif book_title:
                data_on_book = self.client.table("books_table").select("*").eq("book_title", book_title).execute()
                return data_on_book.data[0] if data_on_book.data else None
            elif filename:
                data_on_book = self.client.table("books_table").select("*").eq("filename", filename).execute()
                return data_on_book.data[0] if data_on_book.data else None
        except Exception as e:
            print(e)
            return None

    def get_all_books(self, user_id):
        try:
            data_on_book = self.client.table("books_table").select("*").eq("user_id", user_id).execute()
            return data_on_book.data if data_on_book.data else None
        except Exception as e:
            print(e)
            return None
