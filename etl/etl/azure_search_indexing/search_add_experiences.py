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
    """Upload Reddit experiences to Azure Search index."""
    # leave this import here to avoid collision with modules of same name ....settings.py etc
    from website.biohacks import TopicExperiences

    search_client = SearchClient(
        azure_search_endpoint, index_name, AzureKeyCredential(azure_search_key)
    )
    errors = defaultdict(int)
    docs = []
    topics = ["Biohacking", "Sleep", "Pregnancy"]  # topics are sets of subreddits
    for topic in topics:
        print(f"Processing Reddit topic: {topic}")
        o = TopicExperiences.load(name=topic)
        target_experiences = [experience for experience in o.experiences]
        valid_experiences = [
            experience
            for experience in target_experiences
            if experience.valid_biohack(action_score=2, outcomes_score=2)
            and experience.source_type == "reddit"
        ]
        for experience in tqdm(valid_experiences[:limit], desc=f"Reddit {topic}"):
            try:
                exp = ExperienceV0(**experience.model_dump())
                docs.append(exp.model_dump())
            except Exception as e:
                errors[str(e)] += 1
                logger.warning(f"Error creating ExperienceV0: {e}")
    
    logger.info(f"Found {len(docs)} valid Reddit experiences")
    _upload_docs_with_embeddings(search_client, docs, "Reddit experiences")
    
    if errors:
        print("Errors encountered during Reddit upload:")
        for error, count in errors.items():
            print(f"{error}: {count}")


def upload_studies(*, index_name: str, action_score: int = 1, outcomes_score: int = 1, limit: int | None = None, studies_dir: str | None = None):
    """Upload study experiences to Azure Search index."""
    import json
    from pathlib import Path
    from website.experiences import Experience

    search_client = SearchClient(
        azure_search_endpoint, index_name, AzureKeyCredential(azure_search_key)
    )
    
    # Default studies directory path (adjust as needed)
    if studies_dir is None:
        studies_dir = "/Users/borisdev/workspace/nobsmed/data/etl_store/study_deep_experiences_enriched/"
    
    source_dir = Path(studies_dir)
    if not source_dir.exists():
        logger.warning(f"Studies directory not found: {source_dir}")
        print(f"Studies directory not found: {source_dir}")
        return
    
    files = [file for file in source_dir.rglob("*.json")]
    logger.info(f"Found {len(files)} study files")
    print(f"Found {len(files)} study files")
    
    if not files:
        logger.warning("No study JSON files found")
        return
    
    experiences = []
    errors = defaultdict(int)
    
    for file in tqdm(files, desc="Loading study files"):
        try:
            experience = Experience(**json.loads(file.read_text()))
            experiences.append(experience)
        except Exception as e:
            errors[f"File loading error: {str(e)}"] += 1
            logger.warning(f"Error loading study file {file}: {e}")
    
    # Filter valid experiences
    valid_experiences = [
        experience
        for experience in experiences
        if experience.valid_biohack(action_score=action_score, outcomes_score=outcomes_score)
    ]
    
    logger.info(f"Loaded {len(experiences)} studies, {len(valid_experiences)} valid")
    print(f"Loaded {len(experiences)} studies, {len(valid_experiences)} valid")
    
    docs = []
    for experience in tqdm(valid_experiences[:limit], desc="Processing studies"):
        try:
            exp = ExperienceV0(**experience.model_dump())
            docs.append(exp.model_dump())
        except Exception as e:
            errors[f"ExperienceV0 creation error: {str(e)}"] += 1
            logger.warning(f"Error creating ExperienceV0 from study: {e}")
    
    logger.info(f"Prepared {len(docs)} study documents for upload")
    _upload_docs_with_embeddings(search_client, docs, "Study experiences")
    
    if errors:
        print("Errors encountered during study upload:")
        for error, count in errors.items():
            print(f"{error}: {count}")


def _upload_docs_with_embeddings(search_client: SearchClient, docs: list, description: str):
    """Helper function to upload documents with embeddings in batches."""
    if not docs:
        logger.warning(f"No documents to upload for {description}")
        return
    
    save_batch_size = 50
    docs_batches = list(itertools.batched(docs, save_batch_size))
    total_batches = len(docs_batches)
    counter = 0
    
    for number, batch in enumerate(docs_batches):
        docs_with_vectors = []
        logger.info(f"Embedding {description} batch {number + 1}/{total_batches}...")

        embedding_batch = openai_large.embed_documents(
            [doc["health_disorder"] for doc in batch]
        )
        for doc, embedding in zip(batch, embedding_batch):
            doc["health_disorderVector"] = embedding
            docs_with_vectors.append(doc)
        
        logger.debug(f"Embedding done, Uploading {description} batch {number + 1}/{total_batches}...")
        result = search_client.upload_documents(documents=docs_with_vectors)
        
        if result:
            counter += len(result)
            logger.success(
                f"{description} batch uploaded successfully: {counter}, {counter/len(docs)*100:.2f}%"
            )
        else:
            logger.error(f"No {description} documents were uploaded.")
            raise ValueError(f"No {description} documents were uploaded.")
    
    logger.success(f"Completed uploading {counter} {description}")


def upload_all_experiences(*, index_name: str, reddit_limit: int | None = None, studies_limit: int | None = None, studies_dir: str | None = None):
    """Upload both Reddit experiences and studies to Azure Search index."""
    logger.info("Starting upload of all experiences (Reddit + Studies)")
    
    # Upload Reddit experiences
    logger.info("=== Uploading Reddit Experiences ===")
    upload_experiences(index_name=index_name, limit=reddit_limit)
    
    # Upload study experiences  
    logger.info("=== Uploading Study Experiences ===")
    upload_studies(
        index_name=index_name, 
        action_score=1, 
        outcomes_score=1, 
        limit=studies_limit,
        studies_dir=studies_dir
    )
    
    logger.success("Completed upload of all experiences")


if __name__ == "__main__":
    # TODO: Figure out semantic search with python sdk
    # https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/search/azure-search-documents/samples
    # https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/search/azure-search-documents

    index_name = "experiences-index-3"
    
    # Uncomment to create index and upload data:
    # ExperienceV0.create_index(index_name=index_name)
    
    # Upload only Reddit experiences:
    # upload_experiences(index_name=index_name, limit=100)
    
    # Upload only studies:
    # upload_studies(index_name=index_name, action_score=1, outcomes_score=1, limit=50)
    
    # Upload both Reddit + Studies:
    # upload_all_experiences(index_name=index_name, reddit_limit=100, studies_limit=50)
    
    # Search example:
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
        select=["health_disorder", "action", "outcomes", "url", "source_type"],
        top=5,
    )

    for number, result in enumerate(results):
        logger.info(f"VECTOR Result {number + 1}: {print(result)}")

    results = search_client.search(
        search_text=query,
        vector_queries=[vector_query],
        select=["health_disorder", "action", "outcomes", "url", "source_type"],
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
