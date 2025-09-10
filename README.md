# MemZ: A Distributed Authorization System with RAG-Powered Code Querying

This repository contains two main components:

1.  **MemZ**: A high-performance, distributed authorization system inspired by Google's Zanzibar.
2.  **RAG System**: A Retrieval Augmented Generation (RAG) system that allows you to query the `MemZ` codebase using natural language.

---

## 1. MemZ: Distributed Authorization System

<p align="center">
  <img src="repo/docs/architecture.png" alt="MemZ Architecture" width="600">
</p>

<p align="center">
  <strong>A distributed, memory-first authorization system inspired by <a href="https://research.google/pubs/zanzibar-googles-consistent-global-authorization-system/">Zanzibar</a>.</strong>
</p>

<p align="center">
  <a href="https://github.com/skyrocket-qy/authz/actions/workflows/ci.yml"><img src="https://github.com/skyrocket-qy/authz/actions/workflows/ci.yml/badge.svg" alt="Build Status"></a>
  <a href="#"><img src="https://img.shields.io/badge/coverage-73.3%25-brightgreen" alt="Coverage"></a>
  <a href="https://github.com/skyrocket-qy/authz/releases"><img src="https://img.shields.io/github/v/release/skyrocket-qy/authz.svg" alt="Release"></a>
</p>

`MemZ` is a high-performance, distributed authorization system designed for read-heavy workloads. It prioritizes in-memory evaluation to achieve low latency and high throughput, making it suitable for applications that require fast and reliable access control checks.

### ✨ Features

- **High Performance**: Optimized for read-heavy workloads with in-memory evaluation (p95 latency < 10ms).
- **High Availability**: Distributed architecture with eventual consistency.
- **Scalable**: Designed to scale horizontally to handle a growing number of requests.
- **Flexible Authorization Models**: Supports RBAC, Hierarchical Relations, ABAC, and more.

### 🏛️ Architecture

`MemZ` consists of a central database (source of truth), a Kafka message queue, and a cluster of authorization replicas. This architecture ensures high availability and low latency. For more details, see the [architecture diagram](repo/docs/architecture.png).

### 🚀 Getting Started with MemZ

To get started with `MemZ`, you'll need:

- **Go**: Version 1.25 or higher.
- **Docker**: To run the required services.

**1. Clone the Repository:**
```bash
git clone https://github.com/skyrocket-qy/authz.git
cd authz
```

**2. Start Required Services:**
`MemZ` requires a PostgreSQL database and a Redis instance.
```bash
make pg
make redis
```

**3. Run the Application:**
```bash
cd repo
go run .
```
The server will start on port `8080`.

---

## 2. RAG System for Codebase Querying

This project includes a Python-based RAG system to enable intelligent querying of the `MemZ` codebase.

### 🛠️ Technologies Used

*   **LangChain**: For orchestrating the RAG pipeline.
*   **HuggingFace Embeddings**: Using the `all-MiniLM-L6-v2` model.
*   **PostgreSQL with `pgvector`**: As the vector database.
*   **LLaMA 3.1-8B (GGUF)**: For generating natural language responses.

### 🚀 Getting Started with the RAG System

**Prerequisites:**

*   **Python 3.x**
*   **Docker**
*   **Homebrew (macOS only)**: For `libmagic`, `llama.cpp`, `cmake`.

**1. Install Python Dependencies:**
```bash
pip install -r requirements.txt
```

**2. Start PostgreSQL with `pgvector`:**
```bash
make pg
```

**3. Set Environment Variables:**
```bash
export PG_CONNECTION_STRING="postgresql://postgres:password@localhost:5432/postgres"
export PG_COLLECTION_NAME="rag_embedding"
```

**4. Download and Convert LLaMA Model:**
A script is provided to download and convert the LLaMA model to GGUF format.
```bash
bash convert_llama.sh
```

**5. Embed the Codebase:**
This script will embed the code from the `./repo` directory into the vector database.
```bash
python embed.py
```

**6. Run the RAG System:**
Start the interactive RAG system to ask questions about the codebase.
```bash
python rag_system.py
```

### 💖 Contributing

We welcome contributions! Please fork the repository, make your changes, and submit a pull request.

### 🚀 Performance

The following benchmarks were run on a MacBook Pro with an i7-9750H CPU @ 2.60GHz but limit in docker container with 8 cpus and 12g memory. The tests were run for 30 seconds with a total of 110,000 tuples.

```yaml
roles     = 10000
resources = 1000
users     = 100000
permission = "read"
total tuples = 110000
```

#### Check once
latency: 792us
handler time: 28us

#### Soak test

| Virtual Users (VUs) | Requests per Second (RPS) | Med Latency     | p95 Latency |
| ------------------- | ------------------------- | --------------- | ----------- |
| 10                  | 4,277                     | 2ms             | 3.99ms      |
| 50                  | 5,834                     | 6.37ms          | 21.91ms     |
| 200                 | 5,606                     | 29.45ms         | 86.46ms     |
| 500                 | 5,148                     | 73.24ms         | 257.07ms    |

#### Load test

| Requests per Second (RPS) | Med Latency     | p95 Latency |
| ------------------------- | ------------    | ----------- |
| 50                        | 1.35ms          | 2.3ms       |
| 200                       | 1.07ms          | 1.88ms      |
| 500                       | 948us           | 2.52ms      |
| 2000                      | 940us           | 3.37ms      |
| 4000                      | 1.9ms           | 52.78ms     |

### ❗ Limitations

- **Eventual Consistency**: `MemZ` is eventually consistent.
- **Static Policy Model**: Does not support dynamic policy models.
- **Memory Footprint**: ~10 GB per 100 million tuples for `MemZ`.
- **Write Performance**: `MemZ` is not optimized for write-heavy workloads.
