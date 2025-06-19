import itertools
import os
from collections import defaultdict

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
# Example of defining a semantic configuration when creating an index using the Python SDK
# SemanticConfiguration,; SemanticField,; SemanticSettings,
from azure.search.documents.indexes.models import (HnswAlgorithmConfiguration,
                                                   SearchableField,
                                                   SearchField,
                                                   SearchFieldDataType,
                                                   SearchIndex, SimpleField,
                                                   VectorSearch,
                                                   VectorSearchProfile)
from azure.search.documents.models import VectorizedQuery
from dotenv import find_dotenv, load_dotenv
# from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings
from loguru import logger
from pydantic import BaseModel
from rich import print
from tqdm import tqdm

# load_dotenv(dotenv_path=".env")  # Load environment variables from .secret file
# parent parent
load_dotenv(find_dotenv(".env"))
load_dotenv(find_dotenv(".secret"))
# load_dotenv(dotenv_path=".secret")  # Load environment variables from .secret file
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


class ExperienceV0(BaseModel):
    key: str
    permalink: str
    url: str
    source_type: str
    action_score: int
    outcomes_score: int
    action: str
    health_disorder: str
    outcomes: str
    # personal_context: str
    mechanism: str
    biohack_type: str
    biohack_topic: str

    @classmethod
    def create_index(cls, *, index_name: str):
        logger.info(f"Creating index: {index_name}")
        fields = [
            SimpleField(
                name="key",
                type=SearchFieldDataType.String,
                key=True,
                filterable=False,
            ),
            SimpleField(
                name="permalink",
                type=SearchFieldDataType.String,
                key=False,
                filterable=True,
            ),
            SimpleField(
                name="url", type=SearchFieldDataType.String, key=False, filterable=True
            ),
            SimpleField(
                name="source_type",
                type=SearchFieldDataType.String,
                key=False,
                filterable=True,
                facetable=True,
            ),
            SimpleField(
                name="action_score",
                type=SearchFieldDataType.Int32,
                key=False,
                sortable=True,
            ),
            SimpleField(
                name="outcomes_score",
                type=SearchFieldDataType.Int32,
                key=False,
                sortable=True,
            ),
            SearchableField(
                name="action",
                type=SearchFieldDataType.String,
                sortable=False,
                filterable=True,
                facetable=False,
            ),
            SearchableField(
                name="health_disorder",
                type=SearchFieldDataType.String,
                sortable=False,
                filterable=True,
                facetable=False,
            ),
            SearchableField(
                name="outcomes",
                type=SearchFieldDataType.String,
                sortable=False,
                filterable=True,
                facetable=False,
            ),
            SearchableField(
                name="personal_context",
                type=SearchFieldDataType.String,
                sortable=False,
                filterable=True,
                facetable=False,
            ),
            SearchableField(
                name="mechanism",
                type=SearchFieldDataType.String,
                sortable=False,
                filterable=True,
                facetable=False,
            ),
            SearchableField(
                name="biohack_type",
                type=SearchFieldDataType.String,
                sortable=False,
                filterable=True,
                facetable=True,
            ),
            SearchableField(
                name="biohack_topic",
                type=SearchFieldDataType.String,
                sortable=False,
                filterable=True,
                facetable=True,
            ),
            SearchField(
                name="health_disorderVector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=3072,
                vector_search_profile_name="my-vector-config",
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

        # semantic_config = SemanticConfiguration(
        # 	name="default",
        # 	prioritized_fields={
        # 		"titleField": {"fieldName": "title"},
        # 		"contentFields": [{"fieldName": "content"}],
        # 		"keywordsFields": [{"fieldName": "category"}],
        # 	}
        # )
        #
        # semantic_settings = SemanticSettings(configurations=[semantic_config])

        index_client = SearchIndexClient(service_endpoint, credential)
        try:
            index_client.create_index(
                # SearchIndex(
                #     name=index_name, fields=fields, vector_search=vector_search_config, semantic_settings=semantic_settings
                # )
                SearchIndex(
                    name=index_name, fields=fields, vector_search=vector_search_config
                )
            )
        except Exception as e:
            print(f"Index creation failed: {e}")


def upload_experiences(*, index_name: str, limit: int | None = None):
    # leave this import here to avoid collision with modules of same name ....settings.py etc
    from website.biohacks import TopicExperiences

    search_client = SearchClient(
        azure_search_endpoint, index_name, AzureKeyCredential(azure_search_key)
    )
    errors = defaultdict(int)
    docs = []
    topics = ["Biohacking", "Sleep", "Pregnancy"]  # topics are sets of subreddits
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
            # print(experience)
            # breakpoint()
            # doc = cls.from_pydantic(experience)
            # transform - prunes unused fields
            try:
                exp = ExperienceV0(**experience.model_dump())
                docs.append(exp.model_dump())
            except Exception as e:
                errors[str(e)] += 1
                logger.warning(f"Error creating ExperienceV0: {e}")
            # docs.append(doc)
    # EMBEDDING STEP BREAKS BATCH UPLOAD.....
    save_batch_size = 50
    docs_batches = list(itertools.batched(docs, save_batch_size))
    total_batches = len(docs_batches)
    counter = 0
    for number, batch in enumerate(docs_batches):
        docs_with_vectors = []
        logger.info(f"Embedding batch {number + 1}/{total_batches}...")

        embedding_batch = openai_large.embed_documents(
            [doc["health_disorder"] for doc in batch]
        )
        for doc, embedding in zip(batch, embedding_batch):
            doc["health_disorderVector"] = embedding
            docs_with_vectors.append(doc)
        logger.debug(f"Embedding done, Uploading batch {number + 1}/{total_batches}...")
        result = search_client.upload_documents(documents=docs_with_vectors)
        if result:
            counter += len(result)
            logger.success(
                f"Documents with vectors uploaded successfully: {counter}, {counter/len(docs)*100:.2f}%"
            )
        else:
            logger.error("No documents were uploaded.")
            raise ValueError("No documents were uploaded.")
    if errors:
        print("Errors encountered during upload:")
        for error, count in errors.items():
            print(f"{error}: {count}")


if __name__ == "__main__":
    # TODO: Figure out semantic search with python sdk
    # https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/search/azure-search-documents/samples
    # https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/search/azure-search-documents

    # index_name = "experiences-index-4"
    index_name = "experiences-index-3"
    # ExperienceV0.create_index(index_name=index_name)
    # upload_experiences(index_name=index_name, limit=100)
    search_client = SearchClient(
        azure_search_endpoint, index_name, AzureKeyCredential(azure_search_key)
    )

    query = "Inducement labor"

    vector_query = VectorizedQuery(
        vector=openai_large.embed_query(query),
        k_nearest_neighbors=3,
        fields="health_disorderVector",
    )

    results = search_client.search(
        vector_queries=[vector_query],
        select=["health_disorder", "action", "outcomes", "url"],
        top=5,
    )

    for number, result in enumerate(results):
        logger.info(f"VECTOR Result {number + 1}: {print(result)}")

    results = search_client.search(
        search_text=query,
        vector_queries=[vector_query],
        select=["health_disorder", "action", "outcomes", "url"],
        top=5,
    )

    logger.warning("HYBRID -----------------------------------")
    for number, result in enumerate(results):
        logger.success(f"HYBRID Result {number + 1}: {print(result)}")


# results = search_client.search(
# 	search_text="search query",
# 	query_type="semantic",
# 	semantic_configuration_name="my-semantic-config",
# 	query_language="en-us",
# 	captions="extractive|highlight-true",
# 	answers="extractive|count-3",
# 	select=["health_disorder", "action", "outcomes", "url"],
# 	top=5,
# )
#
#
#    logger.warning("SEMANTIC -----------------------------------")
#    for number, result in enumerate(results):
#        logger.success(f"SEMANTIC Result {number + 1}: {print(result)}")
