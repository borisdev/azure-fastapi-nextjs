import asyncio
import io
import os

from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from rich import print

# Suppress the specific asyncio warning from AzureSearch destructor


load_dotenv(dotenv_path=".secret")  # Load environment variables from .secret file

embeddings: AzureOpenAIEmbeddings = AzureOpenAIEmbeddings(
    azure_deployment="text-embedding-3-large",
    openai_api_version="2024-02-01",
    azure_endpoint="https://boris-m3ndov9n-eastus2.cognitiveservices.azure.com/",
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
)


# Azure Search
vector_store_address: str = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
vector_store_password: str = os.environ["AZURE_SEARCH_API_KEY"]

index_name: str = "langchain-vector-demo"
vector_store: AzureSearch = AzureSearch(
    azure_search_endpoint=vector_store_address,
    azure_search_key=vector_store_password,
    index_name=index_name,
    embedding_function=embeddings.embed_query,
    additional_search_client_options={"retry_total": 4},
)

# try:
#     loader = TextLoader("state_of_the_union.txt", encoding="utf-8")
#     documents = loader.load()
#     text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
#     docs = text_splitter.split_documents(documents)
#     vector_store.add_documents(documents=docs)
# finally:
#     # Properly close the vector store to avoid asyncio cleanup warnings
#     if hasattr(vector_store, "close"):
#         vector_store.close()
#     elif hasattr(vector_store, "_client") and hasattr(vector_store._client, "close"):
#         vector_store._client.close()

if __name__ == "__main__":
    print("Vector store setup complete. Documents added successfully.")
    # Perform a similarity search
    docs = vector_store.similarity_search(
        query="What did the president say about Ketanji Brown Jackson",
        k=3,
        search_type="similarity",
    )
    print(f"Found {len(docs)} documents matching the query.")

    # Script will end here and trigger cleanup, but warnings will be suppressed
    print("=" * 40)
    print(docs[0])
