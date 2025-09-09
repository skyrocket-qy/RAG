import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from langchain_community.vectorstores import PGVector
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# --- Configuration ---

# Path to the LLaMA 3.1-8B model directory
# IMPORTANT: This assumes you have the PyTorch model files downloaded.
# Running an 8B model on CPU can be very slow. Consider converting to GGUF and using llama-cpp-python for better performance.
LLAMA_MODEL_PATH = os.path.expanduser("~/.llama/checkpoints/Llama3.1-8B")

# PostgreSQL connection details (from environment variables)
PG_CONNECTION_STRING = os.getenv("PG_CONNECTION_STRING", "postgresql://postgres:password@localhost:5432/postgres")
PG_COLLECTION_NAME = os.getenv("PG_COLLECTION_NAME", "rag_embedding")

# Embedding model for retrieval
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Number of relevant documents to retrieve
K_RETRIEVED_DOCUMENTS = 4

# --- Initialize Components ---

def initialize_llm():
    print(f"Loading LLaMA 3.1-8B model from {LLAMA_MODEL_PATH}...")
    # Load model in FP16
    model = AutoModelForCausalLM.from_pretrained(LLAMA_MODEL_PATH, torch_dtype=torch.float16)
    tokenizer = AutoTokenizer.from_pretrained(LLAMA_MODEL_PATH)
    
    # Simple wrapper for the model to be used with LangChain
    # This is a basic example; for more robust integration, consider LangChain's HuggingFacePipeline
    class CustomLLM:
        def __init__(self, model, tokenizer):
            self.model = model
            self.tokenizer = tokenizer

        def _call(self, prompt: str, stop: list[str] | None = None) -> str:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            with torch.no_grad():
                outputs = self.model.generate(**inputs, max_new_tokens=200, num_return_sequences=1)
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response

        @property
        def _llm_type(self) -> str:
            return "custom_llama"

    return CustomLLM(model, tokenizer)

def initialize_retriever():
    print(f"Initializing retriever for collection: {PG_COLLECTION_NAME}...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    
    vectorstore = PGVector(
        collection_name=PG_COLLECTION_NAME,
        connection_string=PG_CONNECTION_STRING,
        embedding_function=embeddings,
        # pre_delete_collection=False # Do not delete existing collection
    )
    return vectorstore.as_retriever(search_kwargs={"k": K_RETRIEVED_DOCUMENTS})

def setup_rag_chain(llm, retriever):
    print("Setting up RAG chain...")
    # Define the prompt template for RAG
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
    # Check if model path exists
    if not os.path.exists(LLAMA_MODEL_PATH):
        print(f"Error: LLaMA model not found at {LLAMA_MODEL_PATH}.")
        print("Please ensure the model files are in this directory or update LLAMA_MODEL_PATH.")
        print("If you downloaded the model using 'llama model download', ensure it's the PyTorch version.")
        print("For better performance on CPU, consider converting the model to GGUF format and using llama-cpp-python.")
    else:
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
            try:
                result = rag_chain({"query": query})
                print("\nAnswer:")
                print(result["result"])
                print("\nSource Documents:")
                for doc in result["source_documents"]:
                    print(f"- {doc.metadata['source']}: {doc.page_content[:100]}...")
            except Exception as e:
                print(f"An error occurred: {e}")
                print("Please ensure your PostgreSQL database is running and accessible, and the LLaMA model is correctly loaded.")

    print("Exiting RAG system.")
