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


# class ExperienceDoc4(Document):
#     permalink = Keyword(index=False)
#     url = Keyword(index=False)
#     source_type = Keyword()
#     action = Text(analyzer="english")
#     health_disorder = Text(analyzer="english")
#     outcomes = Text(analyzer="english")
#     personal_context = Text(analyzer="english")
#     mechanism = Text(analyzer="english")
#     biohack_type = Keyword()
#     biohack_topic = Keyword()
#     action_score = Integer()
#     outcomes_score = Integer()
#
#     @classmethod
#     def from_pydantic(cls, experience: Experience) -> ExperienceDoc4:
#         return cls(
#             **experience.model_dump(
#                 include={
#                     "permalink",
#                     "url",
#                     "source_type",
#                     "action",
#                     "health_disorder",
#                     "outcomes",
#                     "personal_context",
#                     "mechanism",
#                     "biohack_type",
#                     "action_score",
#                     "outcomes_score",
#                     "biohack_topic",
#                 }
#             ),
#             # source_type=experience.source_type,
#         )
#
def create_index():
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
    index_client = SearchIndexClient(service_endpoint, credential)
    try:
        index_client.create_index(
            SearchIndex(
                name=index_name, fields=fields, vector_search=vector_search_config
            )
        )
    except Exception as e:
        print(f"Index creation failed: {e}")


def upload_experiences(*, index_name: str):
    from website.biohacks import TopicExperiences

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

    index_name = "experiences-index-0"
    # add_index()
    # upload_experiences(index_name=index_name)
    # test_search_on_experiences(index_name=index_name)
