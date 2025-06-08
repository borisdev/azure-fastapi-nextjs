import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (HnswAlgorithmConfiguration,
                                                   SearchableField,
                                                   SearchField,
                                                   SearchFieldDataType,
                                                   SearchIndex, SimpleField,
                                                   VectorSearch,
                                                   VectorSearchProfile)
from azure.search.documents.models import VectorizedQuery
from dotenv import load_dotenv
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings
from rich import print

load_dotenv(dotenv_path=".secret")  # Load environment variables from .secret file
index_name = "hotels-index"

openai_large = AzureOpenAIEmbeddings(
    # vector = openai_large.embed_query(text)
    # vectors = openai_large.embed_documents(input_texts)
    azure_deployment="text-embedding-3-large",
    openai_api_version="2024-02-01",  # pyright: ignore
    azure_endpoint="https://boris-m3ndov9n-eastus2.cognitiveservices.azure.com/",
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
)

azure_search_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
azure_search_key = os.environ["AZURE_SEARCH_API_KEY"]
azure_search_client = SearchClient(
    azure_search_endpoint, index_name, AzureKeyCredential(azure_search_key)
)

fields = [
    SimpleField(name="hotelId", type=SearchFieldDataType.String, key=True),
    SearchableField(
        name="hotelName",
        type=SearchFieldDataType.String,
        sortable=True,
        filterable=True,
    ),
    SearchableField(name="description", type=SearchFieldDataType.String),
    SearchField(
        name="descriptionVector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=1536,
        vector_search_profile_name="my-vector-config",
    ),
    SearchableField(
        name="category",
        type=SearchFieldDataType.String,
        sortable=True,
        filterable=True,
        facetable=True,
    ),
]
vector_search_config = VectorSearch(
    profiles=[
        VectorSearchProfile(
            name="my-vector-config",
            algorithm_configuration_name="my-algorithms-config",
        )
    ],
    algorithms=[HnswAlgorithmConfiguration(name="my-algorithms-config")],
)
search_index = SearchIndex(
    name=index_name, fields=fields, vector_search=vector_search_config
)


docs = [
    {
        "hotelId": "1",
        "hotelName": "Fancy Stay",
        "description": "Best hotel in town if you like luxury hotels.",
        "category": "Luxury",
    },
    {
        "hotelId": "2",
        "hotelName": "Roach Motel",
        "description": "Cheapest hotel in town. Infact, a motel.",
        "category": "Budget",
    },
    {
        "hotelId": "3",
        "hotelName": "EconoStay",
        "description": "Very popular hotel in town.",
        "category": "Budget",
    },
    {
        "hotelId": "4",
        "hotelName": "Modern Stay",
        "description": "Modern architecture, very polite staff and very clean. Also very affordable.",
        "category": "Luxury",
    },
    {
        "hotelId": "5",
        "hotelName": "Secret Point",
        "description": "One of the best hotel in town. The hotel is ideally located on the main commercial artery of the city in the heart of New York.",
        "category": "Boutique",
    },
]
embedd_docs = []
for doc in docs:
    embedd_docs.append(
        {
            "hotelId": doc["hotelId"],
            "hotelName": doc["hotelName"],
            "description": doc["description"],
            "category": doc["category"],
            "descriptionVector": openai_large.embed_query(doc["description"]),
        }
    )


query = "Top hotels in town"
query_vector = openai_large.embed_query(query)

vector_query = VectorizedQuery(
    vector=query_vector, k_nearest_neighbors=3, fields="descriptionVector"
)

results = azure_search_client.search(
    vector_queries=[vector_query],
    select=["hotelId", "hotelName"],
)

for result in results:
    print(result)


results = azure_search_client.search(
    search_text="",
    vector_queries=[vector_query],
    filter="category eq 'Luxury'",
    select=["hotelId", "hotelName"],
)

for result in results:
    print(result)


vector_query = VectorizedQuery(
    vector=openai_large.embed_query(query),
    k_nearest_neighbors=3,
    fields="descriptionVector",
)

results = azure_search_client.search(
    search_text=query,
    vector_queries=[vector_query],
    select=["hotelId", "hotelName"],
)

for result in results:
    print(result)
