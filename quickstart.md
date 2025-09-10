# Quickstart: RAG Code Embedding Project

This guide provides end-to-end instructions for setting up and running the RAG (Retrieval Augmented Generation) system on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

*   **Python 3.x**: [Download Python](https://www.python.org/downloads/)
*   **Docker**: [Install Docker](https://docs.docker.com/get-docker/) (for running PostgreSQL)
*   **Git**: [Install Git](https://git-scm.com/downloads)
*   **Homebrew (macOS only)**: [Install Homebrew](https://brew.sh/) (for `libmagic` and `cmake`)

## Setup

### 1. Clone the Repository

Clone this repository to your local machine:

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Place Your Codebase

The system is designed to embed the code located in the `repo` directory. Make sure the codebase you want to query is placed there.

```bash
# Example: Clone a repository into the `repo` directory
git clone https://github.com/your-org/your-project.git repo
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

On macOS, you may also need to install `libmagic` and `cmake`:

```bash
brew install libmagic cmake
```

### 4. Set Up PostgreSQL with `pgvector`

We use Docker to run a PostgreSQL database with the `pgvector` extension.

First, stop and remove any existing `postgres` Docker containers to avoid conflicts:

```bash
docker stop postgres && docker rm postgres
```

Then, start a new container:

```bash
docker run -d --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=password pgvector/pgvector:pg17
```

This command starts a PostgreSQL 17.x container, accessible on `localhost:5432` with user `postgres` and password `password`.

### 5. Download and Convert the LLaMA Model

The RAG system uses a local LLaMA model in GGUF format.

**a. Log in to Hugging Face:**

To download the model, you need to be authenticated with Hugging Face. Run the following command and enter your Hugging Face token when prompted:

```bash
huggingface-cli login
```

**b. Download the Model:**

Download a LLaMA model from HuggingFace. We recommend the `Llama-3.1-8B-Instruct` model.

```bash
git clone https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct ~/Llama-3.1-8B-Instruct
```

**b. Convert the Model to GGUF:**

Use the provided `convert_llama.sh` script to convert the downloaded model to the GGUF format, which is optimized for CPU inference with `llama.cpp`.

First, make the script executable:

```bash
chmod +x convert_llama.sh
```

Then, run the script. It will clone `llama.cpp`, build it, and perform the conversion.

```bash
./convert_llama.sh
```

This script will place the converted model (e.g., `Llama.gguf`) in your home directory. You may need to adjust the paths in `convert_llama.sh` and `rag_system.py` if you change the locations.

## Running the System

### Step 1: Embed Your Codebase

Run the `embed.py` script to process your codebase and store the embeddings in the PostgreSQL database.

Make sure to set the connection string environment variable first:

```bash
export PG_CONNECTION_STRING="postgresql://postgres:password@localhost:5432/postgres"
```

Now, run the script:

```bash
python embed.py
```

This process may take a few minutes, depending on the size of your codebase.

### Step 2: Run the RAG System

Once the embedding process is complete, you can start the RAG system to ask questions about your code.

Ensure the `LLAMA_MODEL_PATH` in `rag_system.py` points to your converted GGUF model file.

Run the script:

```bash
python rag_system.py
```

The system will load the model and connect to the database. Once you see the "RAG System Ready" message, you can type your queries and get answers based on your codebase.

To exit the system, type `exit`.
