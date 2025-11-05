from app.services.ragappfunction import vectorstore, read_doc, chunks
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from app.database.books_repo import BooksRepository

load_dotenv()
class PineconeService:
    def __init__(self):
        self.api = os.getenv("PINECONE_API_KEY")
        self.index_name = "langchaintest2"
        self.embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))#getting openai llm
        self.books_repo = BooksRepository()
        self.temp_folder = "temp"

    def upload_vectors(self, book_title: str):
        """
        Upload vectors to Pinecone from a book file.

        Parameters:
        -----------
        book_id : str
            The ID of the book to process

        Process:
        --------
        1. Get book record from database using book_id
        2. Check if file exists in temp folder (temp/{user_id}_{filename})
        3. If exists: Read file, create docs variable, delete temp file
        4. If not exists: Download from Supabase Storage to temp, read file, create docs variable
        """
        docs = None
        temp_path = None

        try:
            # Step 1: Get book record from database
            book_record = self.books_repo.get_book_by_id(book_title=book_title)

            if not book_record:
                raise Exception(f"Book with the Title: {book_title} not found in database")

            # Step 2: Extract user_id and filename from book record
            user_id = book_record['user_id']
            filename = book_record['filename']

            # Step 3: Construct temp file path
            temp_path = os.path.join(self.temp_folder, f"{user_id}_{filename}")

            # Step 4: Check if file exists in temp folder
            if os.path.exists(temp_path):
                # Case A: File exists in temp folder
                # Read the file and create docs variable
                docs = read_doc(temp_path)

                # Delete the temp file after reading
                os.remove(temp_path)

            else:
                # Case B: File doesn't exist in temp folder
                # Download from Supabase Storage
                storage_path = book_record['storage_path']

                # Download file from Supabase Storage
                file_data = self.books_repo.client.storage.from_("documents").download(storage_path)

                # Save to temp folder
                with open(temp_path, "wb") as f:
                    f.write(file_data)

                # Read the file and create docs variable
                docs = read_doc(temp_path)

                # Delete the temp file after reading
                os.remove(temp_path)

            # Return docs variable
            return docs

        except Exception as e:
            # If error occurs and temp file exists, clean it up
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

            raise Exception(f"Error processing book for vectors: {str(e)}")

    def chunk_doc(self, docs, chunk_size=400, chunk_overlap=50):
        """
        Split documents into chunks for vector storage using the chunks function from ragappfunction.

        Parameters:
        -----------
        docs : list
            List of documents to chunk
        chunk_size : int
            Size of each chunk (default: 400)
        chunk_overlap : int
            Overlap between chunks (default: 50)

        Returns:
        --------
        list : Split documents
        """
        return chunks(docs, chunk_size, chunk_overlap)

    def final_upload(self, book_title: str):
        """
        Final upload method that chunks documents and uploads to Pinecone vectorstore.

        Parameters:
        -----------
        book_title : str
            The title of the book to process

        Process:
        --------
        1. Get book record from database to retrieve namespace
        2. Get docs from upload_vectors method
        3. Chunk the docs using chunk_doc method
        4. Create/update vectorstore with chunked docs and namespace
        """
        try:
            # Step 1: Get book record to retrieve namespace
            book_record = self.books_repo.get_book_by_id(book_title=book_title)

            if not book_record:
                raise Exception(f"Book with the Title: {book_title} not found in database")

            # Get namespace from book record
            namespace = book_record['pinecone_namespace']

            # Step 2: Get docs from upload_vectors
            docs = self.upload_vectors(book_title)

            # Step 3: Chunk the documents
            chunked_docs = self.chunk_doc(docs)

            # Step 4: Create vectorstore and upload
            vectorstore(
                embeddings=self.embeddings,
                indexname=self.index_name,
                pineconeapikey=self.api,
                doc=chunked_docs,
                namespace=namespace
            )

            return {
                "success": True,
                "message": f"Successfully uploaded vectors for book: {book_title}",
                "namespace": namespace,
                "chunks_count": len(chunked_docs)
            }

        except Exception as e:
            raise Exception(f"Error in final upload: {str(e)}")

    def get_vectorstore(self, namespace: str):
        """
        Retrieve a specific namespace as a vector store for searching vectors.

        Parameters:
        -----------
        namespace : str
            The namespace to retrieve (e.g., "user_123")

        Returns:
        --------
        PineconeVectorStore : Vector store instance for the specified namespace
        """
        try:
            # Create and return a PineconeVectorStore instance for the specified namespace
            vector_store = PineconeVectorStore(
                index_name=self.index_name,
                embedding=self.embeddings,
                namespace=namespace,
                pinecone_api_key=self.api
            )

            return vector_store

        except Exception as e:
            raise Exception(f"Error retrieving vectorstore for namespace {namespace}: {str(e)}")

