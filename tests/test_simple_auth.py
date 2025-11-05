"""
Simple test for authentication flow
"""
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.database.users_repo import UsersRepository

def test_auth_flow():
    """Test the complete auth flow"""
    print("Testing authentication flow...")
    print("="*60)

    # Initialize repo
    users_repo = UsersRepository()

    # Test user credentials
    test_email = "simple_test@example.com"
    test_name = "Simple Test User"

    print(f"\n1. Checking if user exists: {test_email}")
    existing = users_repo.get_by_email(test_email)

    if existing:
        print(f"   User found: {existing.get('name')}")
        user_id = existing.get('user_id')
    else:
        print(f"   User not found. Creating new user...")
        try:
            response = users_repo.create_user(email=test_email, name=test_name)
            if response and response.data:
                user_data = response.data[0]
                user_id = user_data.get('user_id')
                print(f"   User created successfully!")
                print(f"   User ID: {user_id}")
            else:
                print(f"   Failed to create user")
                return False
        except Exception as e:
            print(f"   Error creating user: {e}")
            return False

    print(f"\n2. Testing retrieval by email...")
    retrieved = users_repo.get_by_email(test_email)
    if retrieved:
        print(f"   SUCCESS: Retrieved user")
        print(f"   Name: {retrieved.get('name')}")
        print(f"   Email: {retrieved.get('email')}")
        print(f"   User ID: {retrieved.get('user_id')}")

        # Verify user_id matches
        if retrieved.get('user_id') == user_id:
            print(f"   User ID matches!")
        else:
            print(f"   ERROR: User ID mismatch!")
            return False
    else:
        print(f"   ERROR: Failed to retrieve user")
        return False

    print(f"\n3. Testing retrieval by name...")
    retrieved_by_name = users_repo.get_by_name(test_name)
    if retrieved_by_name:
        print(f"   SUCCESS: Retrieved user by name")
        print(f"   Name: {retrieved_by_name.get('name')}")
        print(f"   Email: {retrieved_by_name.get('email')}")
    else:
        print(f"   ERROR: Failed to retrieve user by name")
        return False

    print("\n" + "="*60)
    print("All tests PASSED!")
    print("="*60)
    return True

if __name__ == "__main__":
    try:
        success = test_auth_flow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
