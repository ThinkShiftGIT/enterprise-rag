import sys
from pathlib import Path
import asyncio
from typing import List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add src to Python path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from enterprise_rag.core.document_processor import DocumentProcessor
from enterprise_rag.core.embedding_service import EmbeddingService
from enterprise_rag.core.vector_store import VectorStore
from enterprise_rag.core.rag_engine import RAGEngine

console = Console()

def display_results(results: Dict[str, Any]):
    """Display results in a formatted way"""
    console.print("\n")
    console.print(Panel(results['summary'], title="📊 Summary", border_style="blue"))
    
    for category, category_results in results['categories'].items():
        console.print(f"\n[bold blue]📑 {category}[/bold blue]")
        console.print("=" * (len(category) + 4))
        
        for idx, result in enumerate(category_results, 1):
            confidence_color = "green" if float(result['confidence'].strip('%')) > 70 else "yellow"
            
            content_panel = Panel(
                f"[bold]{result['confidence']}[/bold] confidence\n\n"
                f"{result['content']}\n\n"
                f"[bold]Key Points:[/bold]",
                title=f"Finding {idx}",
                border_style=confidence_color
            )
            console.print(content_panel)
            
            for point in result['key_points']:
                console.print(f"[{confidence_color}]•[/{confidence_color}] {point}")
            
            console.print("\n" + "-" * 80 + "\n")

async def test_queries(rag_engine: RAGEngine):
    """Test various queries"""
    test_queries = [
        "What are the safety protocols for radiation exposure?",
        "What training is required for radiation safety?",
        "What are the emergency procedures for radiation incidents?",
        "What are the monitoring requirements for radiation safety?",
        "What protective equipment is required for radiation work?",
        "What are the radiation dose limits?",
        "How should radioactive materials be transported?",
        "What are the requirements for radiation safety officers?"
    ]
    
    for query in test_queries:
        console.print(f"\n[bold green]🔍 Query:[/bold green] {query}")
        results = await rag_engine.process_query(query, top_k=5)
        display_results(results)
        console.print("\n" + "=" * 80)

async def test_pdf_processing():
    """Main test function for the RAG system"""
    # Define paths
    pdf_path = Path("data/documents/Radiation.pdf")
    
    if not pdf_path.exists():
        console.print(f"[red]❌ PDF file not found at {pdf_path}[/red]")
        console.print("\nPlease ensure Radiation.pdf is in the data/documents directory")
        return False

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            # Initialize components
            progress.add_task(description="Initializing components...", total=None)
            doc_processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
            embedding_service = EmbeddingService()
            vector_store = VectorStore(
                collection_name="radiation_docs",
                persist_directory="data/vector_store"
            )
            rag_engine = RAGEngine(embedding_service, vector_store)

            # Process document
            task_id = progress.add_task(description="Processing PDF...", total=None)
            chunks = doc_processor.process_document(str(pdf_path))
            progress.update(task_id, description=f"✅ Document processed into {len(chunks)} chunks")
            
            # Show chunk samples
            console.print("\n[bold]📄 Document Chunks Sample:[/bold]")
            for i in range(min(3, len(chunks))):
                console.print(Panel(
                    chunks[i]["text"][:200] + "...",
                    title=f"Chunk {i+1}",
                    border_style="blue"
                ))
                console.print(f"Metadata: {chunks[i]['metadata']}\n")
            
            # Generate embeddings
            task_id = progress.add_task(description="Generating embeddings...", total=None)
            texts = [chunk["text"] for chunk in chunks]
            embeddings = embedding_service.generate_embeddings(texts)
            progress.update(task_id, description=f"✅ Generated embeddings of shape {embeddings.shape}")

            # Store in vector database
            task_id = progress.add_task(description="Storing in vector database...", total=None)
            vector_store.add_documents(chunks, embeddings)
            progress.update(task_id, description="✅ Documents stored successfully")

            # Run test queries
            console.print("\n[bold blue]🚀 Starting Query Tests[/bold blue]")
            await test_queries(rag_engine)

        return True

    except Exception as e:
        console.print(f"\n[red]❌ Error during processing:[/red] {str(e)}")
        console.print("\n[yellow]Full error trace:[/yellow]")
        import traceback
        console.print(traceback.format_exc())
        return False

def verify_setup():
    """Verify system setup and requirements"""
    try:
        # Check required directories
        for dir_path in ["data/documents", "data/vector_store", "logs"]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            console.print(f"✅ Verified directory: {dir_path}")
        
        # Check PDF file
        pdf_path = Path("data/documents/Radiation.pdf")
        if not pdf_path.exists():
            console.print("[yellow]⚠️  Warning: Radiation.pdf not found in data/documents/[/yellow]")
            console.print("Please copy your PDF file to this location before running tests.")
        else:
            console.print("✅ Found Radiation.pdf")
        
        return True
    except Exception as e:
        console.print(f"[red]❌ Setup verification failed:[/red] {str(e)}")
        return False

if __name__ == "__main__":
    console.print("\n[bold]🚀 Enterprise RAG System Test[/bold]")
    console.print("=" * 50)
    
    if verify_setup():
        asyncio.run(test_pdf_processing())
    else:
        console.print("\n[red]Setup verification failed. Please fix the issues above and try again.[/red]")