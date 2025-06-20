from __future__ import annotations

import asyncio
import os
import time
from collections import defaultdict
from typing import Any, Iterable, Literal, Optional

from azure.search.documents.models import VectorizedQuery
from dotenv import load_dotenv
# from opensearch_dsl import Search
from rich import print
from rich.traceback import install

install(show_locals=True)
# install()

from langchain_openai import AzureOpenAIEmbeddings

from website.experiences import Experience
from website.models import (BiohackTypeGroup, DynamicBiohack,
                            DynamicBiohackingTaxonomy)
from website.settings import azure_search_client, console

openai_large = AzureOpenAIEmbeddings(
    # Usage examples:
    # vector = openai_large.embed_query(text)
    # vectors = openai_large.embed_documents(input_texts)
    azure_deployment="text-embedding-3-large",
    openai_api_version="2024-02-01",  # pyright: ignore
    azure_endpoint="https://openai-rg-nobsmed.openai.azure.com/",
    api_key=os.environ["API_KEY"],
)


def clean(experience: Experience):
    required_fields = {
        "rationale",
        "permalink",
        "action_score",
        "outcomes_score",
        "url",
        "action",
        "outcomes",
        "health_disorder",
        "mechanism",
        "personal_context",
        "takeaway",
        "biohack_type",
        "biohack_topic",
    }
    small_dict = experience.model_dump(include=required_fields)
    experience = Experience(**small_dict)
    return experience


def run_search_query(*, question: str, client, limit: int):
    console.print(f"Client: {client}", style="info")
    console.print(f"Searching for: {question}", style="info")

    vector_query = VectorizedQuery(
        vector=openai_large.embed_query(question),
        k_nearest_neighbors=limit,
        fields="health_disorderVector",
    )

    hybrid_results = client.search(
        vector_queries=[vector_query],  # shape similarity
        search_text=question,  # BM25 - probabilistic
        # select=["health_disorder", "action", "outcomes", "url"],
        top=limit,
    )
    experiences = []
    for hit in hybrid_results:
        experience = Experience(**hit)
        experience = clean(experience)
        experiences.append(experience)
    experiences = sorted(experiences, key=lambda x: x.score, reverse=True)
    print(experiences)
    return experiences


def make_taxonomy(
    *,
    experiences: list[Experience],
) -> DynamicBiohackingTaxonomy:
    start = time.time()
    # deduplicate experiences
    existing = set()
    deduplicated = []
    for experience in experiences:
        action_outcome = f"{experience.action} {experience.outcomes}"
        if action_outcome not in existing:
            deduplicated.append(experience)
            existing.add(action_outcome)
    experiences = deduplicated
    experiences = [clean(experience) for experience in experiences]

    dynamic_biohacks: list[DynamicBiohack] = []
    biohack_topic2experiences = defaultdict(list)
    pertinent_experiences = []
    for experience in experiences:
        experience = clean(experience)
        pertinent_experiences.append(experience)
        biohack_topic2experiences[experience.biohack_topic].append(experience)

    for k, v in biohack_topic2experiences.items():
        dynamic_biohack = DynamicBiohack(biohack_topic=k, experiences=v)
        dynamic_biohacks.append(dynamic_biohack)

    biohack_type2biohack = defaultdict(list)
    enriched_biohacks = []
    for biohack in dynamic_biohacks:
        enriched_biohacks.append(biohack)
        biohack_type2biohack[biohack.biohack_type].append(biohack)

    biohack_type_groups: list[BiohackTypeGroup] = []
    for biohack_type, biohacks in biohack_type2biohack.items():
        biohack_type_group = BiohackTypeGroup(
            biohack_type=biohack_type, biohacks=biohacks
        )
        biohack_type_groups.append(biohack_type_group)

    taxonomy = DynamicBiohackingTaxonomy(
        biohack_types=biohack_type_groups,
        count_experiences=len(pertinent_experiences),
        count_reddits=sum(
            [
                1
                for experience in pertinent_experiences
                if experience.source_type == "reddit"
            ]
        ),
        count_studies=sum(
            [
                1
                for experience in pertinent_experiences
                if experience.source_type == "study"
            ]
        ),
    )
    taxo_time = time.time() - start
    print(f"Taxo time: {taxo_time}")
    return taxonomy


if __name__ == "__main__":
    question = "Iron and pregnancy"
    limit = 100
    start = time.time()
    experiences = run_search_query(
        question=question, client=azure_search_client, limit=limit
    )
    taxonomy = make_taxonomy(experiences=experiences)
    print(taxonomy)
