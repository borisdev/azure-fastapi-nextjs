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
