# Enterprise RAG System

A Retrieval-Augmented Generation (RAG) system for processing and querying PDF documents, built with FastAPI and PyTorch.

## Features

- PDF document processing
- Advanced text embeddings using sentence-transformers
- Vector storage with ChromaDB
- Real-time query processing
- Web interface for document upload and querying
- Docker containerization

## Tech Stack

- FastAPI
- PyTorch
- Sentence Transformers
- ChromaDB
- Docker
- TailwindCSS

## Getting Started

### Prerequisites

- Docker
- Docker Compose
- Python 3.9+

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your# Initialize Git

git init

# Add all files

git add .

# Create initial commit

git commit -m "Initial commit: Enterprise RAG System"

# Add GitHub remote (replace with your repository URL)

git remote add origin https://github.com/ThinkShiftGIT/enterprise-rag.git

# Push to GitHub

git push -u origin main/enterprise-rag.git
cd enterprise-rag
```

2. Create necessary directories:
```bash
mkdir -p data/documents data/vector_store logs
```

3. Build and run with Docker:
```bash
docker-compose up --build
```

4. Access the web interface:
```
http://localhost:8000
```

## Usage

1. Upload a PDF document using the web interface
2. Wait for processing to complete
3. Use the query interface to ask questions about the document
4. View results with relevant document sections

## Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run in development mode:
```bash
uvicorn src.enterprise_rag.api.main:app --reload
```

## Project Structure

```
enterprise_rag/
├── src/
│   └── enterprise_rag/
│       ├── core/
│       │   ├── document_processor.py
│       │   ├── embedding_service.py
│       │   ├── vector_store.py
│       │   └── rag_engine.py
│       └── api/
│           └── main.py
├── templates/
│   └── index.html
├── data/
│   ├── documents/
│   └── vector_store/
└── docker-compose.yml
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.