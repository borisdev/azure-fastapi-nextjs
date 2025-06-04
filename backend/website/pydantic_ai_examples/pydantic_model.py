"""Simple example of using PydanticAI to construct a Pydantic model from a text input.

Run with:

    uv run -m pydantic_ai_examples.pydantic_model
"""

import os
from typing import cast

import website.pydantic_ai_examples.config
from pydantic import BaseModel
# from pydantic_ai import Agent
from pydantic_ai.models import KnownModelName
from website.pydantic_ai_examples.config import Agent


class MyModel(BaseModel):
    city: str
    country: str


model = cast(KnownModelName, os.getenv("PYDANTIC_AI_MODEL", "openai:gpt-4o"))
print(f"Using model: {model}")
agent = Agent(model, result_type=MyModel, instrument=True)

if __name__ == "__main__":
    result = agent.run_sync("The windy city in the US of A.")
    print(result.data)
    print(result.usage())
