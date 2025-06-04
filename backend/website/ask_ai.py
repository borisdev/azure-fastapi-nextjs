from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from website.chain import Chain
from website.experiences import Experience


class AnswerResponseSchema(BaseModel):
    answer: Optional[str] = Field(
        default=None,
        title="Answer",
        description="""
            Clearly explain how the given biohacking experiences informs the question.

            Don't make anything up beyond what you see in the experiences.

            If you are not 100% sure the experiences are relevant to the question, leave its blank.

            You must quickly get the point so our reader can quickly judge if she should invest
            time by clicking to read the full details.

            Never use flowery language or marketing language. Be concrete and to the point.
        """,
    )
    score: Optional[float] = Field(
        default=None,
        title="Score",
        description="""
            On a scale of 0 to 5 how confident are you that these experiences are relevant to the question?
        """,
    )


class QuestionAndTopicAndExperiences(BaseModel):
    question: str
    topic: str
    experiences: list[Experience]


class AskAIChain(Chain):

    input_schema = QuestionAndTopicAndExperiences
    output_schema = AnswerResponseSchema

    @classmethod
    def make_input_text(cls, *, input: QuestionAndTopicAndExperiences) -> str:
        experiences = "\n".join(
            [
                experience.model_dump_json(
                    indent=2,
                    include={
                        "takeaway",
                        "action",
                        "health_disorder",
                        "outcomes",
                        "personal_context",
                    },
                )
                for experience in input.experiences
            ]
        )
        input_text = f"""
            Topic: Biohacking your {input.topic}

            Question: {input.question}

            Experiences
            ------------

            {experiences}
        """
        return input_text


if __name__ == "__main__":
    topic = "Sleep"
