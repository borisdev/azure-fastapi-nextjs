import os

from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from rich import print

load_dotenv(dotenv_path=".secret")  # Load environment variables from .secret file

embeddings: AzureOpenAIEmbeddings = AzureOpenAIEmbeddings(
    azure_deployment="text-embedding-3-large",
    openai_api_version="2024-02-01",
    azure_endpoint="https://boris-m3ndov9n-eastus2.cognitiveservices.azure.com/",
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
)


# Azure Search

index_name: str = "experiences_4"
vector_store: AzureSearch = AzureSearch(
    azure_search_endpoint=os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"],
    azure_search_key=os.environ["AZURE_SEARCH_API_KEY"],
    index_name=index_name,
    embedding_function=embeddings.embed_query,  # pre-processing w batch embedding, before batch load
    additional_search_client_options={"retry_total": 4},
)


if __name__ == "__main__":
    pass
    # vector_store.add_documents(documents=docs)
