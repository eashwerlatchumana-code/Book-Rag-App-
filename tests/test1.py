import sys
import os
#Testing if the book actualy gets uploaded
# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.database.books_repo import BooksRepository

db = BooksRepository()
db.create_book(user_id="2f6413bb-f672-46ec-aeba-815020615d30",filename="test.py", author="Eashwer", book_title="test book")