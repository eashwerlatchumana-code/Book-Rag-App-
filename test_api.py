"""
Quick test script to verify API endpoints are working
Run this after starting the server with: python main.py
"""
import requests
import sys

BASE_URL = "http://localhost:8000"

def test_root():
    """Test root endpoint"""
    print("Testing root endpoint (GET /)...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Root endpoint working - API version: {data['version']}")
            return True
        else:
            print(f"✗ Root endpoint failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_health():
    """Test health check endpoint"""
    print("\nTesting health endpoint (GET /health)...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health check passed - Status: {data['status']}")
            return True
        else:
            print(f"✗ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_docs():
    """Test documentation endpoint"""
    print("\nTesting docs endpoint (GET /docs)...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✓ Documentation endpoint accessible")
            return True
        else:
            print(f"✗ Docs endpoint failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("RAG Chat Backend API - Quick Test")
    print("="*60)
    print(f"\nTesting API at: {BASE_URL}")
    print("Make sure the server is running!\n")

    results = []
    results.append(test_root())
    results.append(test_health())
    results.append(test_docs())

    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✓ All tests passed! ({passed}/{total})")
        print("\nYour API is ready to use!")
        print(f"API Documentation: {BASE_URL}/docs")
        print(f"Alternative Docs: {BASE_URL}/redoc")
        return 0
    else:
        print(f"✗ Some tests failed ({passed}/{total} passed)")
        print("\nPlease check if the server is running:")
        print("  python main.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
