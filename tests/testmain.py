"""
Main CLI application for RAG Chat Backend
Handles user login, chat, history, profile, and book uploads
Modified version with automatic chat continuation
"""
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.users_repo import UsersRepository
from app.database.chats_repo import chatsRepo
from app.services.chat_service import ChatService
from app.services.book_processing_service import BookProcessingService
from app.services.ragappfunction import read_doc, chunks
from app.services.pinecone_service import PineconeService


class UserProfile:
    """
    User profile class to store current user session data
    """
    def __init__(self, name_or_email: str):
        """
        Initialize user profile by fetching user_id from database

        Args:
            name_or_email: User's name or email for login
        """
        self.users_repo = UsersRepository()
        self.user_data = None  # Initialize before calling _get_user_id
        self.user_id = self._get_user_id(name_or_email)

    def _get_user_id(self, name_or_email: str) -> str:
        """
        Fetch user_id from database using name or email

        Args:
            name_or_email: User's name or email

        Returns:
            user_id if found, None otherwise
        """
        # Try email first (if contains @)
        if "@" in name_or_email:
            user_data = self.users_repo.get_by_email(email=name_or_email)
        else:
            # Otherwise try name
            user_data = self.users_repo.get_by_name(name=name_or_email)

        if user_data:
            self.user_data = user_data
            return user_data.get("user_id")
        return None

    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.user_id is not None

    def get_display_name(self) -> str:
        """Get user's display name"""
        if self.user_data:
            return self.user_data.get("name", "Unknown User")
        return "Unknown User"


def login() -> UserProfile:
    """
    Handle user login

    Returns:
        UserProfile object if login successful, None otherwise
    """
    print("\n" + "="*60)
    print(" " * 15 + "Welcome to RAG Chat Backend!")
    print("="*60)

    while True:
        print("\n" + "-"*60)
        print("Please enter your name or email to login")
        print("  - If you enter an email (contains @), we'll search by email")
        print("  - Otherwise, we'll search by name")
        print("-"*60)

        name_or_email = input("\nEnter your name or email: ").strip()

        if not name_or_email:
            print("Please enter a valid name or email")
            continue

        print("\nChecking credentials...")
        # Create user profile and attempt authentication
        user_profile = UserProfile(name_or_email)

        if user_profile.is_authenticated():
            print(f"Login successful! Welcome back, {user_profile.get_display_name()}!")
            return user_profile
        else:
            print(f"\nUser not found with '{name_or_email}'")
            print("\nWhat would you like to do?")
            print("  [1] Try again with different credentials")
            print("  [2] Create a new user account")
            print("  [3] Exit application")

            choice = input("\nEnter your choice (1-3): ").strip()

            if choice == '1':
                continue
            elif choice == '2':
                # Create new user
                new_user = create_new_user()
                if new_user:
                    return new_user
                # If creation failed, loop back to login
            else:
                print("\nExiting application...")
                return None


def create_new_user() -> UserProfile:
    """
    Create a new user account

    Returns:
        UserProfile object if creation successful, None otherwise
    """
    print("\n" + "="*60)
    print(" " * 18 + "CREATE NEW USER")
    print("="*60)

    users_repo = UsersRepository()

    while True:
        print("\nPlease provide the following information:")
        print("-"*60)

        # Get email
        email = input("\nEnter your email: ").strip()
        if not email:
            print("Email is required")
            retry = input("Would you like to try again? (y/n): ").strip().lower()
            if retry != 'y':
                return None
            continue

        if "@" not in email:
            print("Please enter a valid email address (must contain @)")
            retry = input("Would you like to try again? (y/n): ").strip().lower()
            if retry != 'y':
                return None
            continue

        # Check if email already exists
        existing_user = users_repo.get_by_email(email)
        if existing_user:
            print(f"\nError: A user with email '{email}' already exists!")
            print("Please login with this email or use a different email.")
            retry = input("\nWould you like to try a different email? (y/n): ").strip().lower()
            if retry != 'y':
                return None
            continue

        # Get name
        name = input("Enter your name: ").strip()
        if not name:
            print("Name is required")
            retry = input("Would you like to try again? (y/n): ").strip().lower()
            if retry != 'y':
                return None
            continue

        # Confirm details
        print("\n" + "-"*60)
        print("Please confirm your details:")
        print(f"  Email: {email}")
        print(f"  Name: {name}")
        print("-"*60)
        confirm = input("\nIs this information correct? (y/n): ").strip().lower()

        if confirm != 'y':
            print("\nLet's try again...")
            continue

        # Create user
        try:
            print("\nCreating user account...")
            response = users_repo.create_user(email=email, name=name)

            if response and response.data:
                print(f"\nAccount created successfully!")
                print(f"Welcome, {name}!")

                # Create and return user profile
                user_profile = UserProfile(email)
                if user_profile.is_authenticated():
                    return user_profile
                else:
                    print("\nError: Failed to authenticate after creation")
                    return None
            else:
                print("\nError: Failed to create user account")
                retry = input("Would you like to try again? (y/n): ").strip().lower()
                if retry != 'y':
                    return None
        except Exception as e:
            print(f"\nError creating user: {str(e)}")
            retry = input("Would you like to try again? (y/n): ").strip().lower()
            if retry != 'y':
                return None


def display_main_menu():
    """Display the main menu options"""
    print("\n" + "="*60)
    print(" " * 20 + "MAIN MENU")
    print("="*60)
    print("\nAvailable Options:\n")
    print("  [1] Start/Continue Chat")
    print("  [2] View Chat History")
    print("  [3] View Profile")
    print("  [4] Upload Book/PDF")
    print("  [5] Exit")
    print("\n" + "="*60)


def view_profile(user_profile: UserProfile):
    """
    Display user profile information

    Args:
        user_profile: User profile object
    """
    print("\n" + "="*60)
    print(" " * 22 + "USER PROFILE")
    print("="*60)
    print(f"\nName: {user_profile.user_data.get('name', 'N/A')}")
    print(f"Email: {user_profile.user_data.get('email', 'N/A')}")
    print(f"User ID: {user_profile.user_id}")
    print(f"Created: {user_profile.user_data.get('created_at', 'N/A')}")
    print("\n" + "="*60)
    input("\nPress Enter to return to main menu...")


def view_chat_history(user_profile: UserProfile):
    """
    Display chat history and allow user to select a chat to continue

    Args:
        user_profile: User profile object

    Returns:
        chat_id if user selects a chat, None otherwise
    """
    chats_repo_instance = chatsRepo()

    print("\n" + "="*60)
    print(" " * 20 + "CHAT HISTORY")
    print("="*60)

    print("\nFetching your chat history...")
    all_chats = chats_repo_instance.get_all_chats(user_id=user_profile.user_id)

    if not all_chats or len(all_chats) == 0:
        print("\nNo chat history found. Start a new conversation!")
        input("\nPress Enter to return to main menu...")
        return None

    print(f"\nFound {len(all_chats)} chat(s):\n")

    # Display chats with enumeration
    for idx, chat in enumerate(all_chats, 1):
        title = chat.get('chat_title', 'Untitled Chat')[:50]  # Truncate long titles
        created_at = chat.get('created_at', 'Unknown date')[:10]  # Just the date
        print(f"  [{idx}] {title}... (Created: {created_at})")

    print(f"\n  [0] Return to Main Menu")
    print("="*60)

    while True:
        try:
            choice = input("\nEnter the number of the chat to continue: ").strip()

            if choice == '0':
                return None

            choice_num = int(choice)
            if 1 <= choice_num <= len(all_chats):
                selected_chat = all_chats[choice_num - 1]
                chat_id = selected_chat.get('chat_id')
                chat_title = selected_chat.get('chat_title', 'Untitled Chat')
                print(f"\nSelected chat: '{chat_title[:50]}'")
                return chat_id
            else:
                print(f"Please enter a number between 0 and {len(all_chats)}")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n\nReturning to main menu...")
            return None


def chat_session(user_profile: UserProfile, chat_id=None):
    """
    Handle chat session - either new or continue existing
    Modified to automatically continue chat unless user types 'end chat'

    Args:
        user_profile: User profile object
        chat_id: Optional chat_id to continue existing chat
    """
    print("\n" + "="*60)
    print(" " * 20 + "CHAT SESSION")
    print("="*60)

    try:
        current_chat_id = chat_id

        if current_chat_id:
            print(f"\nContinuing existing chat (ID: {current_chat_id[:8]}...)")

            # Display chat history when continuing
            chats_repo_instance = chatsRepo()
            chat_data = chats_repo_instance.get_chat_by_id(chat_id=current_chat_id)

            if chat_data:
                chat_title = chat_data.get('chat_title', 'Untitled Chat')
                print(f"Chat Title: {chat_title}")

                # Get messages from messages_table for proper ordering
                from app.database.messages_repo import MessagesRepo
                messages_repo = MessagesRepo()
                messages_list = messages_repo.get_messages_by_chat_id(chat_id=current_chat_id)

                if messages_list and len(messages_list) > 0:
                    print("\n" + "-"*60)
                    print("Previous Conversation:")
                    print("-"*60)

                    # Sort messages by created_at to ensure chronological order
                    sorted_messages = sorted(messages_list, key=lambda x: x.get('created_at', ''))

                    for msg in sorted_messages:
                        role = msg.get('role', 'unknown')
                        content = msg.get('content', '')

                        if role == 'user':
                            # Extract actual question from "Context::\n...\n\nQuestion: {question}" format
                            if "Question: " in content:
                                # Split by "Question: " and take the last part
                                actual_question = content.split("Question: ", 1)[-1]
                                print(f"\nYou: {actual_question}")
                            else:
                                # Fallback if format is different
                                print(f"\nYou: {content}")
                        elif role == 'assistant':
                            print(f"\nAI: {content}")

                    print("\n" + "-"*60)
                else:
                    print("\n[INFO] No previous messages found in this chat")
        else:
            print("\nStarting new chat session")

        # Display namespace information and check for available books
        namespace = f"user_{user_profile.user_id}"
        print(f"\n[INFO] Using Pinecone namespace: {namespace}")

        # Check if user has uploaded books
        from app.database.books_repo import BooksRepository
        books_repo = BooksRepository()
        user_books = books_repo.get_all_books(user_id=user_profile.user_id)

        if user_books and len(user_books) > 0:
            print(f"[INFO] Found {len(user_books)} book(s) in your library")
            print("[INFO] AI will search your books for context when answering")
        else:
            print("[INFO] No books uploaded yet - AI will use general knowledge")
            print("[INFO] Upload books via Main Menu > Upload Book/PDF to enable RAG")

        print("\nCommands:")
        print("  - Type your question to chat")
        print("  - Type 'end chat' to end the current chat session")
        print("  - Type 'main' to return to main menu")
        print("  - Type 'exit' to quit the application")
        print("="*60 + "\n")

        while True:
            try:
                user_input = input("\nYou: ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.lower() in ['exit', 'quit']:
                    print("\nExiting application...")
                    sys.exit(0)

                if user_input.lower() == 'main':
                    print("\nReturning to main menu...")
                    break

                # Check for 'end chat' command
                if user_input.lower() == 'end chat':
                    print("\nEnding current chat session...")
                    print("Starting fresh chat for next question.\n")
                    current_chat_id = None
                    continue

                # Process chat message
                print("\nAI is thinking...")

                # Initialize ChatService for this message
                chat_service = ChatService(
                    user_id=user_profile.user_id,
                    question=user_input,
                    retrieve_history=True if current_chat_id else False
                )

                if current_chat_id is None:
                    # Start new chat
                    result = chat_service.new_chat(
                        question=user_input,
                        vectorstore=chat_service.vectorstore
                    )

                    if result and result != "end":
                        print(f"\nAI Response: {result}")

                        # Get the chat_id that was created
                        chats_repo_instance = chatsRepo()
                        all_chats = chats_repo_instance.get_all_chats(user_id=user_profile.user_id)
                        if all_chats and len(all_chats) > 0:
                            # Sort by created_at and get the most recent
                            sorted_chats = sorted(all_chats, key=lambda x: x.get('created_at', ''), reverse=True)
                            current_chat_id = sorted_chats[0].get('chat_id')
                            print("\n[INFO] Chat will continue automatically. Type 'end chat' to start a new conversation.")
                    else:
                        print("\nFailed to create chat. Please try again.")

                else:
                    # Continue existing chat
                    result = chat_service.continuing_chat(
                        chat_id=current_chat_id,
                        question=user_input
                    )

                    if result and result != "end":
                        print(f"\nAI Response: {result}")
                        print("\n[INFO] Chat continues. Type 'end chat' to start a new conversation.")
                    else:
                        print("\nFailed to continue chat. Please try again.")

            except KeyboardInterrupt:
                print("\n\nChat interrupted. Returning to main menu...")
                break
            except Exception as e:
                print(f"\nError during chat: {str(e)}")
                print("Please try again or type 'main' to return to main menu.")

    except Exception as e:
        print(f"\nError initializing chat: {str(e)}")
        input("\nPress Enter to return to main menu...")


def upload_book(user_profile: UserProfile):
    """
    Handle book/PDF upload and processing

    Args:
        user_profile: User profile object
    """
    print("\n" + "="*60)
    print(" " * 20 + "BOOK UPLOAD")
    print("="*60)

    try:
        # Get file path
        print("\nPlease provide the full path to your PDF file")
        print("Example: C:\\Users\\YourName\\Documents\\book.pdf")
        print("         or /home/user/documents/book.pdf")
        print("\nType 'main' to return to main menu")
        print("="*60)

        file_path = input("\nEnter PDF file path: ").strip()

        if file_path.lower() == 'main':
            print("\nReturning to main menu...")
            return

        # Remove quotes if user included them
        file_path = file_path.strip('"').strip("'")

        # Validate file exists
        if not os.path.exists(file_path):
            print(f"\nError: File not found at '{file_path}'")
            input("\nPress Enter to return to main menu...")
            return

        # Validate it's a PDF
        if not file_path.lower().endswith('.pdf'):
            print("\nError: Only PDF files are supported")
            input("\nPress Enter to return to main menu...")
            return

        # Get book details
        print("\n" + "-"*60)
        book_title = input("Enter book title: ").strip()
        if not book_title:
            print("Book title is required")
            input("\nPress Enter to return to main menu...")
            return

        author = input("Enter author name (optional, press Enter to skip): ").strip()
        if not author:
            author = None

        print("\n" + "-"*60)
        print("\nStarting upload process...")
        print("This may take a few moments...\n")

        # Step 1: Upload to storage and create book record
        print("Step 1/3: Uploading file to storage...")
        book_service = BookProcessingService()

        # Read file content
        with open(file_path, 'rb') as f:
            file_content = f.read()

        filename = os.path.basename(file_path)

        # Upload using async function
        import asyncio
        asyncio.run(book_service.upload_pdf(
            file_content=file_content,
            filename=filename,
            user_id=user_profile.user_id,
            book_title=book_title,
            author=author
        ))

        print("File uploaded successfully!")

        # Step 2: Process PDF into chunks
        print("\nStep 2/3: Processing PDF and creating chunks...")
        docs = read_doc(file_path)
        chunked_docs = chunks(docs, chunk_size=400, chunk_overlap=50)
        print(f"Created {len(chunked_docs)} text chunks")

        # Step 3: Upload to Pinecone
        print("\nStep 3/3: Uploading vectors to Pinecone...")
        pinecone_service = PineconeService()
        namespace = f"user_{user_profile.user_id}"
        print(f"Using namespace: {namespace}")

        # Get embeddings and vectorstore
        vector_store = pinecone_service.get_vectorstore(namespace=namespace)
        vector_store.add_documents(chunked_docs)

        print("Vectors uploaded to Pinecone successfully!")

        # Success message
        print("\n" + "="*60)
        print("BOOK UPLOAD COMPLETE!")
        print("="*60)
        print(f"\nBook Title: {book_title}")
        if author:
            print(f"Author: {author}")
        print(f"Filename: {filename}")
        print(f"Chunks Created: {len(chunked_docs)}")
        print(f"Namespace: {namespace}")
        print("\nYou can now chat with this book!")
        print("="*60)

        input("\nPress Enter to return to main menu...")

    except Exception as e:
        print(f"\nError during upload: {str(e)}")
        print("\nPlease check:")
        print("  - File path is correct")
        print("  - File is a valid PDF")
        print("  - You have read permissions")
        print("  - Database and Pinecone connections are working")
        input("\nPress Enter to return to main menu...")


def main_menu_loop(user_profile: UserProfile):
    """
    Main menu loop - displays options and handles navigation

    Args:
        user_profile: Authenticated user profile
    """
    while True:
        try:
            display_main_menu()

            choice = input("\nEnter your choice (1-5): ").strip()

            if choice == '1':
                # Start/Continue Chat
                chat_session(user_profile)

            elif choice == '2':
                # View Chat History
                selected_chat_id = view_chat_history(user_profile)
                if selected_chat_id:
                    # User selected a chat, start chat session with that ID
                    chat_session(user_profile, chat_id=selected_chat_id)

            elif choice == '3':
                # View Profile
                view_profile(user_profile)

            elif choice == '4':
                # Upload Book
                upload_book(user_profile)

            elif choice == '5':
                # Exit
                print("\n" + "="*60)
                print("Thank you for using RAG Chat Backend!")
                print("See you next time!")
                print("="*60 + "\n")
                break

            else:
                print("\nInvalid choice. Please enter a number between 1 and 5.")
                input("Press Enter to continue...")

        except KeyboardInterrupt:
            print("\n\nExiting application...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Returning to main menu...")
            input("Press Enter to continue...")


def main():
    """
    Main application entry point
    """
    try:
        # Step 1: Login
        user_profile = login()

        if user_profile is None:
            print("\nLogin cancelled.")
            sys.exit(0)

        # Step 2: Main menu loop
        main_menu_loop(user_profile)

    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
