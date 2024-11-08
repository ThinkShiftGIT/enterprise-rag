import os
import sys
from pathlib import Path

# Add src directory to Python path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_setup():
    try:
        # Test imports
        from enterprise_rag.core.document_processor import DocumentProcessor
        
        # Test document processor
        processor = DocumentProcessor()
        result = processor.process_document("test.txt")
        print("✅ Document processor test successful!")
        print(f"Result: {result}")
        return True
    except Exception as e:
        print(f"❌ Setup test failed: {str(e)}")
        print(f"Error details: {type(e).__name__}: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_setup()
    if not success:
        sys.exit(1)
