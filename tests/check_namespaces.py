"""
Script to check Pinecone index namespaces and statistics
"""
import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

def check_pinecone_namespaces():
    """Check what namespaces exist in the Pinecone index"""

    # Initialize Pinecone
    api_key = os.getenv("PINECONE_API_KEY")
    pc = Pinecone(api_key=api_key)

    # Get the index
    index_name = "langchaintest2"
    index = pc.Index(index_name)

    # Get index stats
    print("\n" + "="*60)
    print(" " * 15 + "PINECONE INDEX STATISTICS")
    print("="*60)
    print(f"\nIndex Name: {index_name}")

    try:
        # Describe index stats - this shows all namespaces
        stats = index.describe_index_stats()

        print(f"\nTotal Vectors: {stats.get('total_vector_count', 0)}")
        print(f"\nDimension: {stats.get('dimension', 'Unknown')}")

        # Get namespaces
        namespaces = stats.get('namespaces', {})

        if namespaces:
            print(f"\n{'='*60}")
            print(f"Found {len(namespaces)} namespace(s):")
            print(f"{'='*60}\n")

            for namespace_name, namespace_stats in namespaces.items():
                vector_count = namespace_stats.get('vector_count', 0)
                if namespace_name == "":
                    print(f"  - '' (default/empty namespace)")
                else:
                    print(f"  - '{namespace_name}'")
                print(f"    Vector count: {vector_count}")
                print()
        else:
            print("\n[WARNING] No namespaces found!")
            print("This could mean:")
            print("  - No data has been uploaded yet")
            print("  - All data is in the default namespace")

        print("="*60)

        # Check if there's data in the default namespace
        if '' in namespaces:
            default_count = namespaces[''].get('vector_count', 0)
            print(f"\n[INFO] Default namespace has {default_count} vectors")

        # List user namespaces
        user_namespaces = [ns for ns in namespaces.keys() if ns.startswith('user_')]
        if user_namespaces:
            print(f"\n[INFO] User-specific namespaces found:")
            for ns in user_namespaces:
                print(f"  - {ns}")
        else:
            print(f"\n[WARNING] No user-specific namespaces (user_*) found!")
            print("This suggests uploaded books may be going to the default namespace")

    except Exception as e:
        print(f"\n[ERROR] Failed to get index stats: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_pinecone_namespaces()
