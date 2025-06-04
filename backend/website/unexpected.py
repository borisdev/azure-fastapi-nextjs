from typing import Optional

from openai import AzureOpenAI
from pydantic import BaseModel, Field

from website.llm import LLM, endpoints

llm_name = "o1-preview"  # "01-mini"
client = AzureOpenAI(
    azure_endpoint=endpoints[llm_name],
    api_key="62ef467f1d4f435f8aa4d2b105bbf44e",
    api_version=endpoints[llm_name].split("api-version=")[-1],
)

template_1 = f"""
    Your Job
    --------

    Step 1:

    As input to your task, read the the below collection on personal
    experiences related to the health issue of {self.subreddit.title}.

    Step 2:

    Find those personal experiences that are most unexpected compared
    your knowledge of the medical consensus on treating {self.subreddit.title}.

    Step 3:

    Report your findings in a summarized form as a list of what you
    think will be most important for our readers when  trying a make a
    experiment with new options for {self.subreddit.title}.

    Next to each finding you report cite the relevant items by referring to their `source_post_id` in parentheses.

    Input: Collection of Personal Experiences from Reddit
    ---------------------------------------------------------

    {causal_relationships_str}

    Output Guidelines
    ----------

    - Use one simple declarative sentence to describe each finding in your list.
    - The output should be a JSON list of strings where each string is a finding.

"""
input_text = f"""
    Synthesize the most interesting findings from the search results
    the will clearly help the user in their biohacking journey.

    Step 1:
    ======

    As input to your synthesis task, read the the below collection of search
    results that were intended to be biohacking experiences of other
    people on the user's search question, "{question}" for the topic of {topic.title}.

    Step 2:
    ======


    Input: Collection of Personal Experiences from Reddit
    ---------------------------------------------------------

    {deep_experiences_str}

    Output Guidelines
    ----------

    - Use one simple declarative sentence to describe each finding in your list.
    - The output should be a JSON list of strings where each string is a finding.

"""


class FindingwithSourceHacks(BaseModel):
    # from unstructured text
    finding: str
    source_post_ids: list[str]


class ListTopFindingsResponse(BaseModel):
    # from unstructured text
    # use gpt-4o
    findings: list[FindingwithSourceHacks] = Field(
        title="Finding and Hacks",
        description="""
            Structure the text of findings into a list of findings with associated source post ids.
        """,
    )


# # o1 can't respond with structured JSON yet
# structured_findings = ListTopFindings.from_unstructured_text(
#     input_text=findings
# )
class InputSearch(BaseModel):
    topic: str
    raw_search: str


class InferredQuestionsResponse(BaseModel):
    questions: list[str] = Field(
        title="Inferred Questions",
        description="""
            You are an AI assistant for a website that helps people find biohacking experiences
            from other people and from clinical studies.

            Given the user's search string, Generate a list of inferred
            questions based on the user's search or question.

            Some guidleines for generating inferred questions:

            - think about both direct and indirect way to achieve the user's goal.
            - think variations in personal context.
            - think about variations in actions that target similar mechanisms.
            - think about variations in mechanisms that target similar outcomes.
            - think about the user's personal context.
            - think of rephrasing using synonyms that are medical terms and layman terms.
            - Be as simple and concise as possible.
        """,
    )


class InferredQuestionsGenerator(LLM):
    input_schema = InputSearch
    output_schema = InferredQuestionsResponse


class DeepQuestionResponse(BaseModel):
    mechanism: Optional[str] = Field(
        default=None,
        title="Medical Mechanism or Pathophysiology",
        description="""
            In seven or less words describe the medical mechanism or pathophysiology
            the author's search is inferring.

            Feel free to infer the medical mechanism or pathophysiology based on the author's search or question.
            """,
    )
    personal_context: Optional[str] = Field(
        default=None,
        title="Personal Context",
        description="""
            In seven or less words describe the personal context of the person asking the question or searching.

            Personal context can include the following:

                - age
                - sex
                - gender
                - weight
                - health condition
                - mental health condition
                - lifestyle
                - social context
                - demographic
                - developmental stage
                - professional context
                - environmental context


            Style Guide:

            - Be as concise as possible.
            - Don't guess.
            - You can infer the personal context based on the author's question or search.
                """,
    )
    action: Optional[str] = Field(
        default=None,
        title="Action (aka. Health or Performance Hack, Treatment, or Intervention)",
        description="""
            Using three of less words, extract the type of action the person asking the question or doing the search is looking for.

            A key action can include a new or a change in the following:

                - diet
                - device usage
                - exercise
                - sleep habit
                - medication
                - dosage
                - supplement
                - therapy
                - habit
                - lifestyle change
                - environment exposure
                - social context
                - physical training
                - mental training (meditation, cognitive therapy, etc.)

            Style Guide:
            ------------

            - If you are not sure the author is talking about a specific type of action or health performance hack, leave it blank.
            - Don't guess. Leave it blank if you are not certain.
            - Be as concise as possible.

        """,
    )
    outcomes: Optional[str] = Field(
        default=None,
        title="Outcomes",
        description="""
            In four words or less describe the health or performance effects that the author is looking for.


            Style Guide:
            ------------

            - Don't be flowery. Get to the point. Be concise.
            - You can infer the desired outcomes based on the author's question.
        """,
    )


class Question(BaseModel):
    topic: str
    question: str


class DeepQuestionsGenerator(LLM):

    input_schema = Question
    output_schema = DeepQuestionResponse

    @classmethod
    def make_input_text(cls, *, input: Question) -> str:
        input_text = f"""
            Topic: {input.topic}
            =================

            User's search for other people's biohacking experiences
            ------------------------------------------------------

            Search Query:

            {input.question}

        """
        return input_text


def ask_ai(topic_title: str, question: str):

    response = InferredQuestionsGenerator.predict(
        input_object=InputSearch(topic=topic_title, raw_search=question),
        llm_name="gpt-4o",
    )
    input_objects = []
    for question_str in response.questions:
        input_object = Question(topic=topic_title, question=question_str)
        input_objects.append(input_object)
    responses = await DeepQuestionsGenerator.batch_predict(
        size=3, llm_name="gpt-4o", input_objects=input_objects
    )
    print(responses)
    for response in responses:

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

        for hit in response:
            print(hit.__dict__)
            # console.print(hit, style="info")
            deep_experience = DeepExperience(**hit.__dict__["_d_"])
            deep_experiences.append(deep_experience)
            deep_experiences_str = [
                o.model_dump_json(indent=2) for o in deep_experiences[:25]
            ]

        # unexpected findings here
        print(input_text)
        llm_name = "o1-preview"  # "01-mini"
        llm_name = "o1-mini"
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
