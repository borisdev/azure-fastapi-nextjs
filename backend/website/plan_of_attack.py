import json
import os
from time import time

import instructor
from dotenv import load_dotenv
from loguru import logger
from openai import AzureOpenAI
from pydantic import BaseModel, Field
from rich import print

from website.search import DynamicBiohackingTaxonomy

load_dotenv()
azure_openai_api_key = os.environ["AZURE_OPENAI_API_KEY"]
from openai import AzureOpenAI


def plan_of_attack(*, question: str, taxonomy: DynamicBiohackingTaxonomy):

    prompt_template = f"""
        Search bar input
        ----------------

        {{question}}



        List of biohack_topic objects
        -----------------------------

        {{biohacks}}


    """
    file_path = "tests/fixtures/taxonomy_fixture.json"

    with open(file_path, "r") as f:
        taxonomy = DynamicBiohackingTaxonomy.model_validate_json(f.read())
    biohacks = []

    for biohack_types in taxonomy.biohack_types:
        for biohack in biohack_types.biohacks:
            # del biohack.relevance_score
            del biohack.answer
            for experience in biohack.experiences:
                del experience.id
                del experience.biohack_slug
                del experience.biohack_subtype
                del experience.health_disorder
                del experience.action
                del experience.biohack_type
                del experience.personal_context
                del experience.permalink
                del experience.takeaway
                del experience.clinical_trial_study
                del experience.action_tag
                del experience.action_embedding
                # del experience.action_score
                # del experience.outcomes_score
            biohacks.append(biohack.model_dump())

    biohacks_str = json.dumps(biohacks, indent=4)

    prompt = prompt_template.format(question=question, biohacks=biohacks_str)
    print(prompt)
    # llm_name = "gpt-4o-mini" # too slow
    llm_name = "o3-mini"

    class MiniBiohack(BaseModel):
        biohack: str = Field(
            title="causal biohack",
            description="""
                The name of the `biohack_topic` that made a big impact.
                You must only use the
                name of the biohack_topic you see that was provided.
                Do not use any other names or terms.
                """,
        )
        outcome: str = Field(
            title="Interesting Outcome",
            description="""
                In as few words as possible, what is the big outcome of this biohack?
                """,
        )

    class Plan(BaseModel):
        top_biohack_topics: list[MiniBiohack] = Field(
            title="Top Biohack Topics",
            description="""
                List the top 7 most interesting or powerful outcomes and the biohack
                topic that made it possible.
                """,
        )

    openai = AzureOpenAI(
        api_version="2024-12-01-preview",
        azure_endpoint="https://boris-m3ndov9n-eastus2.openai.azure.com/",
        azure_deployment=llm_name,
        api_key=azure_openai_api_key,
    )
    llm_client = instructor.patch(openai)

    completion_config = {
        "model": llm_name,
        "messages": [{"role": "user", "content": prompt}],
        "response_model": Plan,
        # "reasoning_effort": "low",
    }

    logger.info("Waiting for completion from LLM  -- might take a couple of minutes")
    start = time()
    response = llm_client.chat.completions.create(**completion_config)
    end = time()
    logger.info(f"LLM took {end - start} seconds")
    return response


# LLM o3
# Plan(
#     top_biohack_topics=[
#         MiniBiohack(biohack_topic='Ketogenic Diet Initiatives for Health and Weight Management'),
#         MiniBiohack(biohack_topic='Low-Carb Baking and Alternative Recipe Innovations'),
#         MiniBiohack(biohack_topic='Meal Prepping Strategies for Time-Efficient Nutrition'),
#         MiniBiohack(biohack_topic='Intermittent Fasting Combined with Low-Carb and Keto Strategies'),
#         MiniBiohack(biohack_topic='Clean, Home-Cooked Whole Food Diets'),
#         MiniBiohack(biohack_topic='Elimination of Seed Oils in Favor of Natural Fats'),
#         MiniBiohack(biohack_topic='Ketogenic Diets with Varied Adaptations and Meal Planning')
#     ]
# )
