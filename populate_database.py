from langchain.vectorstores.chroma import Chroma
from get_embedding import get_embedding
from langchain.schema.document import Document
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import re

# Load audit files
def load_audit_files(audit_dir):
    audit_docs = []
    for fname in os.listdir(audit_dir):
        if fname.endswith(".audit"):
            loader = TextLoader(os.path.join(audit_dir, fname))
            docs = loader.load()
            # Add metadata to differentiate
            for doc in docs:
                doc.metadata["source_type"] = "audit_example"
            audit_docs.extend(docs)
    return audit_docs

# Load PDFs into docs variable
def load_documents():
    pdf_docs = []
    for fname in os.listdir("data"):
        if fname.endswith(".pdf"):
            loader = PyMuPDFLoader(os.path.join("data", fname))
            docs = loader.load()
            for doc in docs:
                doc.metadata["source_type"] = "documentation"
            pdf_docs.extend(docs)

    audit_docs = load_audit_files("audit_examples")
    return pdf_docs, audit_docs

# Split document into chunks so that its easily stored
def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1200,
        chunk_overlap = 100,
        length_function = len,
        is_separator_regex = False,
    )
    return text_splitter.split_documents(documents)

def split_documents_by_page(documents: list[Document]):
    return documents

def split_documents_audit(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000000,  # Disable chunk size
        chunk_overlap=0,
        separators=["</custom_item>"]  # only split on end of custom items
    )
    return text_splitter.split_documents(documents)

def regex_split_custom_items(docs: list[Document]) -> list[Document]:
    custom_item_pattern = r"<custom_item>.*?</custom_item>"
    split_docs = []

    for doc in docs:
        matches = re.findall(custom_item_pattern, doc.page_content, flags=re.DOTALL)
        for i, match in enumerate(matches):
            split_docs.append(Document(
                page_content=match.strip(),
                metadata={**doc.metadata, "split_index": i}
            ))

    return split_docs

# Add chunks to chromaDB
def add_to_chroma(chunks: list[Document]):
    # Load the existing database
    db = Chroma(
        persist_directory="chroma", embedding_function=get_embedding()
    )

    # Calculate Page IDs
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks] # Adding IDs with the chunks

        # For adding documents 100 at a time
        # for i in range(0, len(new_chunks), 100):            
        #     batch = new_chunks[i:i+100]
        #     batch_ids = new_chunk_ids[i:i+100]
        #     db.add_documents(batch, ids=batch_ids)
        #     print(f"batch:{i} added")

        db.add_documents(new_chunks, ids=new_chunk_ids)
        db.persist()
    else:
        print("✅ No new documents to add")

# This function will create IDs like "data/pdfName.pdf:6:2"
# Page Source : Page Number : Chunk Index
def calculate_chunk_ids(chunks):
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page metadata
        chunk.metadata["id"] = chunk_id

    return chunks

def main():
    # Load PDFs and audits separately
    pdf_docs, audit_docs = load_documents()
    
    # Split PDFs with standard splitter 
    # chunks_pdf = split_documents(pdf_docs)
    chunks_pdf = split_documents_by_page(pdf_docs)

    # Split audit files with audit splitter
    # chunks_audit = split_documents_audit(audit_docs)
    chunks_audit = regex_split_custom_items(audit_docs)

    # Combine all chunks
    # all_chunks = chunks_pdf + chunks_audit

    # Add combined chunks to chromaDB
    add_to_chroma(chunks_pdf)

main()
