import os
import sys
from pathlib import Path

def create_file(file_path: Path, content: str):
    """Create or update a file with given content"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"✅ Updated {file_path}")

def verify_and_fix_files():
    base_dir = Path.cwd()
    src_dir = base_dir / "src"
    
    # Step 1: Create package structure
    print("\n📁 Creating package structure...")
    package_dirs = [
        src_dir,
        src_dir / "enterprise_rag",
        src_dir / "enterprise_rag" / "core",
        src_dir / "enterprise_rag" / "api",
        src_dir / "enterprise_rag" / "api" / "routes",
        src_dir / "enterprise_rag" / "schemas",
        src_dir / "enterprise_rag" / "utils",
        base_dir / "data" / "vector_store",
        base_dir / "logs",
    ]
    
    for dir_path in package_dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        init_file = dir_path / "__init__.py"
        if not init_file.exists():
            create_file(init_file, "")
    
    # Step 2: Create/update core files
    print("\n📝 Creating/updating core files...")
    
    # exceptions.py
    create_file(src_dir / "enterprise_rag" / "exceptions.py", """
class RAGException(Exception):
    def __init__(self, message: str, error_code: str, status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)

class DocumentProcessingError(RAGException):
    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_code="DOC_PROCESSING_ERROR",
            status_code=400
        )

class EmbeddingGenerationError(RAGException):
    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_code="EMBEDDING_ERROR",
            status_code=500
        )
""")

    # document_processor.py
    create_file(src_dir / "enterprise_rag" / "core" / "document_processor.py", """
from typing import List, Dict, Any
from pathlib import Path
from ..exceptions import DocumentProcessingError

class DocumentProcessor:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.supported_formats = {'.pdf', '.txt', '.docx'}

    def process_document(self, file_path: str) -> List[Dict[str, Any]]:
        try:
            # Basic implementation for testing
            return [{"text": "Test chunk", "metadata": {"source": file_path}}]
        except Exception as e:
            raise DocumentProcessingError(str(e))
""")

    # Update root __init__.py
    create_file(src_dir / "enterprise_rag" / "__init__.py", """
from .exceptions import DocumentProcessingError, EmbeddingGenerationError
from .core.document_processor import DocumentProcessor

__version__ = "1.0.0"
""")

    # Update test_setup.py
    create_file(base_dir / "test_setup.py", """
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
""")

    # Create/update pyproject.toml
    create_file(base_dir / "pyproject.toml", """
[build-system]
requires = ["setuptools>=45", "wheel", "pip>=21.0"]
build-backend = "setuptools.build_meta"

[project]
name = "enterprise-rag"
version = "1.0.0"
description = "Enterprise-grade RAG System"
requires-python = ">=3.9"

[tool.setuptools]
package-dir = {"" = "src"}
""")

    print("\n✨ Setup complete!")
    print("\nNext steps:")
    print("1. First, install the package in development mode:")
    print("   pip install -e .")
    print("2. Then run the test:")
    print("   python test_setup.py")

if __name__ == "__main__":
    verify_and_fix_files()