"""
Experiment to cluster using pydanticai agent

    * o1 clustering - high quality but very slow, no future keyword search
    * sklearn agglomerative clustering - low quality, dupe clusters
    * bert-topic dbscan  - medium quality, dupe clusters, wrong outliers
    * gpt4 pairwise similarity - medium quality, slow, progressivly worse?
    * this approach
    * bert-topic_simple BEST
"""

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional, Union

from loguru import logger
from openai import AsyncAzureOpenAI
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from rich import print
from rich.console import Console
from rich.theme import Theme
from rich.traceback import install
from website import settings
from website.chain import endpoints

install()
custom_theme = Theme({"info": "dim cyan", "warning": "magenta", "danger": "bold red"})
console = Console(theme=custom_theme)


def load_docs(
    *,
    biohack_type: str,
    topic: str,
    source_field: str,
):
    file_path = Path(f"{biohack_type}_{topic}_{source_field}.json")

    with open(file_path, "r") as f:
        docs = json.load(f)
        logger.debug(f"Loaded doc from {file_path}")
    return docs


endpoint = endpoints["gpt-4o-mini"]
api_version = endpoint.split("api-version=")[-1]
if "west" in endpoint:
    api_key = settings.west_api_key
elif "boris-m3ndov9n-eastus2" in endpoint:
    api_key = settings.eastus2_api_key
else:
    api_key = settings.api_key
client = AsyncAzureOpenAI(
    azure_endpoint=endpoint,
    api_version=api_version,
    api_key=api_key,
)

config = {
    "topic": "Pregnancy",
    "biohack_type": "diet",
    "source_field": "action",
}

docs = load_docs(**config)


@dataclass
class TaggingDependecies:
    ### Run time dependencies (also can hold state)
    broad_topics: list[str]


tag_agent = Agent(
    OpenAIModel("gpt-4o", openai_client=client),
    deps_type=TaggingDependecies,
    result_type=list[str],
    system_prompt=(
        "Annotate the following text with the matching diet intervention label(s)."
        "Only annotate with an existing label if its very clear, otherwise create a new label."
        "Proper names should be their own distinct label."
    ),
)


## invoked to update the system prompt based on run time state (dependencies)
@tag_agent.system_prompt
async def add_candidate_broad_topics(ctx: RunContext[TaggingDependecies]) -> str:
    return f"The diet intervention labels are {ctx.deps.broad_topics!r}"


### Run time dependencies (also can hold state)
tagging_dependencies = TaggingDependecies(broad_topics=["fasting"])

doc2tags = {}

for idx, doc in enumerate(docs):
    result = tag_agent.run_sync(doc, deps=tagging_dependencies)
    broad_topics = tagging_dependencies.broad_topics
    broad_topics.extend(result.data)
    broad_topics = list(set(broad_topics))
    tagging_dependencies.broad_topics = broad_topics

    # Evaluate the results
    console.print(
        f"{idx} of {len(docs)}. [blue]{doc}[/blue] -> [green]{result.data}[/green] , [yellow]{len(tagging_dependencies.broad_topics)}[/yellow]"
    )
    doc2tags[doc] = result.data

file_path = Path(
    f"{config['biohack_type']}_{config['topic']}_{config['source_field']}_tags.json"
)
with open(file_path, "w") as f:
    json.dump(doc2tags, f)
    logger.success(f"Saved doc to {file_path}")


if __name__ == "__main__":
    # change to action_keywords (or intervention keywords)
    # allow one experience to have many action_keywords
    pass
