import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import PGVector
from langchain_community.embeddings import HuggingFaceEmbeddings

# This script embeds a codebase into a PostgreSQL vector database for a RAG system.
# It loads documents, splits them into chunks, generates embeddings, and stores them.

# Path to the cloned repository
REPO_PATH = "./repo"

# Define file types to load
file_types = {
    ".py": "python",
    ".js": "js",
    ".ts": "ts",
    ".jsx": "jsx",
    ".tsx": "tsx",
    ".html": "html",
    ".css": "css",
    
    ".md": "markdown",
    ".txt": "text",
    ".go": "go",
    ".yml": "yaml",
}

def load_documents(repo_path, file_types):
    documents = []
    for ext, loader_type in file_types.items():
        loader = DirectoryLoader(
            repo_path,
            glob=f"**/*{ext}",
            show_progress=True,
            use_multithreading=True
        )
        print(f"Loading {ext} files...")
        documents.extend(loader.load())

    # Load Dockerfile separately as plain text
    dockerfile_loader = DirectoryLoader(
        repo_path,
        glob="**/Dockerfile",
        loader_cls=TextLoader,
        show_progress=True,
        use_multithreading=True
    )
    print("Loading Dockerfile files...")
    documents.extend(dockerfile_loader.load())

    # Load .mod files separately as plain text
    mod_loader = DirectoryLoader(
        repo_path,
        glob="**/*.mod",
        loader_cls=TextLoader,
        show_progress=True,
        use_multithreading=True
    )
    print("Loading .mod files...")
    documents.extend(mod_loader.load())

    return documents

def embed_and_store(documents):
    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # PostgreSQL connection string and collection name from environment variables
    connection_string = os.getenv("PG_CONNECTION_STRING")
    collection_name = os.getenv("PG_COLLECTION_NAME", "rag_embedding")

    if not connection_string:
        print("Error: PG_CONNECTION_STRING environment variable not set.")
        return

    # Create and persist the vector store in PostgreSQL
    print(f"Creating PGVector store in PostgreSQL for collection: {collection_name}...")
    try:
        vectordb = PGVector.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name=collection_name,
            connection_string=connection_string,
            # This will delete the collection if it already exists, ensuring a fresh start.
            pre_delete_collection=True
        )
        print("PGVector store created and data inserted successfully.")
    except Exception as e:
        print(f"Error creating PGVector store: {e}")

if __name__ == "__main__":
    # Check for required environment variables
    if not os.getenv("PG_CONNECTION_STRING"):
        print("Error: The PG_CONNECTION_STRING environment variable is not set.")
        print("Please set it to your PostgreSQL connection string.")
        print("Example: export PG_CONNECTION_STRING=\"postgresql://user:password@host:port/dbname\"")
    elif not os.path.exists(REPO_PATH):
        print(f"Error: Repository not found at {REPO_PATH}.")
        print("Please make sure the code you want to embed is in the './repo' directory.")
    else:
        print(f"Loading documents from {REPO_PATH}...")
        documents = load_documents(REPO_PATH, file_types)
        if documents:
            embed_and_store(documents)
        else:
            print("No documents found to process.")
