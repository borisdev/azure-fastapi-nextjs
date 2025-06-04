"""
JUST USE OUTCOMES

- maybe pre-score outcomes
- maybe do funniest and scariest outcomes
- maybe pre-score outcomes, actions, personal_context, mechanisms???
"""

import asyncio
from typing import Optional

from jinja2 import Template
from openai import AzureOpenAI
from opensearch_dsl import Search
from opensearchpy import (Document, Keyword, OpenSearch, Search, Text,
                          exceptions)
from pydantic import BaseModel, Field
from rich import print

from website.deep_experiences import DeepExperience
from website.llm import LLM, endpoints
from website.settings import (console, opensearch_client,
                              opensearch_experience_index)

index_name = opensearch_experience_index

llm_name = "o1-preview"  # "01-mini"
client = AzureOpenAI(
    azure_endpoint=endpoints[llm_name],
    api_key="62ef467f1d4f435f8aa4d2b105bbf44e",
    api_version=endpoints[llm_name].split("api-version=")[-1],
)
template_1 = Template(
    """
    Your Job
    --------

    Step 1:

    As input to your task, read the the below collection on personal
    experiences related to the question, "{{question}}" for the topic of {{topic_title}}.

    Step 2:

    Find those personal experiences that are most unexpected compared
    your knowledge of the medical consensus on the question, "{{question}}" for the topic of {{topic_title}}.

    Step 3:

    Report your findings in a summarized form as a list of what you
    think will be most important for our readers when they are trying to
    experiment with new biohacking options for the question, "{{question}}" for the topic of {{topic_title}}.

    Next to each finding you report cite the relevant items by referring to
    their `permalink` in parentheses.

    Input: Collection of Personal Experiences from Reddit
    ---------------------------------------------------------

    {% for experience in experiences %}

        {{ experience }}

        ----------------

    {% endfor %}

    Output Guidelines
    ----------

    - Use one simple declarative sentence to describe each finding in your list.
    - The output should be a JSON list of strings where each string is a finding.

"""
)
template_2 = Template(
    """
    Synthesize the most interesting findings from the search results
    the will clearly help the user answer her question, "{{question}}" for the topic of {{topic_title}}.


    Input: Collection of Personal Experiences from Reddit
    ---------------------------------------------------------

    {% for experience in experiences %}

        {{ experience }}

        ----------------

    {% endfor %}

    Output Guidelines
    ----------

    - Use one simple declarative sentence to describe each finding in your list.
    - Next to each finding you report cite the relevant items by referring to their `permalink` in parentheses.
    - The output should be a JSON list of strings where each string is a finding.

"""
)


class FindingwithSourceHacks(BaseModel):
    # from unstructured text
    finding: str
    permalinks: list[str]


class ListTopFindingsResponse(BaseModel):
    # from unstructured text
    # use gpt-4o
    findings: list[FindingwithSourceHacks] = Field(
        title="Finding and Hacks",
        description="""
            Structure the text of findings into a list of findings with associated source post ids.
        """,
    )


async def ask_ai(*, topic_title: str, question: str):

    # Use causal dag and recursions
    response = InferredQuestionsGenerator.predict(
        input_object=InputSearch(topic_title=topic_title, raw_search=question),
        llm_name="gpt-4o",
    )
    print(response)
    input_objects = []
    questions = response.questions + [question]
    questions = [question] + response.questions
    for question_str in questions:
        input_object = Question(topic=topic_title, question=question_str)
        input_objects.append(input_object)
    responses = await DeepQuestionsGenerator.batch_predict(
        size=100, llm_name="gpt-4o", input_objects=input_objects
    )
    print(responses)
    for response in responses[0:1]:

        s = Search(using=opensearch_client, index=index_name).query(
            "bool",
            should=[
                {"match": {"outcomes": response.outcomes}},
                {"match": {"action": response.action}},
                {"match": {"personal_context": response.personal_context}},
                {"match": {"mechanism": response.mechanism}},
            ],
        )
        response = s.execute()

        deep_experiences = []
        for hit in response:
            print(hit.__dict__)
            # console.print(hit, style="info")
            deep_experience = DeepExperience(**hit.__dict__["_d_"])
            deep_experiences.append(deep_experience)
        print(deep_experiences)

        input_text = template_1.render(
            question=question,
            topic_title=topic_title,
            experiences=deep_experiences,
        )
        # input_text = template_2.render(
        #     question=question,
        #     topic_title=topic_title,
        #     experiences=deep_experiences,
        # )
        llm_name = "o1-preview"  # "01-mini"
        llm_name = "o1-mini"
        llm_name = "gpt-4o"
        llm_name = "gpt-4o-mini"

        response = client.chat.completions.create(
            model=llm_name,
            messages=[
                {
                    "role": "user",
                    "content": input_text,
                },
            ],
            max_completion_tokens=5000,
        )

        if response.choices[0].message.content is None:
            raise ValueError("No response from the `Most Interesting Findings` prompt")
        else:
            ai_overview = response.choices[0].message.content.strip()
            print(ai_overview)
        print(question)
        print(questions)


if __name__ == "__main__":
    answer = asyncio.run(
        ask_ai(topic_title="Sleep", question="How can I improve my REM sleep?")
    )
    print(answer)
