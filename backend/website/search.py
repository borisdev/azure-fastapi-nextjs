"""
OpenAI embeddings take .5 secs versus .1 for local embeddings
Remember to add hybrid search with scoring one day
Rememeber to add query highlights one day
embedding_pipeline = "all-MiniLM-L6-v2-AND-text-embedding-3-large"
embedding_experiences_reindex(client=client, embedding_pipeline=embedding_pipeline)
SleepDoc.rehydrate_index(
    topics=["Biohacking", "Sleep"],
    limit=None,
    use_client=client,
    embedding_pipeline="all-MiniLM-L6-v2-AND-text-embedding-3-large",
)
"""

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
from opensearchpy import (Date, DenseVector, Document, InnerDoc, Integer,
                          Keyword, Nested, Object, OpenSearch, Search, Text,
                          exceptions, helpers)
from pydantic import BaseModel, Field
from rich import print
from rich.traceback import install

from website.chain import Chain, endpoints
from website.experiences import Experience
from website.models import (AISummary, BiohackTypeGroup, DynamicBiohack,
                            DynamicBiohackingTaxonomy)
from website.settings import azure_search_client, console

load_dotenv()
azure_openai_api_key = os.environ["AZURE_OPENAI_API_KEY"]
from openai import AsyncAzureOpenAI, AzureOpenAI

from website.settings import west_api_key

# install(show_locals=True)
install()


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


# from azure.core.credentials import AzureKeyCredential

# credential = AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"])
# service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]

from langchain_openai import AzureOpenAIEmbeddings

openai_large = AzureOpenAIEmbeddings(
    # Usage examples:
    # vector = openai_large.embed_query(text)
    # vectors = openai_large.embed_documents(input_texts)
    azure_deployment="text-embedding-3-large",
    openai_api_version="2024-02-01",  # pyright: ignore
    azure_endpoint="https://openai-rg-nobsmed.openai.azure.com/",
    api_key=os.environ["API_KEY"],
)


def run_search_query(*, question: str, client, limit: int):
    console.print(f"Client: {client}", style="info")
    console.print(f"Searching for: {question}", style="info")

    vector_query = VectorizedQuery(
        vector=openai_large.embed_query(question),
        k_nearest_neighbors=10,
        fields="health_disorderVector",
    )

    results = client.search(
        vector_queries=[vector_query],
        # select=["health_disorder", "action", "outcomes", "url"],
        top=limit,
    )
    experiences = []
    for hit in results:
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


async def summary_chain(*, taxonomy: DynamicBiohackingTaxonomy, question: str):

    biohacks = []
    for biohack_type_group in taxonomy.biohack_types:
        if biohack_type_group and hasattr(biohack_type_group, "biohacks"):
            for biohack in biohack_type_group.biohacks:
                biohacks.append(biohack)

    llm_name = "o3-mini"
    prompt_template = """

        User's SEARCH_BAR_TEXT
        ******************************

        {{question}}


        Biohacking research results
        ******************************

        {% for biohack in biohacks %}
            ===========================================
            Biohack name: {{ biohack.biohack_topic }}
            -------------------------------------------

                Outcomes:
                -----------------------------

                {% for experience in biohack.experiences %}
                    {{ experience.outcomes }}
                {% endfor %}


                Mechanisms: {{ biohack.mechanisms }}


        {% endfor %}


    """
    template = Template(prompt_template)
    prompt = template.render(
        question=question,
        biohacks=biohacks,
    )

    class Plan(BaseModel):
        cool: list[str] = Field(
            default=[],
            title="Cool biohacking outcomes",
            description=f"""
                List and describe the top coolest biohacking outcomes that pertain to the user's SEARCH_BAR_TEXT, {question}.
                Cool biohacking outcomes are those that are surprising, novel, unexpected, humorous, and/or super impactful.
                Make your writing pertain to the user's SEARCH_BAR_TEXT, {question}.
                Don't be flowery or verbose, just quickly get to the point.

                Surround the name of all mechanisms and biohacks with <b> </b> tags, such as
                "<b>Taking melatonin</b>, in one case, led to..."
                Just write down the specific facts and details and let the user
                draw her own conclusions.
                Never write opinionated phrases like "demonstrating surprising endurance" or "which stands out as an unexpectedly dramatic outcome"
                Don't repeat yourself. Each biohack topic should never be see on more than one item in the list.
                """,
        )
        contra: list[str] = Field(
            default=[],
            title="Contradictory biohacking outcomes",
            description=f"""
                List and describe situations where the same biohack (treatment)
                has led to contradictory outcomes in different cases.
                In other words the same action had positive outcomes in some cases
                and negative outcomes in others.
                Make your writing pertain to the user's SEARCH_BAR_TEXT, {question}.
                Don't be flowery or verbose, just quickly get to the point.
                Surround the name of all mechanisms and biohacks with <b> </b> tags, such as
                "<b>Taking melatonin</b>, in one case, led to..."
                Just write down the specific facts and details and let the user
                draw her own conclusions.
                Don't repeat yourself. Each biohack topic should never be see on more than one item in the list.
                """,
        )
        balance: list[str] = Field(
            default=[],
            title="Balance biohacks",
            description=f"""
                List and describe biohacks that will balance against the user's
                intended direction (or implicit premise)  based on her SEARCH_BAR_TEXT,
                {question}.

                For example, if the user is asking about "Vegetarian diet and pregnancy", your response could be:

                    "Omega-3 fatty acid supplementation led to decreased
                    infant birth defects so consider taking non-vegetarian
                    sources of Omega-3 fatty acids."


                Make your writing pertain to the user's SEARCH_BAR_TEXT, {question}.
                Don't be flowery or verbose, just quickly get to the point.
                Surround the name of all mechanisms and biohacks with <b> </b> tags, such as
                "<b>Taking melatonin</b>, in one case, led to..."
                Never give advice.
                Just write down the specific facts and details and let the user
                draw her own conclusions.
                Each biohack topic should never be see on more than one item in the list.
                Don't repeat yourself. Each biohack topic should never be seen on more than one item in the list.
                """,
        )
        mechanisms: list[str] = Field(
            default=[],
            title="Mechanisms, top pathways and factors",
            description=f"""
                List and describe the top mechanisms of action of the biohacks that pertain to the user's SEARCH_BAR_TEXT, {question}.

                Make your writing pertain to the user's SEARCH_BAR_TEXT, {question}.
                Don't be flowery or verbose, just quickly get to the point.
                Surround the name of all mechanisms and biohacks with <b> </b> tags, such as
                "<b>Insulin uptake</b> is a mechanism of action of <b>Metformin</b> and <b>Berberine</b>."
                Never give advice.
                Just write down the specific facts and details and let the user draw her own conclusions.
                Don't repeat yourself. Each mechanism should never be seen on more than one item in the list.
                """,
        )

    try:
        openai = AzureOpenAI(
            api_version="2024-12-01-preview",
            azure_endpoint="https://boris-m3ndov9n-eastus2.openai.azure.com/",
            azure_deployment=llm_name,
            api_key=azure_openai_api_key,
        )
        logfire.instrument_openai(openai)
        llm_client = instructor.patch(openai)

        completion_config = {
            "model": llm_name,
            "messages": [{"role": "user", "content": prompt}],
            "response_model": Plan,
            "reasoning_effort": "low",
        }

        response = llm_client.chat.completions.create(**completion_config)
        return response
    except Exception as e:
        error_msg = f"Whoops...error generating AI summary: {str(e)}"
        logger.error("LLM exception in summary_chain o3-mini")
        logger.error(f"Error details: {e}")
        return error_msg


async def balance_task(
    *, llm_name, llm_client, taxonomy: DynamicBiohackingTaxonomy, question: str
):

    biohacks = []
    for biohack_type_group in taxonomy.biohack_types:
        if biohack_type_group and hasattr(biohack_type_group, "biohacks"):
            for biohack in biohack_type_group.biohacks:
                if biohack.balance:
                    biohacks.append(biohack)

    prompt_template = """

        User's SEARCH_BAR_TEXT
        ******************************

        {{question}}


        Biohacking research results
        ******************************

        {% for biohack in biohacks %}
            ===========================================
            Biohack name: {{ biohack.biohack_topic }}
            -------------------------------------------

                Outcomes:
                -----------------------------

                {% for experience in biohack.experiences %}
                    {{ experience.outcomes }}
                {% endfor %}

        {% endfor %}


    """
    template = Template(prompt_template)
    prompt = template.render(
        question=question,
        biohacks=biohacks,
    )

    class Plan(BaseModel):
        balance: list[str] = Field(
            default=[],
            title="Balance biohacks",
            description=f"""
                List and describe biohacks that will balance against the user's
                intended direction (or implicit premise)  based on her SEARCH_BAR_TEXT,
                {question}.

                For example, if the user is asking about "Vegetarian diet and pregnancy", your response could be:

                    "Omega-3 fatty acid supplementation led to decreased
                    infant birth defects so consider taking non-vegetarian
                    sources of Omega-3 fatty acids."


                Make your writing pertain to the user's SEARCH_BAR_TEXT, {question}.
                Don't be flowery or verbose, just quickly get to the point.
                Surround the name of all mechanisms and biohacks with <b> </b> tags, such as
                "<b>Taking melatonin</b>, in one case, led to..."
                Never give advice.
                Just write down the specific facts and details and let the user
                draw her own conclusions.
                Each biohack topic should never be see on more than one item in the list.
                Don't repeat yourself. Each biohack topic should never be seen on more than one item in the list.
                """,
        )

    try:
        completion_config = {
            "model": llm_name,
            "messages": [{"role": "user", "content": prompt}],
            "response_model": Plan,
            "reasoning_effort": "low",
        }
        if llm_name != "o3-mini":
            del completion_config["reasoning_effort"]
        response = await llm_client.chat.completions.create(**completion_config)
        return response
    except Exception as e:
        error_msg = f"Whoops...error generating AI summary: {str(e)}"
        logger.error("LLM exception in summary_chain o3-mini")
        logger.error(f"Error details: {e}")
        return error_msg


async def skeptical_task(
    *, llm_name, llm_client, taxonomy: DynamicBiohackingTaxonomy, question: str
):

    biohacks = []
    for biohack_type_group in taxonomy.biohack_types:
        if biohack_type_group and hasattr(biohack_type_group, "biohacks"):
            for biohack in biohack_type_group.biohacks:
                if biohack.skeptical:
                    biohacks.append(biohack)

    prompt_template = """

        User's SEARCH_BAR_TEXT
        ******************************

        {{question}}


        Biohacking research results
        ******************************

        {% for biohack in biohacks %}
            ===========================================
            Biohack name: {{ biohack.biohack_topic }}
            -------------------------------------------

                Outcomes:
                -----------------------------

                {% for experience in biohack.experiences %}
                    {{ experience.outcomes }}
                {% endfor %}

        {% endfor %}


    """
    template = Template(prompt_template)
    prompt = template.render(
        question=question,
        biohacks=biohacks,
    )

    class Plan(BaseModel):
        skeptical: list[str] = Field(
            default=[],
            title="Skeptical biohacks",
            description=f"""
                List and describe situations where the same biohack (treatment)
                has led to contradictory outcomes in different cases.
                In other words the same action had positive outcomes in some cases
                and negative outcomes in others.
                Make your writing pertain to the user's SEARCH_BAR_TEXT, {question}.
                Don't be flowery or verbose, just quickly get to the point.
                Surround the name of all mechanisms and biohacks with <b> </b> tags, such as
                "<b>Taking melatonin</b>, in one case, led to..."
                Just write down the specific facts and details and let the user
                draw her own conclusions.
                Don't repeat yourself. Each biohack topic should never be see on more than one item in the list.
                """,
        )

    try:
        completion_config = {
            "model": llm_name,
            "messages": [{"role": "user", "content": prompt}],
            "response_model": Plan,
            "reasoning_effort": "low",
        }
        if llm_name != "o3-mini":
            del completion_config["reasoning_effort"]

        response = await llm_client.chat.completions.create(**completion_config)
        return response
    except Exception as e:
        error_msg = f"Whoops...error generating AI summary: {str(e)}"
        logger.error("LLM exception in summary_chain o3-mini")
        logger.error(f"Error details: {e}")
        return error_msg


async def curious_task(
    *, llm_name, llm_client, taxonomy: DynamicBiohackingTaxonomy, question: str
):

    biohacks = []
    for biohack_type_group in taxonomy.biohack_types:
        if biohack_type_group and hasattr(biohack_type_group, "biohacks"):
            for biohack in biohack_type_group.biohacks:
                if biohack.curious:
                    biohacks.append(biohack)

    prompt_template = """

        User's SEARCH_BAR_TEXT
        ******************************

        {{question}}


        Biohacking research results
        ******************************

        {% for biohack in biohacks %}
            ===========================================
            Biohack name: {{ biohack.biohack_topic }}
            -------------------------------------------

                Outcomes:
                -----------------------------

                {% for experience in biohack.experiences %}
                    {{ experience.outcomes }}
                {% endfor %}

        {% endfor %}


    """
    template = Template(prompt_template)
    prompt = template.render(
        question=question,
        biohacks=biohacks,
    )

    class Plan(BaseModel):
        curious: list[str] = Field(
            default=[],
            title="Curious biohacks",
            description=f"""
                List and describe biohacks that will balance against the user's
                intended direction (or implicit premise)  based on her SEARCH_BAR_TEXT,
                {question}.

                For example, if the user is asking about "Vegetarian diet and pregnancy", your response could be:

                    "Omega-3 fatty acid supplementation led to decreased
                    infant birth defects so consider taking non-vegetarian
                    sources of Omega-3 fatty acids."


                Make your writing pertain to the user's SEARCH_BAR_TEXT, {question}.
                Don't be flowery or verbose, just quickly get to the point.
                Surround the name of all mechanisms and biohacks with <b> </b> tags, such as
                "<b>Taking melatonin</b>, in one case, led to..."
                Never give advice.
                Just write down the specific facts and details and let the user
                draw her own conclusions.
                Each biohack topic should never be see on more than one item in the list.
                Don't repeat yourself. Each biohack topic should never be seen on more than one item in the list.
                """,
        )

    try:
        completion_config = {
            "model": llm_name,
            "messages": [{"role": "user", "content": prompt}],
            "response_model": Plan,
            "reasoning_effort": "low",
        }
        if llm_name != "03-mini":
            del completion_config["reasoning_effort"]

        response = await llm_client.chat.completions.create(**completion_config)
        return response
    except Exception as e:
        error_msg = f"Whoops...error generating AI summary: {str(e)}"
        logger.error("LLM exception in summary_chain o3-mini")
        logger.error(f"Error details: {e}")
        return error_msg


async def mechanism_task(
    *, llm_name, llm_client, taxonomy: DynamicBiohackingTaxonomy, question: str
):

    biohacks = []
    for biohack_type_group in taxonomy.biohack_types:
        if biohack_type_group and hasattr(biohack_type_group, "biohacks"):
            for biohack in biohack_type_group.biohacks:
                biohacks.append(biohack)

    prompt_template = """

        User's SEARCH_BAR_TEXT
        ******************************

        {{question}}


        Biohacking research results
        ******************************

        {% for biohack in biohacks %}
            ===========================================
            Biohack name: {{ biohack.biohack_topic }}
            -------------------------------------------

                Mechanisms -> Outcomes
                -----------------------------

                {% for experience in biohack.experiences %}

                    Mechanisms: {{ experience.mechanism }} --> Outcomes: {{ experience.outcomes }}

                {% endfor %}


        {% endfor %}


    """
    template = Template(prompt_template)
    prompt = template.render(
        question=question,
        biohacks=biohacks,
    )

    class Plan(BaseModel):
        mechanisms: list[str] = Field(
            default=[],
            title="Mechanisms (pathways)",
            description=f"""
                Return a valid JSON array of what you see as the top common clusters of mechanisms (ie., pathways)  involved in the biohacks that can
                help the user in terms of her SEARCH_BAR_TEXT, {question}.

                Each item if the array must be a description of one cluster of mechanisms.

                Decribe in a manner that directly pertains to the user's SEARCH_BAR_TEXT, {question}.

                Surround the name of all mechanisms and biohacks with <b> </b> tags, such as
                "<b>Insulin uptake</b> is a mechanism of action of <b>Metformin</b> and <b>Berberine</b>."

                Never give advice.

                Just write down the specific facts and details and let the user draw her own conclusions.

                Don't repeat yourself.

                Explain the common causal mechanisms that play the biggest role in success.
                """,
        )

    try:
        completion_config = {
            "model": llm_name,
            "messages": [{"role": "user", "content": prompt}],
            "response_model": Plan,
            "reasoning_effort": "low",
        }
        if llm_name != "03-mini":
            del completion_config["reasoning_effort"]

        response = await llm_client.chat.completions.create(**completion_config)
        return response
    except Exception as e:
        error_msg = f"Whoops...error generating AI summary: {str(e)}"
        logger.error(error_msg)
        return error_msg


async def new_ai_summary(*, taxonomy: DynamicBiohackingTaxonomy, question: str):
    llm_name = "gpt-4o"
    llm_name = "o3-mini"
    if llm_name == "gpt-4o":
        endpoint = "https://openai-rg-nobsmed.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2023-03-15-preview"
        api_version = endpoint.split("api-version=")[-1]
        api_key = "62ef467f1d4f435f8aa4d2b105bbf44e"

    elif llm_name == "o3-mini":
        endpoint = "https://boris-m3ndov9n-eastus2.openai.azure.com"
        api_version = "2024-12-01-preview"
        api_key = azure_openai_api_key
    else:
        raise ValueError(f"Unknown LLM name: {llm_name}")

    openai = AsyncAzureOpenAI(
        max_retries=0,
        api_version=api_version,
        azure_endpoint=endpoint,
        azure_deployment=llm_name,
        api_key=api_key,
    )
    logfire.instrument_openai(openai)
    llm_client = instructor.patch(openai)
    responses = []
    tasks = []
    tasks.append(
        asyncio.create_task(
            balance_task(
                llm_name=llm_name,
                llm_client=llm_client,
                taxonomy=taxonomy,
                question=question,
            )
        )
    )
    tasks.append(
        asyncio.create_task(
            skeptical_task(
                llm_name=llm_name,
                llm_client=llm_client,
                taxonomy=taxonomy,
                question=question,
            )
        )
    )
    tasks.append(
        asyncio.create_task(
            curious_task(
                llm_name=llm_name,
                llm_client=llm_client,
                taxonomy=taxonomy,
                question=question,
            )
        )
    )
    # tasks.append(
    #     asyncio.create_task(
    #         mechanism_task(
    #             llm_name=llm_name,
    #             llm_client=llm_client,
    #             taxonomy=taxonomy,
    #             question=question,
    #         )
    #     )
    # )

    responses.extend(await asyncio.gather(*tasks))

    ai_summary = AISummary(
        balance=getattr(responses[0], "balance", []),
        skeptical=getattr(responses[1], "skeptical", []),
        curious=getattr(responses[2], "curious", []),
        # mechanisms=getattr(responses[3], "mechanisms", []),
        mechanisms=[],
    )
    return ai_summary


class EnrichBiohackInput(BaseModel):
    question: str
    biohack: DynamicBiohack


# balance, curious and skeptical are the same
prompt_template = """

    User's SEARCH_BAR_TEXT: {{question}}



    Biohack name: {{ biohack.biohack_topic }}
    ===========================================

        Outcomes:
        -----------------------------

        {% for experience in biohack.experiences %}
            Action: {{ experience.action }} -- LED TO --> Outcomes:{{ experience.outcomes }}
        {% endfor %}

"""


from instructor.exceptions import InstructorRetryException
from openai import AsyncAzureOpenAI, AzureOpenAI, BadRequestError
from pydantic import ValidationError


async def mechanism_coroutine_task_o3(
    *,
    client,
    llm_name: str,
    max_retries: int,
    max_tokens: int,
    question: str,
    biohack: DynamicBiohack,
) -> Any:
    class Response(BaseModel):
        mechanisms: list[str] = Field(
            default=[],
            title="Mechanisms (pathways)",
            description=f"""
                Describe the top mechanisms of the biohacks that pertain to the user's SEARCH_BAR_TEXT, {question}.
                Surround the name of all mechanisms and biohacks with <b> </b> tags, such as
                "<b>Insulin uptake</b> is a mechanism of action of <b>Metformin</b> and <b>Berberine</b>."
                Never give advice.
                Just write down the specific facts and details and let the user draw her own conclusions.
                Don't repeat yourself.
                Make this a mini-science lesson for our user to understand the common causal
                mechanisms that successful biohacks have in common.

                """,
        )

    prompt_template = """

        User's SEARCH_BAR_TEXT: {{question}}



        Biohack name: {{ biohackbiohack_topic }}
        ===========================================

            Outcomes:
            -----------------------------

            {% for experience in biohack.experiences %}
                Action: {{ experience.action }} --> Mechanism (Pathway): {{ experience.mechanism }} --> Outcomes: {{ experience.outcomes }}
            {% endfor %}

    """
    template = Template(prompt_template)
    prompt = template.render(question=question, biohack=biohack)

    try:
        completion_config = {
            "model": llm_name,
            "messages": [{"role": "user", "content": prompt}],
            "response_model": Response,
            "reasoning_effort": "low",
            "max_retries": max_retries,
            "max_tokens": max_tokens,
        }

        result = client.chat.completions.create(**completion_config)

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


async def mechanism_coroutine_task(
    *,
    client,
    llm_name: str,
    max_retries: int,
    # max_tokens: int,
    question: str,
    biohack: DynamicBiohack,
) -> Any:
    class Response(BaseModel):
        mechanisms: list[str] = Field(
            default=[],
            title="Mechanisms (pathways)",
            description=f"""
                Describe the top mechanisms of the biohacks that pertain to the user's SEARCH_BAR_TEXT, {question}.
                Surround the name of all mechanisms and biohacks with <b> </b> tags, such as
                "<b>Insulin uptake</b> is a mechanism of action of <b>Metformin</b> and <b>Berberine</b>."
                Never give advice.
                Don't be flowery or verbose, just quickly get to the point.
                Just write down the specific facts and details and let the user draw her own conclusions.
                Don't repeat yourself.
                We want the user to understand the common causal mechanisms that successful biohacks have in common
                in terms of the user's SEARCH_BAR_TEXT, {question}.
                """,
        )

    prompt_template = """

        User's SEARCH_BAR_TEXT: {{question}}



        Biohack name: {{ biohackbiohack_topic }}
        ===========================================

            Outcomes:
            -----------------------------

            {% for idx, experience in biohack.experiences %}
                Action: {{ experience.action }} --> Mechanism (Pathway): {{ experience.mechanism }} --> Outcomes: {{ experience.outcomes }}
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


def main(*, question: str, biohacks: list[DynamicBiohack]):
    llm_name = "o3-mini"
    endpoint = "https://boris-m3ndov9n-eastus2.openai.azure.com"
    api_version = "2024-12-01-preview"
    api_key = azure_openai_api_key

    llm_name = "gpt-4o"
    endpoint = "https://west-us-4000-quota-gpt-4o-mini.openai.azure.com/openai/deployments/gpt-4o/"
    api_version = "2024-11-20"
    api_key = west_api_key

    # "gpt-4o-mini": "https://west-us-4000-quota-gpt-4o-mini.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-08-01-preview",
    llm_name = "gpt-4o-mini"
    endpoint = "https://west-us-4000-quota-gpt-4o-mini.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-08-01-preview"
    api_version = "2024-08-01-preview"

    max_retries = 0
    max_tokens = 200
    tasks = []
    from openai import AsyncAzureOpenAI
    from pydantic_ai import Agent, RunContext
    from pydantic_ai.models.openai import OpenAIModel
    from pydantic_ai.providers.openai import OpenAIProvider

    client = AsyncAzureOpenAI(
        max_retries=0,
        api_version=api_version,
        azure_endpoint=endpoint,
        azure_deployment=llm_name,
        api_key=api_key,
    )
    logfire.instrument_openai(client)
    model = OpenAIModel(
        "gpt-4o",
        provider=OpenAIProvider(openai_client=client),
    )
    from dataclasses import dataclass

    @dataclass
    class RuntimeDependecies:
        biohack: DynamicBiohack

    system_prompt = """
        The health problem is: {question}
        What are the top actions and impacts of the biohack?
    """.strip()

    class ActionImpactResponse(BaseModel):
        impacts: list[str] = Field(
            title="Action impacts",
            description=f"""
                What are coolest impacts of the biohack that is being described?
                Don't be flowery or verbose, just quickly get to the point using words or short phrases.
                Don't repeat yourself.
                """,
        )

    agent = Agent(
        model,
        deps_type=RuntimeDependecies,
        result_type=ActionImpactResponse,
        system_prompt=system_prompt,
    )

    @agent.system_prompt
    async def add_biohack(ctx: RunContext[RuntimeDependecies]) -> str:
        # invoked to update the system prompt based on run time state (dependencies)
        return f"The diet intervention labels are {ctx.deps.biohack!r}"

    for biohack in biohacks:
        result = agent.run_sync(question, deps=RuntimeDependecies(biohack=biohack))
        print("========================")
        print("Biohack:", biohack.biohack_topic)
        print(result.data)


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
    limit = 250
    topic_index = "experiences_3"
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
    # ai_enrich_time = time.time() - start
    # print(f"AI enrich time: {ai_enrich_time}")
    # start = time.time()
    # # summary = asyncio.run(new_ai_summary(taxonomy=taxonomy, question=question))
    # biohacks = []
    # for biohack_type_group in taxonomy.biohack_types:
    #     for biohack in biohack_type_group.biohacks:
    #         biohacks.append(biohack)
    # main(question=question, biohacks=biohacks)
    # ai_summary_time = time.time() - start
    # print(f"Opensearch time: {opensearch_time}")
    # print(f"AI enrich time: {ai_enrich_time}")
    # print(f"AI summary time: {ai_summary_time}")
