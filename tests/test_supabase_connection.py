"""
Test Supabase connection and user creation/retrieval
"""
import sys
import os
# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.database.users_repo import UsersRepository
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_supabase_connection():
    """Test basic Supabase connection"""
    print("Testing Supabase connection...")

    try:
        # Test connection by creating repo
        users_repo = UsersRepository()
        print("[PASS] Successfully connected to Supabase")
        return True
    except Exception as e:
        print(f"[FAIL] Failed to connect to Supabase: {e}")
        return False

def test_user_retrieval():
    """Test retrieving users from database"""
    print("\nTesting user retrieval...")

    try:
        users_repo = UsersRepository()

        # Try to get all users (we'll query for any email pattern)
        response = users_repo.client.table("user_table").select("*").execute()

        if response.data:
            print(f"[PASS] Found {len(response.data)} user(s) in database")
            for user in response.data[:3]:  # Show first 3 users
                print(f"  - {user.get('name')} ({user.get('email')})")
        else:
            print("[PASS] Connected but no users found in database")

        return True
    except Exception as e:
        print(f"[FAIL] Failed to retrieve users: {e}")
        return False

def test_create_and_retrieve_user():
    """Test creating a user and then retrieving it"""
    print("\nTesting user creation and retrieval...")

    try:
        users_repo = UsersRepository()

        # Create a test user
        test_email = "test_user_123@example.com"
        test_name = "Test User 123"

        # First check if user already exists
        existing = users_repo.get_by_email(test_email)
        if existing:
            print(f"[PASS] Test user already exists: {existing.get('name')} ({existing.get('email')})")
            print(f"  User ID: {existing.get('user_id')}")
            return True

        # Create user
        print(f"Creating test user: {test_name} ({test_email})")
        response = users_repo.create_user(email=test_email, name=test_name)

        if response and response.data:
            print("[PASS] User created successfully")
            created_user = response.data[0]
            print(f"  User ID: {created_user.get('user_id')}")
            print(f"  Name: {created_user.get('name')}")
            print(f"  Email: {created_user.get('email')}")

            # Now try to retrieve the user
            print("\nRetrieving user by email...")
            retrieved = users_repo.get_by_email(test_email)

            if retrieved:
                print("[PASS] Successfully retrieved user after creation")
                print(f"  Name: {retrieved.get('name')}")
                print(f"  Email: {retrieved.get('email')}")
                print(f"  User ID: {retrieved.get('user_id')}")
                return True
            else:
                print("[FAIL] Failed to retrieve user after creation!")
                return False
        else:
            print(f"[FAIL] Failed to create user: {response}")
            return False

    except Exception as e:
        print(f"[FAIL] Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*60)
    print("SUPABASE CONNECTION TEST")
    print("="*60)

    results = []

    # Test 1: Connection
    results.append(("Connection", test_supabase_connection()))

    # Test 2: Retrieval
    results.append(("Retrieval", test_user_retrieval()))

    # Test 3: Create and Retrieve
    results.append(("Create & Retrieve", test_create_and_retrieve_user()))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")

    all_passed = all(result for _, result in results)
    print("\n" + "="*60)
    if all_passed:
        print("All tests PASSED")
    else:
        print("Some tests FAILED")
    print("="*60)

if __name__ == "__main__":
    main()
