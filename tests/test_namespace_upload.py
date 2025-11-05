"""
Test script to verify that uploading documents creates the correct namespace
This simulates the upload process without actually uploading a file
"""
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from pinecone import Pinecone

load_dotenv()

def test_namespace_creation():
    """Test that creating a vectorstore with a namespace works correctly"""

    # Setup
    api_key = os.getenv("PINECONE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    index_name = "langchaintest2"
    test_namespace = "test_user_12345"

    print("\n" + "="*60)
    print(" " * 15 + "NAMESPACE CREATION TEST")
    print("="*60)
    print(f"\nTest namespace: {test_namespace}")

    # Step 1: Check current state
    print("\n[Step 1] Checking current namespaces...")
    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)
    stats_before = index.describe_index_stats()

    namespaces_before = list(stats_before.get('namespaces', {}).keys())
    print(f"Current namespaces: {namespaces_before if namespaces_before else ['(default)']}")

    # Step 2: Create vectorstore with namespace (exactly like in main.py)
    print("\n[Step 2] Creating PineconeVectorStore with namespace...")
    embeddings = OpenAIEmbeddings(api_key=openai_key)

    vector_store = PineconeVectorStore(
        index_name=index_name,
        embedding=embeddings,
        namespace=test_namespace,
        pinecone_api_key=api_key
    )
    print("[OK] VectorStore created")

    # Step 3: Add test documents (exactly like in main.py line 558)
    print("\n[Step 3] Adding test documents to namespace...")
    test_docs = [
        Document(page_content="This is a test document for namespace verification.",
                 metadata={"test": "true", "doc_num": 1}),
        Document(page_content="Second test document to ensure multiple docs work.",
                 metadata={"test": "true", "doc_num": 2})
    ]

    vector_store.add_documents(test_docs)
    print(f"[OK] Added {len(test_docs)} documents")

    # Step 4: Verify namespace was created
    print("\n[Step 4] Verifying namespace creation...")
    import time
    time.sleep(2)  # Give Pinecone a moment to index

    stats_after = index.describe_index_stats()
    namespaces_after = stats_after.get('namespaces', {})

    print("\n" + "="*60)
    print("RESULTS:")
    print("="*60)

    if test_namespace in namespaces_after:
        vector_count = namespaces_after[test_namespace].get('vector_count', 0)
        print(f"[SUCCESS] Namespace '{test_namespace}' was created")
        print(f"  Vector count: {vector_count}")
    else:
        print(f"[FAILED] Namespace '{test_namespace}' was NOT created")
        print(f"  Available namespaces: {list(namespaces_after.keys())}")

        # Check if vectors went to default namespace
        if '' in namespaces_after:
            default_before = stats_before.get('namespaces', {}).get('', {}).get('vector_count', 0)
            default_after = namespaces_after[''].get('vector_count', 0)
            if default_after > default_before:
                print(f"\n  WARNING: Vectors were added to DEFAULT namespace instead!")
                print(f"  Default namespace count increased from {default_before} to {default_after}")

    print("\n" + "="*60)

    # Step 5: Cleanup
    print("\n[Step 5] Cleaning up test data...")
    try:
        # Delete the test namespace vectors
        index.delete(delete_all=True, namespace=test_namespace)
        print(f"[OK] Cleaned up test namespace '{test_namespace}'")
    except Exception as e:
        print(f"Note: Could not clean up (namespace may not exist): {e}")

    print("\n" + "="*60)

if __name__ == "__main__":
    try:
        test_namespace_creation()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
