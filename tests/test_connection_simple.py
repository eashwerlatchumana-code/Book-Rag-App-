"""
Simple connection test with SSL workaround
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import httpx
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

def test_simple_connection():
    """Test direct HTTP connection to Supabase"""
    print("="*60)
    print("TESTING SUPABASE CONNECTION")
    print("="*60)
    print(f"\nURL: {SUPABASE_URL}")
    print(f"Key: {SUPABASE_KEY[:20]}...")

    # Test 1: Basic connectivity with httpx
    print("\n" + "-"*60)
    print("Test 1: Basic REST API connection")
    print("-"*60)

    try:
        # Create client with longer timeout and SSL verification disabled (for testing)
        client = httpx.Client(timeout=30.0, verify=False)

        response = client.get(
            f"{SUPABASE_URL}/rest/v1/user_table",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✓ SUCCESS! Found {len(data)} users")

            if data:
                print("\nUsers in database:")
                for i, user in enumerate(data, 1):
                    print(f"\n  User {i}:")
                    print(f"    Name: {user.get('name')}")
                    print(f"    Email: {user.get('email')}")
                    print(f"    ID: {user.get('user_id')}")
            else:
                print("\n⚠ Database is empty - no users found")
        else:
            print(f"✗ FAILED with status {response.status_code}")
            print(f"Response: {response.text}")

        client.close()

    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: Using Supabase client
    print("\n" + "-"*60)
    print("Test 2: Using Supabase Python client")
    print("-"*60)

    try:
        from supabase import create_client

        # Try with custom httpx client that has SSL disabled
        http_client = httpx.Client(timeout=30.0, verify=False)
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

        # Override the internal client
        supabase.postgrest.session = http_client

        response = supabase.table("user_table").select("*").execute()

        print(f"✓ SUCCESS! Found {len(response.data)} users")

        if response.data:
            print("\nUsers in database:")
            for i, user in enumerate(response.data, 1):
                print(f"\n  User {i}:")
                print(f"    Name: {user.get('name')}")
                print(f"    Email: {user.get('email')}")
                print(f"    ID: {user.get('user_id')}")
        else:
            print("\n⚠ Database is empty - no users found")

        http_client.close()

    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_connection()
