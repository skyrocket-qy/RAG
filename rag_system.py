import os
from langchain_community.vectorstores import PGVector
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import LlamaCpp
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# --- Configuration ---

# Path to the LLaMA GGUF model, fetched from an environment variable
LLAMA_MODEL_PATH = "/home/qy/Llama.gguf"

# PostgreSQL connection details, fetched from environment variables
PG_CONNECTION_STRING = "postgresql://postgres:password@localhost:5432/rag_embedding"
PG_COLLECTION_NAME = os.getenv("PG_COLLECTION_NAME", "rag_embedding")

# Embedding model for retrieval (must match the one used in embed.py)
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Number of relevant documents to retrieve
K_RETRIEVED_DOCUMENTS = 4

# --- Initialize Components ---

def initialize_llm():
    """Initializes the LLaMA language model."""
    print(f"Loading LLaMA GGUF model from {LLAMA_MODEL_PATH}...")
    llm = LlamaCpp(
        model_path=LLAMA_MODEL_PATH,
        temperature=0.7,
        max_tokens=2000,
        top_p=1,
        n_ctx=2048,  # Context window size
        verbose=False,
    )
    return llm

def initialize_retriever():
    """Initializes the retriever for the vector store."""
    print(f"Initializing retriever for collection: {PG_COLLECTION_NAME}...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    
    vectorstore = PGVector(
        collection_name=PG_COLLECTION_NAME,
        connection_string=PG_CONNECTION_STRING,
        embedding_function=embeddings,
    )
    return vectorstore.as_retriever(search_kwargs={"k": K_RETRIEVED_DOCUMENTS})

def setup_rag_chain(llm, retriever):
    """Sets up the RAG chain with a prompt template."""
    print("Setting up RAG chain...")
    template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}
Helpful Answer:"""
    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

    qa_chain = RetrievalQA.from_chain_type(
        llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
    )
    return qa_chain

# --- Main Execution ---

if __name__ == "__main__":
    # --- Pre-flight Checks ---
    if not LLAMA_MODEL_PATH:
        print("Error: The LLAMA_MODEL_PATH environment variable is not set.")
        print("Please set it to the path of your LLaMA GGUF model file.")
        print("Example: export LLAMA_MODEL_PATH=\"/path/to/your/model.gguf\"")
    elif not os.path.exists(LLAMA_MODEL_PATH):
        print(f"Error: LLaMA model not found at the specified path: {LLAMA_MODEL_PATH}")
        print("Please ensure the path is correct and the file exists.")
    elif not PG_CONNECTION_STRING:
        print("Error: The PG_CONNECTION_STRING environment variable is not set.")
        print("Please set it to your PostgreSQL connection string.")
        print("Example: export PG_CONNECTION_STRING=\"postgresql://user:password@host:port/dbname\"")
    else:
        try:
            # --- Initialization ---
            llm = initialize_llm()
            retriever = initialize_retriever()
            rag_chain = setup_rag_chain(llm, retriever)

            print("\n--- RAG System Ready ---")
            print("Type your query and press Enter. Type 'exit' to quit.")

            # --- Interactive Query Loop ---
            while True:
                query = input("\nQuery: ")
                if query.lower() == 'exit':
                    break

                if not query.strip():
                    continue

                print("Searching and generating...")
                try:
                    result = rag_chain({"query": query})
                    print("\nAnswer:")
                    print(result["result"])
                    print("\n--- Source Documents ---")
                    for doc in result["source_documents"]:
                        source = doc.metadata.get('source', 'Unknown')
                        content_preview = doc.page_content[:120].replace('\n', ' ') + "..."
                        print(f"- {source}: \"{content_preview}\"")

                except Exception as e:
                    print(f"\nAn error occurred while processing your query: {e}")

        except Exception as e:
            print(f"\nAn error occurred during initialization: {e}")
            print("Please ensure your PostgreSQL database is running and accessible,")
            print("and that the embedding model name is correct.")

    print("\nExiting RAG system.")
