import os
from app.database.books_repo import BooksRepository


class BookProcessingService:
    """
    Service for handling book upload operations.
    This service coordinates between receiving files and storing them.
    """

    def __init__(self):
        """
        Initialize the service with necessary dependencies.
        - books_repo: Repository for database and storage operations
        - temp_folder: Local folder to temporarily store uploaded files
        """
        self.books_repo = BooksRepository()
        self.temp_folder = "temp"

    async def upload_pdf(
        self,
        file_content: bytes,
        filename: str,
        user_id: str,
        book_title: str,
        author: str = None
):
        """
        Upload a PDF book and create a database record.

        Parameters:
        -----------
        file_content : bytes
            The raw binary content of the uploaded PDF file
        filename : str
            The name of the file (e.g., "mybook.pdf")
        user_id : str
            The ID of the user uploading the book
        book_title : str
            The title of the book
        author : str, optional
            The author of the book (default: None)

        Returns:
        --------
        dict
            The created book record from the database

        Process:
        --------
        1. Save file to temp folder for potential later processing (Chunking the doc and uploading to Pinecoene)
        2. Upload file to Supabase Storage in user's subfolder
        3. Create book record in database with storage path
        """
        temp_path = None

        try:
            # Step 1: Save file to temp folder
            # Format: temp/user123_mybook.pdf
            # This allows the file to be processed later by other services
            temp_path = os.path.join(self.temp_folder, f"{user_id}_{filename}")

            # Write the binary content to a file
            with open(temp_path, "wb") as f:
                f.write(file_content)

            # Step 2: Upload to Supabase Storage
            # This creates a subfolder with user_id and stores the file
            # Example path in Supabase: documents/user123/mybook.pdf
            upload_result = self.books_repo.upload_file_to_storage(
                user_id=user_id,
                file_content=file_content,
                filename=filename
            )

            # Step 3: Create book record in database
            # This saves metadata about the book including where it's stored
            book_record = self.books_repo.create_book(
                user_id=user_id,
                filename=filename,
                author=author,
                book_title=book_title,
                storage_path=upload_result["storage_path"]  # Path from Supabase
            )

            # Return the created book record
            return book_record

        except Exception as e:
            # If any error occurs, clean up the temp file
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

            # Re-raise the exception with context
            raise Exception(f"Error uploading PDF: {str(e)}")
