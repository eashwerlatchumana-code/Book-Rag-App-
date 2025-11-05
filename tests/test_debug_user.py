"""
Debug script to test user lookup
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.database.users_repo import UsersRepository

def test_user_lookup():
    """Test user lookup by name and email"""
    repo = UsersRepository()

    # First, let's see ALL users in the database
    print("\n" + "="*60)
    print("FETCHING ALL USERS FROM DATABASE")
    print("="*60)

    try:
        response = repo.client.table("user_table").select("*").execute()

        if response.data:
            print(f"\nFound {len(response.data)} users:")
            for i, user in enumerate(response.data, 1):
                print(f"\nUser {i}:")
                print(f"  user_id: {user.get('user_id')}")
                print(f"  name: {user.get('name')}")
                print(f"  email: {user.get('email')}")
                print(f"  created_at: {user.get('created_at')}")
        else:
            print("\nNo users found in database!")

    except Exception as e:
        print(f"\nError fetching all users: {e}")
        import traceback
        traceback.print_exc()

    # Now test the get_by_name method
    print("\n" + "="*60)
    print("TESTING get_by_name() METHOD")
    print("="*60)

    test_name = input("\nEnter a name to search for: ").strip()

    if test_name:
        print(f"\nSearching for user with name: '{test_name}'")
        result = repo.get_by_name(test_name)

        if result:
            print("\n✓ FOUND USER:")
            print(f"  user_id: {result.get('user_id')}")
            print(f"  name: {result.get('name')}")
            print(f"  email: {result.get('email')}")
            print(f"  created_at: {result.get('created_at')}")
        else:
            print("\n✗ NO USER FOUND")
            print("\nPossible reasons:")
            print("  1. Name doesn't exist in database")
            print("  2. Name has different capitalization")
            print("  3. Name has extra spaces")

    # Test get_by_email method
    print("\n" + "="*60)
    print("TESTING get_by_email() METHOD")
    print("="*60)

    test_email = input("\nEnter an email to search for: ").strip()

    if test_email:
        print(f"\nSearching for user with email: '{test_email}'")
        result = repo.get_by_email(test_email)

        if result:
            print("\n✓ FOUND USER:")
            print(f"  user_id: {result.get('user_id')}")
            print(f"  name: {result.get('name')}")
            print(f"  email: {result.get('email')}")
            print(f"  created_at: {result.get('created_at')}")
        else:
            print("\n✗ NO USER FOUND")
            print("\nPossible reasons:")
            print("  1. Email doesn't exist in database")
            print("  2. Email has different capitalization")
            print("  3. Email has extra spaces")

if __name__ == "__main__":
    test_user_lookup()
