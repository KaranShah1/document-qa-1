import requests
import zipfile
import io
import os
from bs4 import BeautifulSoup
import openai
import chromadb
import time
import streamlit as st

# Initialize ChromaDB client
client = chromadb.Client()
collection_name = "Lab4_Collections"

# Delete collection if it exists
try:
    client.delete_collection(collection_name)
except Exception as e:
    print(f"Error deleting collection: {e}")

# Create a new collection
collection = client.create_collection(name=collection_name)

# Function to download and extract the GitHub repository
def download_and_extract_github_repo():
    url = 'https://github.com/KaranShah1/document-qa-1/archive/refs/heads/main.zip'
    response = requests.get(url)
    
    if response.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            zip_ref.extractall("Lab4_datafiles")
        st.success("Repository successfully downloaded and extracted!")
    else:
        st.error("Failed to download the repository.")

# Function to read HTML files and convert them to text
def read_html_to_text(html_path):
    with open(html_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        return soup.get_text()

# Function to add new HTML files to the vector database
def add_new_html_to_vector_db(new_html_folder_path):
    for html_filename in os.listdir(new_html_folder_path):
        if html_filename.endswith(".html"):
            html_path = os.path.join(new_html_folder_path, html_filename)
            st.write(f"Processing new file: {html_filename}")

            # Extract text from the new HTML file
            document_text = read_html_to_text(html_path)

            # Set the OpenAI API key
            openai_api_key = st.secrets.get("openai")
            openai.api_key = openai_api_key

            # Generate embeddings
            embedding_response = openai.Embedding.create(
                input=document_text,
                model="text-embedding-ada-002"  # Updated model
            )
            embedding_vector = embedding_response['data'][0]['embedding']

            # Add new document and embedding to ChromaDB collection
            collection.add(
                documents=[document_text],
                embeddings=[embedding_vector],
                metadatas=[{"filename": html_filename}],
                ids=[html_filename]
            )
            st.write(f"Added {html_filename} to the vector database.")
            time.sleep(20)

# Main function to manage the process
def main():
    # Download and extract GitHub repo
    download_and_extract_github_repo()

    # Process and add HTML files to vector database
    new_html_folder_path = './Lab4_datafiles/document-qa-1-main/Lab4_datafiles/'  # Adjust the path after extraction
    add_new_html_to_vector_db(new_html_folder_path)

# Streamlit UI
st.title("ChromaDB & OpenAI Embedding Processor")
if st.button("Process Documents"):
    main()
