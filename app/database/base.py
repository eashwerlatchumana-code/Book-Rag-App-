from supabase import create_client, Client
import os
from dotenv import load_dotenv
import httpx

load_dotenv()

def get_supabase():
    """
    Create and return Supabase client - simple version
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")

    if not url or not key:
        raise ValueError("Missing Supabase credentials in .env")

    # Create client with SSL disabled and long timeout
    http_client = httpx.Client(
        timeout=60.0,
        verify=False  # Disable SSL verification
    )

    client = create_client(url, key)
    client.postgrest.session = http_client

    return client

class BaseRepo:
    def __init__(self):
        self.client = get_supabase()