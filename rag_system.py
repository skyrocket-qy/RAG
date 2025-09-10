import os
from langchain_community.vectorstores import PGVector
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import LlamaCpp
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# --- Configuration ---

# Path to the LLaMA GGUF model
# UPDATE THIS PATH to point to your local LLaMA model file
LLAMA_MODEL_PATH = os.path.expanduser("~/Llama-3.1-8B-Instruct.Q4_K_M.gguf")

# PostgreSQL connection details (ensure these match your setup)
PG_CONNECTION_STRING = os.getenv("PG_CONNECTION_STRING", "postgresql://postgres:password@localhost:5432/postgres")
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
    if not os.path.exists(LLAMA_MODEL_PATH):
        print(f"Error: LLaMA model not found at {LLAMA_MODEL_PATH}.")
        print("Please update the LLAMA_MODEL_PATH variable in this script.")
    else:
        try:
            llm = initialize_llm()
            retriever = initialize_retriever()
            rag_chain = setup_rag_chain(llm, retriever)

            print("\n--- RAG System Ready ---")
            print("Type your query and press Enter. Type 'exit' to quit.")

            while True:
                query = input("\nQuery: ")
                if query.lower() == 'exit':
                    break

                print("Searching and generating...")
                result = rag_chain({"query": query})
                print("\nAnswer:")
                print(result["result"])
                print("\nSource Documents:")
                for doc in result["source_documents"]:
                    print(f"- {doc.metadata['source']}: {doc.page_content[:100]}...")

        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please ensure your PostgreSQL database is running and accessible.")

    print("Exiting RAG system.")
