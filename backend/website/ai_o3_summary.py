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

    responses.extend(await asyncio.gather(*tasks))

    ai_summary = AISummary(
        balance=getattr(responses[0], "balance", []),
        skeptical=getattr(responses[1], "skeptical", []),
        curious=getattr(responses[2], "curious", []),
        # mechanisms=getattr(responses[3], "mechanisms", []),
        mechanisms=[],
    )
    return ai_summary
