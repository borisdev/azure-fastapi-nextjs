import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import VectorizedQuery
from dotenv import load_dotenv

load_dotenv(dotenv_path=".secret")  # Load environment variables from .secret file
service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]
index_name = "hotels-index-2"  # You can change this to any name you prefer


def get_hotel_index(name: str):
    from azure.search.documents.indexes.models import (
        HnswAlgorithmConfiguration, SearchableField, SearchField,
        SearchFieldDataType, SearchIndex, SimpleField, VectorSearch,
        VectorSearchProfile)

    fields = [
        SimpleField(name="hotelId", type=SearchFieldDataType.String, key=True),
        SearchableField(
            name="hotelName",
            type=SearchFieldDataType.String,
            sortable=True,
            filterable=True,
        ),
        SearchableField(name="description", type=SearchFieldDataType.String),
        # SearchField(
        #     name="descriptionVector",
        #     type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        #     searchable=True,
        #     vector_search_dimensions=1536,
        #     vector_search_profile_name="my-vector-config",
        # ),
        SearchableField(
            name="category",
            type=SearchFieldDataType.String,
            sortable=True,
            filterable=True,
            facetable=True,
        ),
    ]
    vector_search = VectorSearch(
        profiles=[
            VectorSearchProfile(
                name="my-vector-config",
                algorithm_configuration_name="my-algorithms-config",
            )
        ],
        algorithms=[HnswAlgorithmConfiguration(name="my-algorithms-config")],
    )
    return SearchIndex(name=name, fields=fields, vector_search=vector_search)


def get_hotel_documents():
    docs = [
        {
            "hotelId": "1",
            "hotelName": "Fancy Stay",
            "description": "Best hotel in town if you like luxury hotels.",
            # "descriptionVector": get_embeddings(
            #     "Best hotel in town if you like luxury hotels."
            # ),
            "category": "Luxury",
        },
        {
            "hotelId": "2",
            "hotelName": "Roach Motel",
            "description": "Cheapest hotel in town. Infact, a motel.",
            # "descriptionVector": get_embeddings(
            #     "Cheapest hotel in town. Infact, a motel."
            # ),
            "category": "Budget",
        },
        {
            "hotelId": "3",
            "hotelName": "EconoStay",
            "description": "Very popular hotel in town.",
            # "descriptionVector": get_embeddings("Very popular hotel in town."),
            "category": "Budget",
        },
        {
            "hotelId": "4",
            "hotelName": "Modern Stay",
            "description": "Modern architecture, very polite staff and very clean. Also very affordable.",
            # "descriptionVector": get_embeddings(
            #     "Modern architecture, very polite staff and very clean. Also very affordable."
            # ),
            "category": "Luxury",
        },
        {
            "hotelId": "5",
            "hotelName": "Secret Point",
            "description": "One of the best hotel in town. The hotel is ideally located on the main commercial artery of the city in the heart of New York.",
            # "descriptionVector": get_embeddings(
            #     "One of the best hotel in town. The hotel is ideally located on the main commercial artery of the city in the heart of New York."
            # ),
            "category": "Boutique",
        },
    ]
    return docs


if __name__ == "__main__":
    credential = AzureKeyCredential(key)
    index_client = SearchIndexClient(service_endpoint, credential)
    index = get_hotel_index(index_name)
    try:
        index_client.create_index(index)
    except Exception as e:
        print(f"Index {index_name} already exists. Error: {e}")
        pass
    client = SearchClient(service_endpoint, index_name, credential)
    hotel_docs = get_hotel_documents()
    client.upload_documents(documents=hotel_docs)

    query = "Top hotels in town"
    query = "boris johnson"
    query = "town x"
    print(f"\nSearch results for hotels using query: {query}")
    print("=====================================================")
    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))
    results = search_client.search(
        search_text=query,
        select=["hotelId", "hotelName"],
    )

    for result in results:
        print(result)

    filter = "category eq 'Luxury'"
    print(f"\nSearch results for hotels using filter: {filter}")
    print("=====================================================")
    results = search_client.search(
        search_text="",
        filter="category eq 'Luxury'",
        select=["hotelId", "hotelName"],
    )

    for result in results:
        print(result)
