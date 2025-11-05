from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional
import os
import tempfile

from app.models.schemas import (
    BookUploadRequest,
    BookProcessRequest,
    BookResponse,
    BookListResponse,
    FileUploadResponse,
    VectorProcessResponse,
    SuccessResponse,
    ErrorResponse
)
from app.services.book_processing_service import BookProcessingService
from app.services.pinecone_service import PineconeService
from app.services.ragappfunction import read_doc, chunks
from app.database.books_repo import BooksRepository


router = APIRouter(
    prefix="/api/books",
    tags=["books"]
)


@router.post("/upload", response_model=FileUploadResponse)
async def upload_book(
    file: UploadFile = File(..., description="PDF file to upload"),
    user_id: str = Form(..., description="User ID"),
    book_title: str = Form(..., min_length=1, max_length=200, description="Book title"),
    author: Optional[str] = Form(None, max_length=100, description="Author name (optional)")
):
    """
    Upload a PDF book and create a database record.

    This endpoint handles:
    1. Validating the uploaded file is a PDF
    2. Saving the file temporarily
    3. Uploading to Supabase Storage
    4. Creating a book record in the database

    Args:
        file: PDF file (multipart/form-data)
        user_id: ID of the user uploading the book
        book_title: Title of the book
        author: Author name (optional)

    Returns:
        FileUploadResponse with upload details

    Raises:
        HTTPException: If file validation fails or upload errors occur
    """
    try:
        # Validate file is a PDF
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )

        # Read file content
        file_content = await file.read()

        if len(file_content) == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )

        # Initialize book service
        book_service = BookProcessingService()

        # Upload PDF and create book record
        book_record = await book_service.upload_pdf(
            file_content=file_content,
            filename=file.filename,
            user_id=user_id,
            book_title=book_title,
            author=author
        )

        return FileUploadResponse(
            success=True,
            message="Book uploaded successfully",
            book_id=book_record.get('book_id'),
            filename=book_record.get('filename'),
            storage_path=book_record.get('storage_path')
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading book: {str(e)}"
        )


@router.post("/upload-and-process", response_model=VectorProcessResponse)
async def upload_and_process_book(
    file: UploadFile = File(..., description="PDF file to upload"),
    user_id: str = Form(..., description="User ID"),
    book_title: str = Form(..., min_length=1, max_length=200, description="Book title"),
    author: Optional[str] = Form(None, max_length=100, description="Author name (optional)"),
    chunk_size: int = Form(400, ge=100, le=2000, description="Size of text chunks"),
    chunk_overlap: int = Form(50, ge=0, le=500, description="Overlap between chunks")
):
    """
    Upload a PDF book and process it into vector embeddings in one operation.

    This is a comprehensive endpoint that:
    1. Uploads the PDF to storage and creates a database record
    2. Processes the PDF into text chunks
    3. Uploads vectors to Pinecone

    This mirrors the upload_book function from the CLI application.

    Args:
        file: PDF file (multipart/form-data)
        user_id: ID of the user uploading the book
        book_title: Title of the book
        author: Author name (optional)
        chunk_size: Size of text chunks for vectorization (default: 400)
        chunk_overlap: Overlap between chunks (default: 50)

    Returns:
        VectorProcessResponse with processing details

    Raises:
        HTTPException: If any step fails
    """
    temp_file_path = None

    try:
        # Step 1: Validate file is a PDF
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )

        # Read file content
        file_content = await file.read()

        if len(file_content) == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )

        # Step 2: Upload to storage and create book record
        book_service = BookProcessingService()

        book_record = await book_service.upload_pdf(
            file_content=file_content,
            filename=file.filename,
            user_id=user_id,
            book_title=book_title,
            author=author
        )

        # Step 3: Save file temporarily for processing
        # Create a temporary file with .pdf extension
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(file_content)
            temp_file_path = tmp_file.name

        # Step 4: Process PDF into chunks
        docs = read_doc(temp_file_path)
        chunked_docs = chunks(docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        # Step 5: Upload to Pinecone
        pinecone_service = PineconeService()
        namespace = f"user_{user_id}"

        # Get vectorstore and add documents
        vector_store = pinecone_service.get_vectorstore(namespace=namespace)
        vector_store.add_documents(chunked_docs)

        # Clean up temp file
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        return VectorProcessResponse(
            success=True,
            message=f"Book uploaded and processed successfully. {len(chunked_docs)} chunks created.",
            namespace=namespace,
            chunks_count=len(chunked_docs)
        )

    except HTTPException:
        raise
    except Exception as e:
        # Clean up temp file on error
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except:
                pass

        raise HTTPException(
            status_code=500,
            detail=f"Error processing book: {str(e)}"
        )


@router.post("/process/{book_title}", response_model=VectorProcessResponse)
async def process_existing_book(
    book_title: str,
    chunk_size: int = 400,
    chunk_overlap: int = 50
):
    """
    Process an already uploaded book into vector embeddings.

    Use this endpoint when you've previously uploaded a book but want to
    re-process it with different chunking parameters or if processing
    was interrupted.

    Args:
        book_title: Title of the book to process
        chunk_size: Size of text chunks for vectorization (default: 400)
        chunk_overlap: Overlap between chunks (default: 50)

    Returns:
        VectorProcessResponse with processing details

    Raises:
        HTTPException: If book not found or processing fails
    """
    try:
        pinecone_service = PineconeService()

        # Get book record to validate it exists
        books_repo = BooksRepository()
        book_record = books_repo.get_book_by_id(book_title=book_title)

        if not book_record:
            raise HTTPException(
                status_code=404,
                detail=f"Book with title '{book_title}' not found"
            )

        # Get docs from storage
        docs = pinecone_service.upload_vectors(book_title)

        # Chunk the documents
        chunked_docs = pinecone_service.chunk_doc(docs, chunk_size, chunk_overlap)

        # Get namespace and upload to Pinecone
        namespace = book_record['pinecone_namespace']
        vector_store = pinecone_service.get_vectorstore(namespace=namespace)
        vector_store.add_documents(chunked_docs)

        return VectorProcessResponse(
            success=True,
            message=f"Book processed successfully. {len(chunked_docs)} chunks created.",
            namespace=namespace,
            chunks_count=len(chunked_docs)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing book: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=BookListResponse)
async def get_user_books(user_id: str):
    """
    Get all books for a specific user.

    Args:
        user_id: ID of the user

    Returns:
        BookListResponse with list of books and total count

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        books_repo = BooksRepository()
        books = books_repo.get_all_books(user_id=user_id)

        if not books:
            books = []

        return BookListResponse(
            books=books,
            total=len(books)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving books: {str(e)}"
        )


@router.get("/{book_title}", response_model=BookResponse)
async def get_book_by_title(book_title: str):
    """
    Get book details by title.

    Args:
        book_title: Title of the book

    Returns:
        BookResponse with book details

    Raises:
        HTTPException: If book not found
    """
    try:
        books_repo = BooksRepository()
        book = books_repo.get_book_by_id(book_title=book_title)

        if not book:
            raise HTTPException(
                status_code=404,
                detail=f"Book with title '{book_title}' not found"
            )

        return BookResponse(**book)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving book: {str(e)}"
        )


@router.delete("/{book_title}", response_model=SuccessResponse)
async def delete_book(book_title: str):
    """
    Delete a book and its associated data.

    Note: This currently only deletes the database record.
    TODO: Add cleanup of storage files and Pinecone vectors

    Args:
        book_title: Title of the book to delete

    Returns:
        SuccessResponse confirming deletion

    Raises:
        HTTPException: If book not found or deletion fails
    """
    try:
        books_repo = BooksRepository()

        # Check if book exists
        book = books_repo.get_book_by_id(book_title=book_title)
        if not book:
            raise HTTPException(
                status_code=404,
                detail=f"Book with title '{book_title}' not found"
            )

        # Delete book record
        # TODO: Add storage and Pinecone cleanup
        result = books_repo.delete_book(book_title=book_title)

        return SuccessResponse(
            success=True,
            message=f"Book '{book_title}' deleted successfully",
            data={"book_title": book_title}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting book: {str(e)}"
        )
