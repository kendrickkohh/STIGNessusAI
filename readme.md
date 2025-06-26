# # STIG2Nessus-GenAI
A Generative AI-powered tool to convert Security Technical Implementation Guides (STIGs) into Tenable Nessus audit files.  
This project leverages Retrieval-Augmented Generation (RAG) with vector embeddings to parse and understand STIG documentation and generate accurate Nessus audit scripts.

---

## Features
- Parse and chunk STIG documents (PDF/CSV) and Nessus `.audit` example files separately  
- Store parsed chunks into a vector store for efficient semantic search  
- Use generative AI (Ollama model or similar) combined with RAG to generate fluent and valid Nessus audit file syntax  
- Differentiate between STIG documentation and audit examples via metadata in the vector store  
- Modular, extensible pipeline to add more sources or formats  

---

## Getting Started

### Prerequisites
- Python 3.10  
- [LangChain](https://github.com/hwchase17/langchain) and related dependencies  
- Vector database: [Chroma](https://www.trychroma.com/)  

### Installation
```bash
pip install -r requirements.txt
