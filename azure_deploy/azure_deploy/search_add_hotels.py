import itertools
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
# from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings
from loguru import logger
from rich import print
from tqdm import tqdm

load_dotenv(dotenv_path=".env")  # Load environment variables from .secret file
load_dotenv(dotenv_path=".secret")  # Load environment variables from .secret file
credential = AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"])
service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]

openai_large = AzureOpenAIEmbeddings(
    # Usage examples:
    # vector = openai_large.embed_query(text)
    # vectors = openai_large.embed_documents(input_texts)
    azure_deployment="text-embedding-3-large",
    openai_api_version="2024-02-01",  # pyright: ignore
    azure_endpoint="https://openai-rg-nobsmed.openai.azure.com/",
    api_key=os.environ["API_KEY"],
)

azure_search_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
azure_search_key = os.environ["AZURE_SEARCH_API_KEY"]
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
        vector_search_dimensions=3072,
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


def upload_hotels(*, index_name: str):
    index_client = SearchIndexClient(service_endpoint, credential)
    try:
        index_client.create_index(
            SearchIndex(
                name=index_name, fields=fields, vector_search=vector_search_config
            )
        )
    except Exception as e:
        print(f"Index creation failed: {e}")

    hotels = [
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
    for hotel in hotels:
        hotel["descriptionVector"] = openai_large.embed_query(hotel["description"])
    search_client = SearchClient(
        azure_search_endpoint, index_name, AzureKeyCredential(azure_search_key)
    )
    try:
        result = search_client.upload_documents(documents=hotels)
        if result:
            logger.info(f"Documents uploaded successfully: {result}")
        else:
            logger.warning("No documents were uploaded.")
    except Exception as e:
        logger.error(f"Failed to upload documents: {e}")


def test_search_on_hotels(*, index_name: str):
    search_client = SearchClient(
        azure_search_endpoint, index_name, AzureKeyCredential(azure_search_key)
    )
    query = "Top hotels in town"
    query_vector = openai_large.embed_query(query)

    vector_query = VectorizedQuery(
        vector=query_vector, k_nearest_neighbors=3, fields="descriptionVector"
    )

    results = search_client.search(
        vector_queries=[vector_query],
        select=["hotelId", "hotelName"],
    )

    for result in results:
        print(result)

    results = search_client.search(
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

    results = search_client.search(
        search_text=query,
        vector_queries=[vector_query],
        select=["hotelId", "hotelName"],
    )

    for result in results:
        print(result)


def upload_experiences(*, index_name: str):
    from website.biohacks import TopicExperiences

    index_client = SearchIndexClient(service_endpoint, credential)
    docs = []
    topics = ["Biohacking", "Sleep", "Pregnancy"]  # topics are sets of subreddits
    limit = 1000
    for topic in topics:
        print(topic)
        o = TopicExperiences.load(name=topic)
        target_experiences = [experience for experience in o.experiences]
        valid_experiences = [
            experience
            for experience in target_experiences
            if experience.valid_biohack(action_score=2, outcomes_score=2)
            and experience.source_type == "reddit"
        ]
        for experience in tqdm(valid_experiences[:limit]):
            print(experience)
            # doc = cls.from_pydantic(experience)
            docs.append(experience.model_dump())
            # docs.append(doc)
    # save_batch_size = 500
    # docs_batches = list(itertools.batched(docs, save_batch_size))
    try:
        index_client.create_index(
            SearchIndex(
                name=index_name, fields=fields, vector_search=vector_search_config
            )
        )
    except Exception as e:
        print(f"Index creation failed: {e}")

    # for doc in docs:
    #     hotel["descriptionVector"] = openai_large.embed_query(hotel["description"])
    search_client = SearchClient(
        azure_search_endpoint, index_name, AzureKeyCredential(azure_search_key)
    )
    try:
        result = search_client.upload_documents(documents=docs)
        if result:
            logger.info(f"Documents uploaded successfully: {result}")
        else:
            logger.warning("No documents were uploaded.")
    except Exception as e:
        logger.error(f"Failed to upload documents: {e}")


if __name__ == "__main__":

    # index_name = "hotels-index-3"
    # upload_hotels(index_name=index_name)
    # test_search_on_hotels(index_name=index_name)
    index_name = "experiences-index-0"
    # add_index()
    # upload_experiences(index_name=index_name)
