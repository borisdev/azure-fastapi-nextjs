"""
LLM Clustering
"""

from typing import Optional

from jinja2 import Template
from openai import AzureOpenAI
from pydantic import BaseModel
from pydantic.fields import Field
from rich import print
from rich.console import Console
from rich.table import Table

from website.chain import Chain, endpoints
from website.settings import console

console = Console()


def is_member(*, llm_name: str, topic_1: str, topic_2: str) -> bool:
    """
    Job
    ====

    Determine if topic_1 and topic_2 are clear scientific subsets of one another or near duplicates?

    Only return True or False. Any other response will be considered invalid.

    Error on the side of caution. If you are unsure, return False.

    Motivating problem
    ==================

    The answer will be user to merge topics into larger clusters of topics to
    get rid off near duplicate clusters that came from the clustering software.


    Its AMBIGUOUS if low carb and ketogenic diet are the same or different.

    Examples (Doc test cases)
    =========================

    >>> is_member_by_o1_llm(topic_1="Follow a ketogenic diet and exercise regularly to manage glucose levels.", topic_2="Following a ketogenic diet")
    True
    >>> is_member_by_o1_llm(topic_1="Brewer Diet", topic_2="Following a ketogenic diet")
    False
    >>> is_member_by_o1_llm(topic_1="Omega-3 Fatty Acids", topic_2="Following a ketogenic diet")
    False
    >>> is_member_by_o1_llm(topic_1="Increased protein intake while maintaining a caloric deficit", topic_2="Following a ketogenic diet")
    False
    >>> is_member_by_o1_llm(topic_1="Maintaining a calorie deficit while breastfeeding by ensuring adequate protein and micronutrient intake", topic_2="Following a ketogenic diet")
    False
    >>> is_member_by_o1_llm(topic_1="Seed cycling in smoothies", topic_2="Following a ketogenic diet")
    False
    >>> is_member_by_o1_llm(topic_1="Ketogenic diet with electrolyte replacement", topic_2="Following a ketogenic diet")
    True
    >>> is_member_by_o1_llm(topic_1="Increased protein intake", topic_2="Following a ketogenic diet")
    False
    >>> is_member_by_o1_llm(topic_1="Protein-Supplemented Very-Low-Calorie Diet", topic_2="Following a ketogenic diet")
    False
    >>> is_member_by_o1_llm(topic_1="Controlled carb intake to manage mealtime blood sugar levels during pregnancy", topic_2="Following a ketogenic diet")
    False
    >>> is_member_by_o1_llm(topic_1="Intermittent Fasting (IF)", topic_2="Following a ketogenic diet")
    False
    >>> is_member_by_o1_llm(topic_1="Low-Carbohydrate Diet", topic_2="Following a ketogenic diet")
    False
    >>> is_member_by_o1_llm(topic_1="Low carb diet", topic_2="Following a ketogenic diet")
    False
    >>> is_member_by_o1_llm(topic_1="Going keto", topic_2="Following a ketogenic diet")
    True
    >>> is_member_by_o1_llm(topic_1="Implement dietary changes to manage acid reflux", topic_2="Following a ketogenic diet")
    False
    >>> is_member_by_o1_llm(topic_1="Follow a ketogenic diet (keto) for weight loss", topic_2="Following a ketogenic diet")
    True
    >>> is_member_by_o1_llm(topic_1="strict keto-style diet", topic_2="Following a ketogenic diet")
    True
    >>> is_member_by_o1_llm(topic_1="Incorporating more vegetables and healthy ingredients into meals, such as soups, stews, and salads.", topic_2="Following a ketogenic diet")
    False
    >>> is_member_by_o1_llm(topic_1="Incorporating nutrient-dense foods like salmon and liver into the diet during pregnancy", topic_2="Following a ketogenic diet")
    False

    """
    if llm_name == "o1-mini":
        return is_member_by_o1_llm(topic_1=topic_1, topic_2=topic_2)
    else:
        raise ValueError(f"Invalid LLM name: {llm_name}")


instructions = """

    Instructions
    =============


    Return True if a functional medicine doctor will think that TOPIC_1 and TOPIC_2
    clearly are near duplicates or if one is a clear scientific subset of the other.

    Only return True or False. Any other response will be considered invalid.

"""


def is_member_by_o1_llm(*, topic_1: str, topic_2: str) -> bool:
    """
    2 of 19 tests failed
    on low carb and ketogenic diet
    """
    llm_name = "o1-mini"
    o1_client = AzureOpenAI(
        azure_endpoint=endpoints[llm_name],
        api_key="62ef467f1d4f435f8aa4d2b105bbf44e",
        api_version=endpoints[llm_name].split("api-version=")[-1],
    )

    o1_prompt_template = Template(
        """

        {{instructions}}


        INPUT DATA
        =============


        TOPIC_1
        ------------------------

        {{topic_1}}


        TOPIC_2
        ------------------------

        {{topic_2}}

    """
    )
    rendered_prompt = o1_prompt_template.render(
        topic_1=topic_1, topic_2=topic_2, instructions=instructions
    )
    response = o1_client.chat.completions.create(
        model=llm_name,
        messages=[
            {
                "role": "user",
                "content": rendered_prompt,
            },
        ],
        max_completion_tokens=5000,
    )
    o1_answer = response.choices[0].message.content
    if o1_answer == "True":
        return True
    elif o1_answer == "False":
        return False
    else:
        raise ValueError(f"Invalid response from LLM: {o1_answer}")


class NearDupeResponse(BaseModel):
    # BASIC ONE
    answer: bool = Field(
        title="Near Duplicate",
        description=f"""

            Instructions
            =============


            Return True if a functional medicine doctor will think that TOPIC_1 and TOPIC_2
            clearly are near duplicates or if one is a clear scientific subset of the other.

            Only return True or False. Any other response will be considered invalid.
            """,
    )


class NearDupeResponseV2(BaseModel):
    near_dupe: bool = Field(
        title="Near Duplicate",
        description=f"""

            Instructions
            =============

            Are TOPIC_1 and TOPIC_2, more or less, about the same general biohack or treatment?

            In other words, should they be included in the same chapter of our book on biohacking?

            Only return True or False. Any other response will be considered invalid.

            """,
    )
    consensus: bool = Field(
        title="Clear Consensus",
        description=f"""
            Will a group of functional doctors easily agree that the main
            treatment or biohack in TOPIC_1 and TOPIC_2 are essentially
            synonymous or near duplicates?

            If there could easily be a debate, then this should be False.
            """,
    )

    @property
    def answer(self) -> bool:
        return self.near_dupe and self.consensus


class NearDupeResponseV3(BaseModel):
    # NEW ONE
    answer: bool = Field(
        title="Near Duplicate",
        description=f"""

            Context
            =======

            You are helping a scientist organize his observational data for a research
            article on the outcomes of different biohacking treatment experiements that
            ordinary people reported to him. You are helping him by grouping together
            his outcome data into similar biohacking and treatment topics.

            Instructions
            =============

            Return True if a functional medicine doctor will think that TOPIC_1 and TOPIC_2
            clearly are near duplicates or if one is a clear scientific subset of the other.
            In other words, return True when it makes sense that the outcomes of the grouped
            actions can be aggregated because they come from similar enough mechansims.
            Otherwise, return False.

            Only return True or False. Any other response will be considered invalid.

            """,
    )


class NearDupeInput(BaseModel):
    topic_1: str
    topic_2: str
    expected_answer: Optional[bool] = None


class NearDupeChain(Chain):
    input_schema = NearDupeInput
    output_schema = NearDupeResponse

    @classmethod
    def make_input_text(cls, *, input: NearDupeInput) -> str:
        input_template = Template(
            """
            TOPIC_1: {{topic_1}}


            TOPIC_2: {{topic_2}}

        """
        )
        input_text = input_template.render(
            topic_1=input.topic_1,
            topic_2=input.topic_2,
        )
        return input_text


class NearDupeChainV2(NearDupeChain):
    input_schema = NearDupeInput
    output_schema = NearDupeResponseV2


class NearDupeChainV3(NearDupeChain):
    input_schema = NearDupeInput
    output_schema = NearDupeResponseV3


class NearDupeInputChunk(BaseModel):
    input_objects: list[NearDupeInput]

    @classmethod
    def from_input_objects(
        cls, input_objects: list[NearDupeInput]
    ) -> "NearDupeInputChunk":
        return cls(input_objects=input_objects)


class NearDupeScore(BaseModel):
    same_mechanism: bool
    same_action: bool
    same_personal_context: bool


class NearDupeResponseChunk(BaseModel):
    answers: list[bool] = Field(
        title="Near Duplicate",
        # description=f"""
        #
        #     Instructions
        #     =============
        #
        #     Return the True or False near duplicate answer for each pair of topics.
        #
        #     Return True if a functional medicine doctor will think that TOPIC_1 and TOPIC_2
        #     clearly are near duplicates or if one is a clear scientific subset of the other.
        #
        #     Only return True when you are very confident, otherwise return False.
        #
        #     Never return True when you see two distinct personal contexts in the pair of topics.
        #
        #     """,
        description=f"""

            Instructions
            =============

            For each pair A and B of biohack treatments return True if you are certain A and B are near duplicates, otherwise return False.
            Only return True when you are very confident, otherwise return False.
            Never return True when you see two distinct personal contexts in the pair of topics.
            It is very dangerous for people's health if you say True about a pair that is not a near duplicate.
            Error on the side of caution and return False if you are unsure.

            """,
    )

    def responses(self) -> list[NearDupeResponse]:
        # fascade pattern
        responses = []
        for answer in self.answers:
            responses.append(NearDupeResponse(answer=answer))
        return responses


class NearDupeResponseChunkV2(NearDupeResponseChunk):
    answers: list[bool] = Field(
        title="Same search result",
        description=f"""

            Instructions
            =============

            For each pair of topics return True if its obvious that a biohacker would
            want to see them together in the same search result. Otherwise, return False.
            """,
    )


class NearDupeResponseChunkV3(NearDupeResponseChunk):
    answers: list[bool] = Field(
        title="Near Duplicate",
        description=f"""


            Context
            =======

            You are trying to reduce the noise in a biohacking search engine by
            merging near duplicate search results, but at the same time
            maximizing the recall by retaining the relevant diversity of the
            results.

            Our users are biohackers who are desparately searching for interventional
            treatments to improve their health. They will be very frustrated if they
            see the same search results over and over again. But they will also be ecstatic
            if they can find a needle in the haystack that can help their personal, unique
            health situation.

            Instructions
            =============

            For each pair of these pairs of search results return True if its obvious that
            the pair are near duplicates. Otherwise, return False.

            Pointers
            --------

            - users want to see distinct personal contexts in the search
            results, so don't say a pair is a near duplicate if the personal
            context is different
            - when the interventional actions are only different by some minor
            details, then the pair is a near duplicate.
            - Two different broad topics in the public perception are never
            near duplicates since they are different entrypoints to knowledge.
            - A detailed search result that is a clear subset of a broader
            search result is a near duplicate.

            """,
    )


class NearDupeResponseChunkV4(BaseModel):
    answers: list[bool] = Field(
        title="Duplicate Diet Names",
        description=f"""
            Write True if Diet Name A and Diet Name B can be interchanged in a sentence without changing the meaning.
            Otherwise, write False.
            Be very conservative in labeling two diet names as duplicates since they can have different meanings in different contexts and an error can be dangerous to our users.
            Each key component of the diet name must be the same for the diet names to be considered duplicates.
            Only return True when you are very confident, otherwise return False.
            """,
    )

    def responses(self) -> list[NearDupeResponse]:
        # fascade pattern
        responses = []
        for answer in self.answers:
            responses.append(NearDupeResponse(answer=answer))
        return responses


class NearDupeChainChunk(Chain):
    input_schema = NearDupeInputChunk
    output_schema = NearDupeResponseChunk

    @classmethod
    def make_input_text(cls, *, input: NearDupeInputChunk) -> str:
        input_text = ""
        for input_object in input.input_objects:
            input_template = Template(
                """
                A.{{topic_1}} B.{{topic_2}}
                """
            )
            input_text += input_template.render(
                topic_1=input_object.topic_1,
                topic_2=input_object.topic_2,
            )
        return input_text


class NearDupeChainChunkV2(NearDupeChainChunk):
    input_schema = NearDupeInputChunk
    output_schema = NearDupeResponseChunkV2


class NearDupeChainChunkV3(NearDupeChainChunk):
    input_schema = NearDupeInputChunk
    output_schema = NearDupeResponseChunkV3


class NearDupeChainChunkV4(NearDupeChainChunk):
    input_schema = NearDupeInputChunk
    output_schema = NearDupeResponseChunkV4

    @classmethod
    def make_input_text(cls, *, input: NearDupeInputChunk) -> str:
        input_text = ""
        for input_object in input.input_objects:
            input_template = Template(
                """
                Diet Name A. {{topic_1}}
                Diet Name B. {{topic_2}}
                """
            )
            input_text += input_template.render(
                topic_1=input_object.topic_1,
                topic_2=input_object.topic_2,
            )
        return input_text


if __name__ == "__main__":
    # poetry run python is_member_by_o1_llm.py -v
    # pytest --doctest-modules is_member_by_o1_llm.py -v
    # import doctest
    #
    # doctest.testmod()
    print("Running tests")
    import asyncio

    input_objects = [
        NearDupeInput(
            topic_1="Follow a ketogenic diet and exercise regularly to manage glucose levels.",
            topic_2="Following a ketogenic diet",
            expected_answer=True,
        ),
        NearDupeInput(
            topic_1="Brewer Diet",
            topic_2="Following a ketogenic diet",
            expected_answer=False,
        ),
        NearDupeInput(
            topic_1="Omega-3 Fatty Acids",
            topic_2="Following a ketogenic diet",
            expected_answer=False,
        ),
        NearDupeInput(
            topic_1="Increased protein intake while maintaining a caloric deficit",
            topic_2="Following a ketogenic diet",
            expected_answer=False,
        ),
        NearDupeInput(
            topic_1="Maintaining a calorie deficit while breastfeeding by ensuring adequate protein and micronutrient intake",
            topic_2="Following a ketogenic diet",
            expected_answer=False,
        ),
        NearDupeInput(
            topic_1="Seed cycling in smoothies",
            topic_2="Following a ketogenic diet",
            expected_answer=False,
        ),
        NearDupeInput(
            topic_1="Ketogenic diet with electrolyte replacement",
            topic_2="Following a ketogenic diet",
            expected_answer=True,
        ),
        NearDupeInput(
            topic_1="Increased protein intake",
            topic_2="Following a ketogenic diet",
            expected_answer=False,
        ),
        NearDupeInput(
            topic_1="Protein-Supplemented Very-Low-Calorie Diet",
            topic_2="Following a ketogenic diet",
            expected_answer=False,
        ),
        NearDupeInput(
            topic_1="Controlled carb intake to manage mealtime blood sugar levels during pregnancy",
            topic_2="Following a ketogenic diet",
            expected_answer=False,
        ),
        NearDupeInput(
            topic_1="Intermittent Fasting (IF)",
            topic_2="Following a ketogenic diet",
            expected_answer=False,
        ),
        NearDupeInput(
            topic_1="Low-Carbohydrate Diet",
            topic_2="Following a ketogenic diet",
            expected_answer=False,
        ),
        NearDupeInput(
            topic_1="Low carb diet",
            topic_2="Following a ketogenic diet",
            expected_answer=False,
        ),
        NearDupeInput(
            topic_1="Going keto",
            topic_2="Following a ketogenic diet",
            expected_answer=True,
        ),
        NearDupeInput(
            topic_1="Implement dietary changes to manage acid reflux",
            topic_2="Following a ketogenic diet",
            expected_answer=False,
        ),
        NearDupeInput(
            topic_1="Follow a ketogenic diet (keto) for weight loss",
            topic_2="Following a ketogenic diet",
            expected_answer=True,
        ),
        NearDupeInput(
            topic_1="strict keto-style diet",
            topic_2="Following a ketogenic diet",
            expected_answer=True,
        ),
        NearDupeInput(
            topic_1="Incorporating more vegetables and healthy ingredients into meals, such as soups, stews, and salads.",
            topic_2="Following a ketogenic diet",
            expected_answer=False,
        ),
        NearDupeInput(
            topic_1="Incorporating nutrient-dense foods like salmon and liver into the diet during pregnancy",
            topic_2="Following a ketogenic diet",
            expected_answer=False,
        ),
        NearDupeInput(
            topic_1="Incorporating nutrient-dense foods like salmon and liver into the diet during pregnancy",
            topic_2="Following a ketogenic diet",
            expected_answer=False,
        ),
        # advanced examples
        NearDupeInput(
            topic_1="16/8 fasting",
            topic_2="Atkins diet",
            expected_answer=False,
        ),
        # Atkins diet IS a near dupe of 1940s USDA diet
        NearDupeInput(
            topic_1="Atkins diet",
            topic_2="1940s USDA diet",
            expected_answer=True,
        ),
    ]
    size = 25
    max_tokens = 100
    max_retries = 1
    timeout = 5
    llm_name = "gpt-4o"

    chunk_chains = [
        NearDupeChainChunk,
        NearDupeChainChunkV2,
        NearDupeChainChunkV3,
        NearDupeChainChunkV4,
    ]
    chains = [
        NearDupeChain,
        NearDupeChainV2,
        NearDupeChainV3,
    ] + chunk_chains
    table = Table(title="Near Duplicate Accuracy by LLM Chain")
    table.add_column("Chain")
    table.add_column("Percent Correct")
    table.add_column("Failed")
    table.add_column("Succeeded")
    table.add_column("Total")

    import itertools

    for chain in chains:
        print(f"Cluster test invoked for chain, {chain.__name__}")

        # just one chunk of 25 examples in the input_objects
        # below is wrapper to normalize the input_objects and responses of the chunk chain
        # so its in line with the other chains
        if chain in chunk_chains:
            # normalize the input
            # a bit overkill for just one chunk...but its an example for the future
            chunked_input_objects = itertools.batched(input_objects, 10)
            chunked_input_objects = [
                NearDupeInputChunk.from_input_objects(chunk)
                for chunk in chunked_input_objects
            ]
            responses = asyncio.run(
                chain.batch_predict(
                    size=size,
                    llm_name=llm_name,
                    input_objects=chunked_input_objects,
                    max_tokens=max_tokens,
                    max_retries=max_retries,
                    timeout=timeout,
                )
            )
        else:
            responses = asyncio.run(
                chain.batch_predict(
                    size=size,
                    llm_name=llm_name,
                    input_objects=input_objects,
                    max_tokens=max_tokens,
                    max_retries=max_retries,
                    timeout=timeout,
                )
            )
        if chain in chunk_chains:
            responses = responses[0].responses()
        examples_where_llm_fails = []
        for response, input_object in zip(responses, input_objects):

            success_couter = 0
            failure_counter = 0
            total = len(input_objects)
            if response.answer == input_object.expected_answer:
                pass
            else:
                examples_where_llm_fails.append((input_object, response))
        console.print(f"Log failed examples for {chain.__name__}")
        console.print("================================")
        print(examples_where_llm_fails)
        console.print("================================")
        failed = len(examples_where_llm_fails)
        succeeded = len(input_objects) - len(examples_where_llm_fails)
        total = len(input_objects)
        accuracy = 100 * (1 - len(examples_where_llm_fails) / len(input_objects))
        table.add_row(
            chain.__name__,
            f"{accuracy:.2f}%",
            str(failed),
            str(succeeded),
            str(total),
        )
    console.print(table)
