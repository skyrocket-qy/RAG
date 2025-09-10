# RAG Code Embedding Project

This project provides a Python script to embed your codebase into a PostgreSQL vector database using LangChain and Sentence Transformers. This setup is ideal for building Retrieval Augmented Generation (RAG) systems that can query your code.

## Features

*   Loads various code file types (Python, JavaScript, TypeScript, Go, HTML, CSS, Markdown, Text, YAML, Dockerfiles, Go Modules).
*   Splits documents into manageable chunks for embedding.
*   Generates embeddings using the `all-MiniLM-L6-v2` Sentence Transformer model.
*   Stores embeddings in a PostgreSQL database with the `pgvector` extension.

## Prerequisites

Before you begin, ensure you have the following installed:

*   **Python 3.x**: [Download Python](https://www.python.org/downloads/)
*   **Docker**: [Install Docker](https://docs.docker.com/get-docker/) (for running PostgreSQL)
*   **Homebrew (macOS only)**: [Install Homebrew](https://brew.sh/) (for `libmagic`)

## Setup

1.  **Clone the Repository (or place your code):**
    Ensure the codebase you want to embed is located in a directory named `repo` at the root of this project. If your code is elsewhere, update the `REPO_PATH` variable in `embed.py`.

    ```bash
    # Example: If your Go project is in a different location
    # git clone https://github.com/your-org/your-go-project.git repo
    ```

2.  **Install Python Dependencies:**
    Navigate to the project root directory and install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

3.  **Start PostgreSQL with `pgvector`:**
    This project requires a PostgreSQL database with the `pgvector` extension enabled. We recommend using the `pgvector/pgvector` Docker image for easy setup.

    First, stop and remove any existing `postgres` Docker containers:

    ```bash
    docker stop postgres && docker rm postgres
    ```

    Then, start a new container:

    ```bash
    docker run -d --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=password pgvector/pgvector:pg17
    ```
    This will start a PostgreSQL 17.x container with `pgvector` pre-installed, accessible on `localhost:5432` with user `postgres` and password `password`.

4.  **Set PostgreSQL Connection String:**
    Set the `PG_CONNECTION_STRING` environment variable. This script uses the `rag_embedding` collection name by default.

    ```bash
    export PG_CONNECTION_STRING="postgresql://postgres:password@localhost:5432/postgres"
    # Optional: export PG_COLLECTION_NAME="my_custom_collection"
    ```

5.  **Install `libmagic` (Recommended for macOS/Linux):**
    `libmagic` helps with accurate file type detection.

    ```bash
    # For macOS:
    brew install libmagic
    brew install llama.cpp
    brew install cmake
    # For Debian/Ubuntu:
    # sudo apt-get update && sudo apt-get install libmagic-dev
    ```

## Usage

Run the embedding script from the project root directory:

```bash
python embed.py
```

The script will load your documents, split them into chunks, generate embeddings, and store them in the `rag_embedding` table (or your specified collection name) in your PostgreSQL database.

## Verification

To confirm that the embeddings have been successfully stored in your PostgreSQL database:

1.  **Connect to PostgreSQL:**
    ```bash
    psql "postgresql://postgres:password@localhost:5432/postgres"
    ```

2.  **List Tables:**
    Inside the `psql` prompt, list the tables to confirm `rag_embedding` exists:
    ```sql
    \dt
    ```

3.  **Count Entries:**
    Count the number of rows in the `rag_embedding` table:
    ```sql
    SELECT COUNT(*) FROM rag_embedding;
    ```

4.  **View Sample Data (Optional):**
    Inspect a few rows to see the stored embeddings and document content:
    ```sql
    SELECT * FROM rag_embedding LIMIT 5;
    ```

5.  **Exit `psql`:**
    ```sql
    \q
    ```

## Notes

*   **LangChain Deprecation Warning:** You might see a `LangChainDeprecationWarning` regarding `HuggingFaceEmbeddings`. This is a warning, not an error, and the script will still function. For future compatibility, you can update your `langchain` setup to use the new `langchain-huggingface` package as suggested in the warning.
*   **Customizing File Types:** If you have other file types in your repository that you wish to embed, you can add them to the `file_types` dictionary in `embed.py`. If `unstructured` struggles with a specific file type, consider loading it as plain text using `TextLoader` as demonstrated for Dockerfiles and Go module files.
