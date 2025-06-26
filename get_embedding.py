from langchain_ollama import OllamaEmbeddings

# Call embedding model
def get_embedding():
    embeddings = OllamaEmbeddings(model="mxbai-embed-large")
    return embeddings