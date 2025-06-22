from __future__ import annotations

import asyncio
import os
import time
from collections import defaultdict
from typing import Any, Iterable, Literal, Optional

from azure.search.documents.models import VectorizedQuery
from dotenv import load_dotenv
from jinja2 import Template
from loguru import logger
from pydantic import BaseModel, Field
# from opensearch_dsl import Search
from rich import print
from rich.traceback import install
from website.chain import Chain

# install(show_locals=True)
install()

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

    # deduplicate experiences


def dedupe_experiences(experiences: Iterable[Experience]) -> None:
    existing = set()
    deduplicated = []
    for experience in experiences:
        action_outcome = f"{experience.action} {experience.outcomes}"
        if action_outcome not in existing:
            deduplicated.append(experience)
            existing.add(action_outcome)
    experiences = deduplicated


def experiences2biohacks(
    experiences: Iterable[Experience],
) -> list[DynamicBiohack]:
    """
    Group experiences into dynamic biohacks.
    """
    dedupe_experiences(experiences)
    d = {}
    for experience in experiences:
        experience = clean(experience)
        if experience.biohack_topic not in d:
            d[experience.biohack_topic] = []
        d[experience.biohack_topic].append(experience)

    dynamic_biohacks = []
    for k, v in d.items():
        dynamic_biohack = DynamicBiohack(
            biohack_topic=k,
            experiences=v,
        )
        dynamic_biohacks.append(dynamic_biohack)
    return dynamic_biohacks


async def enrich_biohacks(
    *,
    biohacks: list[DynamicBiohack],
    question: str,
    batch_size: int,
    llm_name: str,
    max_tokens: int,
    max_retries: int,
    timeout: int,
    start: int = 0,
    size: Optional[int] = None,
) -> list[DynamicBiohack]:

    question = question.strip()

    class Output(BaseModel):
        relevant: bool = Field(
            default=False,
            title="Relevant",
            description="""
                Write True if the health hack is relevant to the user's question, otherwise False.
                A relevant health hack must meet the following criteria:
                1. The health hack must be related to the user's question.
                2. The health hack must be interesting or effective enough to be worth mentioning.
                3. The health hack must be actionable, meaning the user can take steps to implement it.
            """,
        )
        why_care: Optional[str] = Field(
            default=None,
            title="Why matters",
            description=f"""
            Look at the health hack experiences and summarize in one concise sentence
            the most impoertant takeaway for the user based on her health optimization, {question}.
            Leave your response empty if the health hack is not relevant to the user's question.
                """,
        )

    class Input(BaseModel):
        question: str
        biohack: DynamicBiohack

    class EnrichChain(Chain):

        output_schema = Output
        input_schema = Input

        @classmethod
        def make_input_text(cls, *, input: Input) -> str:
            prompt_template = """

                User's SEARCH_BAR_TEXT
                ******************************

                {{question}}


                Biohack name: {{ biohack.biohack_topic }}
                -------------------------------------------

                Experiences:
                -----------------------------

                {% for experience in biohack.experiences %}
                    ------------------------------------------

                    Source: {{ experience.source_type }}
                    Action: {{ experience.action }}
                    Outcomes: {{ experience.outcomes }}
                    Disorder: {{ experience.health_disorder }}

                    ------------------------------------------
                {% endfor %}
            """
            template = Template(prompt_template)
            prompt = template.render(question=input.question, biohack=input.biohack)
            return prompt

    input_objects = [Input(question=question, biohack=biohack) for biohack in biohacks]
    responses = await EnrichChain.batch_predict(
        size=batch_size,  # 300
        llm_name=llm_name,
        input_objects=input_objects,
        max_tokens=max_tokens,  # 100
        max_retries=max_retries,  # 0
        timeout=timeout,  # 1
    )
    enriched_biohacks = []

    for biohack, response in zip(biohacks, responses):
        if not isinstance(response, Output):
            continue  # Skip if response is not of type Output
        if not response.relevant:
            continue
        if response.why_care is None or response.why_care.strip() == "":
            continue  # Skip if why_care is not empty
        biohack.why_care = response.why_care.strip()

        print(biohack.why_care)
        enriched_biohacks.append(biohack)
    return enriched_biohacks


def enriched_biohacks_to_taxonomy(
    enriched_biohacks: list[DynamicBiohack],
) -> DynamicBiohackingTaxonomy:
    """
    Convert a list of enriched biohacks into a DynamicBiohackingTaxonomy.

    Args:
        enriched_biohacks: List of DynamicBiohack objects that have been enriched with why_care

    Returns:
        DynamicBiohackingTaxonomy: Organized taxonomy grouped by biohack type
    """
    # Group biohacks by their biohack_type
    biohack_type2biohack = defaultdict(list)
    all_experiences = []

    for biohack in enriched_biohacks:
        biohack_type2biohack[biohack.biohack_type].append(biohack)
        all_experiences.extend(biohack.experiences)

    # Create BiohackTypeGroup objects
    biohack_type_groups: list[BiohackTypeGroup] = []
    for biohack_type, biohacks in biohack_type2biohack.items():
        biohack_type_group = BiohackTypeGroup(
            biohack_type=biohack_type, biohacks=biohacks
        )
        biohack_type_groups.append(biohack_type_group)

    # Calculate counts
    count_experiences = len(all_experiences)
    count_reddits = sum(
        1 for experience in all_experiences if experience.source_type == "reddit"
    )
    count_studies = sum(
        1 for experience in all_experiences if experience.source_type == "study"
    )

    # Create and return the taxonomy
    taxonomy = DynamicBiohackingTaxonomy(
        biohack_types=biohack_type_groups,
        count_experiences=count_experiences,
        count_reddits=count_reddits,
        count_studies=count_studies,
    )

    return taxonomy


async def run_search_and_enrich(
    *,
    question: str,
    client,
    limit: int = 100,
    batch_size: int = 300,
    llm_name: str = "gpt-4o",
    max_tokens: int = 100,
    max_retries: int = 0,
    timeout: int = 1,
) -> DynamicBiohackingTaxonomy:
    """
    Run a search query and enrich the results with LLM.
    """
    experiences = run_search_query(question=question, client=client, limit=limit)
    biohacks = experiences2biohacks(experiences)
    enriched_biohacks = await enrich_biohacks(
        biohacks=biohacks,
        question=question,
        batch_size=batch_size,
        llm_name=llm_name,
        max_tokens=max_tokens,
        max_retries=max_retries,
        timeout=timeout,
    )
    taxonomy = enriched_biohacks_to_taxonomy(enriched_biohacks)
    return taxonomy


if __name__ == "__main__":
    question = "Iron and pregnancy"
    limit = 20
    start = time.time()
    experiences = run_search_query(
        question=question, client=azure_search_client, limit=limit
    )
    biohacks = experiences2biohacks(experiences)
    enriched_biohacks = asyncio.run(
        enrich_biohacks(
            biohacks=biohacks,
            question=question,
            batch_size=300,
            llm_name="gpt-4o",
            max_tokens=100,
            max_retries=0,
            timeout=1,
        )
    )
    print(enriched_biohacks)
    print(
        f"N experiences: {len(experiences)} --> N biohacks: {len(biohacks)} --> N enriched biohacks: {len(enriched_biohacks)}"
    )

    # Convert enriched biohacks to taxonomy
    taxonomy = enriched_biohacks_to_taxonomy(enriched_biohacks)
    print(f"Taxonomy with {len(taxonomy.biohack_types)} biohack types")
    print(f"Total experiences: {taxonomy.count_experiences}")
    print(f"Reddit experiences: {taxonomy.count_reddits}")
    print(f"Study experiences: {taxonomy.count_studies}")

    end = time.time()
    print(f"Time taken: {end - start} seconds")

    taxonomy = asyncio.run(
        run_search_and_enrich(
            question=question,
            client=azure_search_client,
            limit=limit,
            batch_size=300,
            llm_name="gpt-4o",
            max_tokens=100,
            max_retries=0,
            timeout=1,
        )
    )
    print(f"Taxonomy with {len(taxonomy.biohack_types)} biohack types")
