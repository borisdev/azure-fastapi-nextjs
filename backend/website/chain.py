from __future__ import annotations

import asyncio
import itertools
import random
from abc import ABCMeta, abstractmethod
from time import sleep
from typing import Any, ClassVar, Iterable, Optional, Type, Union

import instructor
from instructor.exceptions import InstructorRetryException
from loguru import logger
from openai import (APIConnectionError, AsyncAzureOpenAI, AzureOpenAI,
                    BadRequestError)
from pydantic import BaseModel, Field, ValidationError
from rich import print
from rich.console import Console
from rich.theme import Theme
from rich.traceback import install
from website import settings

install()

custom_theme = Theme({"info": "dim cyan", "warning": "magenta", "danger": "bold red"})
console = Console(theme=custom_theme)

backup_endpoints = {}

# endpoint="https://boris-m3ndov9n-eastus2.openai.azure.com/",
# api_version="2024-12-01-preview",
# https://boris-m3ndov9n-eastus2.cognitiveservices.azure.com/openai/deployments/text-embedding-3-large/embeddings?api-version=2023-05-15'
endpoints = {
    # "gpt-4o-mini": "https://openai-rg-nobsmed.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-02-15-preview",
    "gpt-4o-mini": "https://west-us-4000-quota-gpt-4o-mini.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-08-01-preview",
    "gpt-4o": "https://openai-rg-nobsmed.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2023-03-15-preview",
    "text-embedding-3-large": "https://boris-m3ndov9n-eastus2.cognitiveservices.azure.com/openai/deployments/text-embedding-3-large/embeddings?api-version=2023-05-15",
    # "text-embedding-3-large": "https://openai-rg-nobsmed.openai.azure.com/openai/deployments/text-embedding-3-large/embeddings?api-version=2023-05-15",
    "text-embedding-3-small": "https://openai-rg-nobsmed.openai.azure.com/openai/deployments/text-embedding-3-small/embeddings?api-version=2023-05-15",
    "o1-preview": "https://openai-rg-nobsmed.openai.azure.com/openai/deployments/o1-preview/chat/completions?api-version=2024-08-01-preview",
    "o1-mini": "https://openai-rg-nobsmed.openai.azure.com/openai/deployments/o1-mini/chat/completions?api-version=2024-08-01-preview",
    "o3-mini": "https://boris-m3ndov9n-eastus2.openai.azure.com/",
}


class Chain(BaseModel, metaclass=ABCMeta):
    """
    Define

    - input schema
    - output schema
    - prompt generation
    - LLM base model

    >>> cls.predict()
    >>> await cls.batch_predict()
    """

    input_schema: ClassVar[Type[Any]]
    output_schema: ClassVar[Type[Any]]

    @classmethod
    @abstractmethod
    def make_input_text(cls, *, input: Any) -> str:
        pass

    @classmethod
    def make_inputs(cls, *, input_objects: list[Type[BaseModel]]) -> list[str]:
        for input_object in input_objects:
            check = isinstance(input_object, cls.input_schema)
            if check is False:
                print("input object")
                print(input_object)
                print("input schema")
                print(cls.input_schema)
                raise ValueError(f"input object is not of type {cls.input_schema()}")
        prompts = [
            cls.make_input_text(input=input_object) for input_object in input_objects
        ]
        return prompts

    @classmethod
    def make_client(
        cls, llm_name: str, timeout: Union[int, None], sync: bool = False
    ) -> Union[AsyncAzureOpenAI, AzureOpenAI]:
        endpoint = endpoints[llm_name]

        if llm_name == "o3-mini":
            api_version = "2024-12-01-preview"
        else:
            api_version = endpoint.split("api-version=")[-1]

        if "west" in endpoint:
            api_key = settings.west_api_key
        elif "boris-m3ndov9n-eastus2" in endpoint:
            api_key = settings.eastus2_api_key
        else:
            api_key = settings.api_key

        if sync is False:
            deployment_client = instructor.from_openai(
                AsyncAzureOpenAI(
                    api_version=api_version,
                    azure_endpoint=endpoint,
                    azure_deployment=llm_name,
                    api_key=api_key,
                    timeout=timeout,
                )
            )
        else:
            deployment_client = instructor.patch(
                AzureOpenAI(
                    api_version=api_version,
                    azure_endpoint=endpoint,
                    azure_deployment=llm_name,
                    api_key=api_key,
                    timeout=timeout,
                )
            )
        return deployment_client  # type: ignore

    @classmethod
    async def coroutine(
        cls,
        *,
        client,
        llm_name: str,
        prompt: str,
        max_retries: int,
        max_tokens: int,
        reasoning_effort: Optional[str] = None,
    ) -> Any:
        try:
            if reasoning_effort is not None:
                result = await client.chat.completions.create(  # type: ignore
                    model=llm_name,
                    messages=[
                        {"role": "user", "content": prompt},
                    ],
                    response_model=cls.output_schema,
                    max_retries=max_retries,
                    # max_tokens=max_tokens,
                )
            else:
                result = await client.chat.completions.create(  # type: ignore
                    model=llm_name,
                    messages=[
                        {"role": "user", "content": prompt},
                    ],
                    response_model=cls.output_schema,
                    max_retries=max_retries,
                    max_tokens=max_tokens,
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

    @classmethod
    async def batch_predict(
        cls,
        *,
        max_tokens: int,
        size: int,
        llm_name: str,
        timeout: Union[int, None],
        max_retries: int,
        input_objects: Iterable[Any],
        reasoning_effort: Optional[str] = None,
        **kwargs,
    ) -> list[Any]:
        responses = []
        batch_size = size
        name = cls.__name__
        try:
            input_objects_batches = list(itertools.batched(input_objects, batch_size))
        except Exception as e:
            print(input_objects)
            print(batch_size)
            print(e)
            breakpoint()
        # new client for each batch
        client = cls.make_client(llm_name, sync=False, timeout=timeout)
        for idx, input_objects_batch in enumerate(input_objects_batches):

            console.print(
                f"{name} idx {idx}/{len(input_objects_batches)} - batch size: {batch_size}",
                style="info",
            )

            prompts = cls.make_inputs(input_objects=input_objects_batch, **kwargs)
            tasks = []
            for prompt in prompts:
                # print(prompt)
                task = asyncio.create_task(
                    cls.coroutine(
                        client=client,
                        llm_name=llm_name,
                        prompt=prompt,
                        max_tokens=max_tokens,
                        max_retries=max_retries,
                        reasoning_effort=reasoning_effort,
                    )
                )
                tasks.append(task)

            try:
                responses.extend(await asyncio.gather(*tasks))
            except APIConnectionError as e:
                logger.warning(f"You batch {size} is too big? ...retrying {e}")
                raise Exception(f"error in batch predict: {e}")
            except Exception as e:
                # TOO MANY OPEN FILES
                logger.warning(f"error in batch predict: {e}")
        errors = [r for r in responses if isinstance(r, Exception)]
        N = len(errors)
        if N > 0:
            logger.warning(f"batch run for {name}: {N} errors")
        # client.close()
        return responses

    @classmethod
    def predict(
        cls,
        *,
        max_tokens: Optional[int] = None,
        llm_name: str,
        input_object: Any,
        timeout: int,
        **kwargs,
    ) -> Any:
        client = cls.make_client(llm_name, sync=True, timeout=timeout)

        prompts = cls.make_inputs(input_objects=[input_object])
        prompt = prompts[0]
        print(prompt)
        try:
            response = client.chat.completions.create(  # type: ignore
                model=llm_name,
                temperature=0.0,
                messages=[
                    {"role": "user", "content": prompt},
                ],
                response_model=cls.output_schema,
                max_retries=3,
                max_tokens=max_tokens,
            )
        except BadRequestError as e:
            print(prompt)
            logger.error(f"error in predict: {e}")
            response = e

        return response


async def example():
    class InputSchema(BaseModel):
        sentence: str

    class OutputSchema(BaseModel):
        completion: str = Field(
            title="completion",
            description="Answer the question in the given text",
        )

    class TestChain(Chain):

        input_schema = InputSchema
        output_schema = OutputSchema

        @classmethod
        def make_input_text(cls, *, input: InputSchema) -> str:
            return f"Question: {input.sentence}"

    response = TestChain.predict(
        max_tokens=5000,
        llm_name="gpt-4o-mini",
        input_object=InputSchema(
            sentence="How do I output all files in a directory using Python?"
        ),
    )
    console.print(response, style="info")

    sentences = [
        "How do I output all files in a directory using Python?",
        "How do I output all files in a directory using Python?",
        "How do I output all files in a directory using Python?",
    ]
    input_objects = [InputSchema(sentence=sentence) for sentence in sentences]
    responses = await TestChain.batch_predict(
        max_tokens=5000,
        size=3,
        timeout=30,
        max_retries=3,
        batch_size=50,
        llm_name="gpt-4o-mini",
        input_objects=input_objects,
    )
    print(responses)


if __name__ == "__main__":
    asyncio.run(example())
