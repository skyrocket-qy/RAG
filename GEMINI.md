# Project Overview

This is a Python-based Retrieval Augmented Generation (RAG) project designed to enable intelligent querying of a codebase. It integrates several key technologies to achieve this:

*   **LangChain**: Used for orchestrating the various components of the RAG pipeline.
*   **HuggingFace Embeddings**: Utilizes the `all-MiniLM-L6-v2` model for generating semantic embeddings of code snippets.
*   **PostgreSQL with `pgvector`**: Serves as the vector database to store and efficiently retrieve document embeddings.
*   **LLaMA 3.1-8B (GGUF)**: Employs the LLaMA 3.1-8B model (converted to the GGUF format using `llama.cpp`) for generating natural language responses based on retrieved code context.

The primary goal of this project is to allow users to ask questions about their codebase in natural language and receive answers informed by the actual code, facilitating code understanding and development.

# Building and Running

Follow these steps to set up, build, and run the RAG system:

## Prerequisites

*   **Python 3.x**: Ensure Python 3 is installed.
*   **Docker**: Required for running the PostgreSQL database.
*   **Homebrew (macOS only)**: Recommended for installing `libmagic`, `llama.cpp`, and `cmake`.

## Setup

1.  **Clone or Place Codebase**:
    Ensure the codebase you wish to embed is located in a directory named `repo` at the root of this project.

2.  **Install Python Dependencies**:
    Navigate to the project root directory (`/Users/qy/skyro/RAG/`) and install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Start PostgreSQL with `pgvector`**:
    Use the provided Makefile command to start a PostgreSQL container with the `pgvector` extension:
    ```bash
    make pg
    ```
    This will start a PostgreSQL 17.x container with `pgvector` pre-installed, accessible on `localhost:5432` with user `postgres` and password `password`.

4.  **Set PostgreSQL Connection String**:
    Set the necessary environment variables for PostgreSQL connection:
    ```bash
    export PG_CONNECTION_STRING="postgresql://postgres:password@localhost:5432/postgres"
    export PG_COLLECTION_NAME="rag_embedding" # Default collection name
    ```

5.  **Install `libmagic` (Recommended for macOS/Linux)**:
    `libmagic` assists with accurate file type detection during embedding.
    *   For macOS: `brew install libmagic`
    *   For Debian/Ubuntu: `sudo apt-get update && sudo apt-get install libmagic-dev`

## Model Conversion

1.  **Download LLaMA PyTorch Model**:
    Ensure your LLaMA 3.1-8B PyTorch model files are located at `$HOME/.llama/checkpoints/Llama3.1-8B`.

2.  **Convert Model to GGUF**:
    Run the conversion script to transform your PyTorch model into the GGUF format, which is optimized for `llama.cpp` and CPU performance:
    ```bash
    bash convert_llama.sh
    ```
    This script will clone/update `llama.cpp`, install its dependencies, build necessary binaries, and perform a two-step conversion (FP16 then quantized to Q4_K_M). The final GGUF model will be saved in your home directory (e.g., `~/Llama3.1-8B.Q4_K_M.gguf`).

## Embed Codebase

Once PostgreSQL is running and the model is converted, embed your codebase into the vector database:
```bash
python embed.py
```
This script will load documents from the `./repo` directory, split them, generate embeddings, and store them in your PostgreSQL database.

## Run RAG System

After embedding your codebase, you can start the interactive RAG system:
```bash
python rag_system.py
```
The system will load the GGUF model and initialize the retriever. You can then type your queries to get answers based on your embedded codebase.

# Development Conventions

*   **Python**: The primary language for the RAG system and embedding scripts.
*   **Dependency Management**: `pip` and `requirements.txt` are used for managing Python dependencies.
*   **Build Automation**: A `Makefile` is provided for common tasks like starting the PostgreSQL Docker container and freezing dependencies.
*   **Version Control**: `git` is used for source code management.
