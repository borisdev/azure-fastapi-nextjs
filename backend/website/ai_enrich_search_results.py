from __future__ import annotations

import asyncio
import os
import time
from collections import defaultdict
from typing import Any, Iterable, Literal, Optional

import instructor
import logfire
from azure.search.documents.models import VectorizedQuery
from dotenv import load_dotenv
from jinja2 import Template
from loguru import logger
from openai import AzureOpenAI
# from opensearch_dsl import Search
from pydantic import BaseModel, Field
from rich import print
from rich.traceback import install

install(show_locals=True)
# install()

from website.chain import Chain, endpoints
from website.experiences import Experience
from website.models import (AISummary, BiohackTypeGroup, DynamicBiohack,
                            DynamicBiohackingTaxonomy)
from website.settings import azure_search_client, console

load_dotenv()
azure_openai_api_key = os.environ["AZURE_OPENAI_API_KEY"]
from langchain_openai import AzureOpenAIEmbeddings
from openai import AsyncAzureOpenAI, AzureOpenAI

from website.settings import west_api_key

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


async def enrich_search_results_chain(
    *,
    experiences: list[Experience],
    question: str,
    batch_size: int,
    llm_name: str,
    max_tokens: int,
    max_retries: int,
    timeout: int,
    start: int = 0,
    size: Optional[int] = None,
) -> DynamicBiohackingTaxonomy:
    # deduplicate experiences
    existing = set()
    deduplicated = []
    for experience in experiences:
        action_outcome = f"{experience.action} {experience.outcomes}"
        if action_outcome not in existing:
            deduplicated.append(experience)
            existing.add(action_outcome)
    experiences = deduplicated

    question = question.strip()

    class PertinentResponse(BaseModel):
        success: bool = Field(
            default=False,
            title=f"Concrete example of treatment outcomes pertaining to {question}",
            description=f"""
                Answer True or False to the following question:

                Is this experience a concrete example of treatment outcomes pertaining to {question}?
                """,
        )

    class PertinentInput(BaseModel):
        question: str
        experience: Experience

    class PertinentChain(Chain):

        input_schema = PertinentInput
        output_schema = PertinentResponse

        @classmethod
        def make_input_text(cls, *, input: PertinentInput) -> str:
            input_text = f"""

            {input.experience.outcomes}

            """
            return input_text

    if size is None:
        size = len(experiences)
    logger.info(f"Size: {size}")
    logger.info(f"Start: {start}")
    input_objects = [
        PertinentInput(question=question, experience=experience)
        for experience in experiences[start : start + size]
    ]
    llm_start = time.time()
    responses = await PertinentChain.batch_predict(
        size=300,
        llm_name=llm_name,
        input_objects=input_objects,
        max_tokens=100,
        max_retries=0,
        timeout=1,
    )
    pertinent_experiences = []
    for experience, response in zip(experiences, responses):
        # prune irrelevant experiences
        try:
            if response.success:
                pertinent_experiences.append(experience)
        except Exception as e:
            logger.warning(f"Exception: {e}")
            logger.warning(f"Response: {response}")
            continue
        experience = clean(experience)
        pertinent_experiences.append(experience)
    experiences = pertinent_experiences

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

    enrich_time = time.time() - llm_start
    logger.info(f"Enrich time: {enrich_time}")
    start = time.time()

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


class EnrichBiohackInput(BaseModel):
    question: str
    biohack: DynamicBiohack


async def why_care_coroutine_task(
    *,
    client,
    llm_name: str,
    max_retries: int,
    # max_tokens: int,
    question: str,
    biohack: DynamicBiohack,
) -> Any:
    class Response(BaseModel):
        why_care: Optional[str] = Field(
            default=None,
            title="Why care about this biohack?",
            description=f"""
                As concisely as possible, in 2-3 sentences, tell the user why she should care about this biohack in the context of her SEARCH_BAR_TEXT, {question}.
                Just write down the specific facts and details and let the user draw her own conclusions.
                Never give advice.
                Clues that the user should care about this biohack include:

                    - Impactful
                    - Funny, novel, surprising, unexpected biohacks
                    - Adverse side effects
                    - Against conventional wisdom
                    - Contradictory outcomes

                If you are not sure you see a clear reason why the user should care about this biohack, just leave it blank.

                Never write opinionated phrases like "demonstrating surprising endurance" or "which stands out as an unexpectedly dramatic outcome". Just stick to the facts and get to the point.
                """,
        )

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
            Mechanism: {{ experience.mechanism }}
            Disorder: {{ experience.health_disorder }}

            ------------------------------------------
        {% endfor %}
    """

    template = Template(prompt_template)
    prompt = template.render(question=question, biohack=biohack)
    try:
        result = await client.chat.completions.create(  # type: ignore
            model=llm_name,
            messages=[
                {"role": "user", "content": prompt},
            ],
            response_model=Response,
            max_retries=max_retries,
            # max_tokens=max_tokens,
        )
    except InstructorRetryException as e:
        print(prompt)
        logger.warning(f"Retry Exception: {e}")
        return e
    except BadRequestError as e:
        print(prompt)
        logger.warning(f"Risky Content: {e}")
        return e
    except ValidationError as e:
        print(prompt)
        logger.warning(f"Validation error: {e}")
        return e
    except Exception as e:
        print(prompt)
        logger.error(f"Unknown Exception: {e}")
        # website.chain:coroutine:136 - Unknown Exception: Connection error.
        return e
    return result


if __name__ == "__main__":
    # Cross encoder will works to filter out very obvious non-relevant experiences, say .30 and below
    # https://github.com/UKPLab/sentence-transformers/blob/master/examples/applications/cross-encoder/cross-encoder_usage.py
    # ExperienceDoc3.re_create_index(use_client=client)
    # ExperienceDoc3.rehydrate_index(
    #     use_client=client, topics=["Biohacking", "Sleep", "Pregnancy"]
    # )
    # ExperienceDoc3.rehydrate_index_studies(use_client=client)
    question = "Flatulence"
    question = "REM sleep"
    question = "Vegetarian diet and pregnancy"
    question = "Iron and pregnancy"
    question = "Blueprint+diet"
    question = "Cancer and diet"
    question = "My Oura ring is showing a low REM score. What can I do to improve it?"
    limit = 100
    start = time.time()
    experiences = run_search_query(
        question=question, client=azure_search_client, limit=limit
    )
    # opensearch_time = time.time() - start
    # start = time.time()
    # taxonomy = asyncio.run(
    #     enrich_search_results_chain(
    #         question=question,
    #         experiences=experiences,
    #         batch_size=limit + 1,
    #         llm_name="gpt-4o-mini",
    #         max_tokens=200,
    #         max_retries=0,
    #         timeout=4,
    #     )
    # )
    taxonomy = make_taxonomy(experiences=experiences)
    # ai_enrich_time = time.time() - start
    # print(f"AI enrich time: {ai_enrich_time}")
    # start = time.time()
    summary = asyncio.run(new_ai_summary(taxonomy=taxonomy, question=question))
    print(summary)

    # biohacks = []
    # for biohack_type_group in taxonomy.biohack_types:
    #     for biohack in biohack_type_group.biohacks:
    #         biohacks.append(biohack)
    # main(question=question, biohacks=biohacks)
    # ai_summary_time = time.time() - start
    # print(f"Opensearch time: {opensearch_time}")
    # print(f"AI enrich time: {ai_enrich_time}")
    # print(f"AI summary time: {ai_summary_time}")
