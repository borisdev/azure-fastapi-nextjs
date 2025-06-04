# remember to add MECHANISMS for more indirect, backdoor, root cause biohacks

from __future__ import annotations

import asyncio
import itertools
import operator
from collections import defaultdict
from enum import Enum
from functools import reduce
from operator import attrgetter
from typing import (Annotated, Any, Iterable, Literal, Optional, Type, TypeVar,
                    Union)

import nest_asyncio
from loguru import logger
from opensearch_dsl import Search
from opensearchpy import (Document, InnerDoc, Integer, Keyword, Nested, Object,
                          OpenSearch, Search, Text, exceptions)
from pydantic import (BaseModel, BeforeValidator, ConfigDict, Field,
                      PlainSerializer, PrivateAttr, ValidationError)
from rich import print
from rich.console import Console
from rich.theme import Theme
# rich traceback
from rich.traceback import install
from slugify import slugify
from tqdm import tqdm

from website.base import Base
from website.chain import Chain
from website.experiences import (CommentExperiences, Experience,
                                 StudyExperiences, SubmissionExperiences)
from website.subreddit import (biohacker_subreddits, new_biohacker_subreddits,
                               pregnancy_subreddits, sleep_subreddits)

install()


class ExperienceAndTopic(BaseModel):
    experience: Experience
    topic: str


class ActionKeywordPhraseResponse(BaseModel):
    keyword_phrase: str = Field(
        title="Main Biohacking Intervention",
        description="""
            What is the most critical noun phrase required for organizing this sleep health hack?
            Use four words or less.
            Be as minimalistic as possible.
            Spell out abbreviations, then add the abbreviation in parentheses.

            Keep
            -----

            - Keep product names, brand names, devices, drug names, supplement names, therapy names, nootropic names.

            Drop
            -----

            - Drop general terms.
            - Drop adjectives.
            - Drop verbs.
            - Drop dosages and quantities.
            """,
    )


class KeywordPhraseInput(BaseModel):
    sentence: Union[str, None]


class ActionKeywordPhraseChain(Chain):

    input_schema = KeywordPhraseInput
    output_schema = ActionKeywordPhraseResponse

    @classmethod
    def make_input_text(cls, *, input: KeywordPhraseInput) -> str:
        input_text = f"""

            {input.sentence}

        """
        return input_text


class ActionClusterNameResponse(BaseModel):
    title: str = Field(
        title="Title",
        description="""
            In seven words or less, label the main biohacking intervention or treatment of the phrases.

            Guidelines:

            - Don't include the topic name.
            - Spell out acronyms in parentheses.
            - Use the least words possible.
        """,
    )


class OutcomeClusterNameResponse(BaseModel):
    title: str = Field(
        title="Title",
        description="""
            In five words or less, label the main health or performance outcome of the phrases.
            In other words, what is the main health or performance outcome that the author or study participants experienced
            as a result of the biohacking intervention or treatment?

            Guidelines:

            - Don't include the topic name.
            - Spell out acronyms in parentheses.
            - Use the least words possible.
        """,
    )


class HealthDisorderClusterNameResponse(BaseModel):
    title: str = Field(
        title="Title",
        description="""
            In five words or less, label the main medical health disorder of the phrases.

            Guidelines:

            - Don't include the topic name
            - Spell out acronyms in parentheses.
            - Use the least words possible.
        """,
    )


class KeywordClusterNameInput(BaseModel):
    topic: str
    sentences: list[str]


class KeywordClusterNameChain(Chain):

    input_schema = KeywordClusterNameInput
    output_schema = NotImplemented

    @classmethod
    def make_input_text(cls, *, input: KeywordClusterNameInput) -> str:
        sentences = "\n".join(input.sentences)
        input_text = f"""

            Phrases
            ----------------

            {sentences}

        """
        return input_text


class ActionClusterNameChain(KeywordClusterNameChain):

    output_schema = ActionClusterNameResponse


class OutcomeClusterNameChain(KeywordClusterNameChain):

    output_schema = OutcomeClusterNameResponse


class HealthDisorderClusterNameChain(KeywordClusterNameChain):

    output_schema = HealthDisorderClusterNameResponse


class ActionScoreResponse(BaseModel):
    score: int = Field(
        title="Is this a Biohacking Intervention?",
        description="""
            Is this a biohacking intervention?

            In other words, is this a method, technique, or product that a biohacker can partly
            replicate or use on their own mind or body to improve their own health performance?

            Provide an answer from 0 to 3.

            Scoring Guide:
            --------------

            0: Definitely No. This not a biohacking intervention.
            1: Maybe Yes or Maybe No. Its not clear whether this is a biohacking intervention.
            2: This is a biohacking intervention. But its hard to replicate or use.
            3: This is exactly what a biohacker likes to learn about. This is a biohacking intervention.

        """,
    )


class ActionScoreChain(Chain):

    input_schema = Experience
    output_schema = ActionScoreResponse

    @classmethod
    def make_input_text(cls, *, input: Experience) -> str:
        input_text = f"""

            {input.action}

        """
        return input_text


class OutcomesScoreResponse(BaseModel):
    score: int = Field(
        title="Specific, directly experienced health or performance outcomes?",
        description="""
            Are these specific health and performance outcomes that were
            directly experienced by the author or study participants?

            Provide an answer from 0 to 3.

            Scoring Guide:
            --------------

            0: Its not clear whether these are health or performance outcomes.
            1: These are health or performance outcomes, but not directly experienced.
            2: These are clear health or performance outcomes that were directly experienced.
            3: These are clear, specific, and compelling health or performance outcomes that were directly experienced.
        """,
    )


class OutcomesScoreChain(Chain):

    input_schema = Experience
    output_schema = OutcomesScoreResponse

    @classmethod
    def make_input_text(cls, *, input: Experience) -> str:
        input_text = f"""

            {input.outcomes}

        """

        return input_text


class BiohackSubtypeInput(BaseModel):
    action: Union[str, None]
    biohack_type: Union[str, None]


class BiohackSubtypeResponse(BaseModel):
    biohack_subtype: Optional[str] = Field(
        default=None,
        title="Biohack",
        description=f"""
            Extract the `BIOHACK_TYPE` from the text.

            This is the short interventional medical treatment term that you might find in the SNOMED CT database.

            Spell out acronyms in parentheses.
            Be as concise as possible.

            Drop all non-essential words in terms of identifying the general
            biohack intervention. For example, drop the following:

                - Drop generic phrases like "for better sleep"
                - Dop dosages and quantities.
                - Drop product versions.
                - Drop text describing the disorder like "...for insomnia"

            You are allowed to include a very short product name or brand name if that is the only specific biohack interventional treatment in the text.
            """,
    )


class BiohackSubtypeChain(Chain):

    input_schema = BiohackSubtypeInput
    output_schema = BiohackSubtypeResponse

    @classmethod
    def make_input_text(cls, *, input: BiohackSubtypeInput) -> str:
        input_text = f"""

        BIOHACK_TYPE: {input.biohack_type}

        {input.action}


        """
        return input_text


class TopicExperiences(Base):
    """
    30K sleep experiences
    2457 clusters of keywords
    """

    experiences: list[Experience]
    action_clusters: Optional[list[list[list[int]]]] = None
    health_disorder_clusters: Optional[list[list[list[int]]]] = None
    outcomes_clusters: Optional[list[list[list[int]]]] = None
    action_named_clusters: Optional[list[str]] = None
    health_disorder_named_clusters: Optional[list[str]] = None
    outcomes_named_clusters: Optional[list[str]] = None
    # parse mechanisms on a per biohack basis
    health_disorder_embeddings: Optional[list[list[float]]] = None
    action_embeddings: Optional[list[list[float]]] = None
    outcomes_embeddings: Optional[list[list[float]]] = None
    _action_embeddings: Any = PrivateAttr()
    _outcomes_embeddings: Any = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)

    def deduplicate_experiences(self) -> None:
        old_length = len(self.experiences)
        unique_experiences = []
        unique_permalinks = set()
        for experience in self.experiences:
            if experience.permalink not in unique_permalinks:
                unique_experiences.append(experience)
                unique_permalinks.add(experience.permalink)
        self.experiences = list(unique_experiences)
        self.save()
        print(f"Unique experiences: {len(unique_experiences)} down from {old_length}")

    async def extract_biohack_subtype(
        self,
        *,
        start: int,
        size: int,
        batch_size: int,
        llm_name: str,
        max_tokens: int,
        max_retries: int,
        timeout: int,
    ) -> None:
        # save the experiences after every 500 batch
        save_batch_size = 500
        experiences = self.experiences[start:size]
        experience_batches = list(itertools.batched(experiences, save_batch_size))
        number_of_batches = len(experience_batches)
        for idx, experience_batch in enumerate(experience_batches):
            print(f"Batch: {idx}/{number_of_batches} saving every {save_batch_size}")
            responses = await BiohackSubtypeChain.batch_predict(
                size=batch_size,
                llm_name=llm_name,
                input_objects=[
                    BiohackSubtypeInput(action=e.action, biohack_type=e.biohack_type)
                    for e in experience_batch
                ],
                max_tokens=max_tokens,
                max_retries=max_retries,
                timeout=timeout,
            )
            for experience, response in zip(experience_batch, responses):
                try:
                    experience.biohack_subtype = response.biohack_subtype
                except Exception as e:
                    print(e)
                    print(response)
                    experience.biohack_subtype = None
                if size != None:
                    print(experience.action)
                    print(experience.biohack_subtype)
                    print("-" * 50)
            self.save()

    async def action_score_experiences(
        self,
        *,
        size: int,
        batch_size: int,
        llm_name: str,
        max_tokens: int,
        max_retries: int,
        timeout: int,
        start: int = 0,
    ) -> None:
        # save the experiences after every 500 batch
        save_batch_size = 500
        experiences = self.experiences[start:size]
        experience_batches = list(itertools.batched(experiences, save_batch_size))
        number_of_batches = len(experience_batches)
        for idx, experience_batch in enumerate(experience_batches):
            print(f"Batch: {idx}/{number_of_batches} saving every {save_batch_size}")
            responses = await ActionScoreChain.batch_predict(
                size=batch_size,
                llm_name=llm_name,
                input_objects=experience_batch,
                max_tokens=max_tokens,
                max_retries=max_retries,
                timeout=timeout,
            )
            for experience, response in zip(experience_batch, responses):
                try:
                    experience.action_score = response.score
                except Exception as e:
                    print(response)
                    experience.action_score = 0

            self.save()

    async def outcomes_score_experiences(
        self,
        *,
        size: int,
        batch_size: int,
        llm_name: str,
        max_tokens: int,
        max_retries: int,
        timeout: int,
        start: int = 0,
    ) -> None:
        # save the experiences after every 500 batch
        def missing_outcomes_score():
            missing = sum([1 for e in self.experiences if e.outcomes_score is None])
            print(f"Missing outcomes: {missing}")

        missing_outcomes_score()
        save_batch_size = 500
        experiences = self.experiences[start:size]
        indices = [
            idx
            for idx, experience in enumerate(experiences)
            if experience.outcomes_score is None
        ]
        outcomes_scores = [experience.outcomes_score for experience in experiences]
        indices = indices[start:size]
        indices_batches = list(itertools.batched(indices, save_batch_size))
        for idx, index_batch in enumerate(indices_batches):
            print(f"Batch: {idx}/{len(indices_batches)}")
            experience_batch = [experiences[idx] for idx in index_batch]
            responses = await OutcomesScoreChain.batch_predict(
                size=batch_size,
                llm_name=llm_name,
                input_objects=experience_batch,
                max_tokens=max_tokens,
                max_retries=max_retries,
                timeout=timeout,
            )
            for index, response in zip(index_batch, responses):
                try:
                    self.experiences[index].outcomes_score = response.score
                except Exception as e:
                    print(response)
                    self.experiences[index].outcomes_score = 0
            missing_outcomes_score()
            self.save()

    @classmethod
    def from_all(
        cls,
        *,
        topic: str,
        subreddit_names: list[str],
    ) -> None:
        data = {}
        data["title"] = topic
        experiences = []
        print(topic)
        print(subreddit_names)

        s = StudyExperiences.load(name=topic)
        experiences.extend(s.experiences)
        metadatum = []
        for subreddit_name in subreddit_names:
            subreddit = subreddit_name.split("r/")[-1]
            c = CommentExperiences.load(name=subreddit)
            experiences.extend(c.experiences)
            s = SubmissionExperiences.load(name=subreddit)
            experiences.extend(s.experiences)
            metadata = cls.subreddit_metadata(subreddit)
            print(metadata)
            metadatum.append(metadata)
        data["subreddit"] = metadatum
        filtered_experiences = [
            experience for experience in experiences if experience.valid_biohack is True
        ]
        data["experiences"] = filtered_experiences
        instance = cls(**data)
        instance.save()
        print(f"Filtered experiences: {len(filtered_experiences)}")
        print(f"Total experiences: {len(experiences)}")


class Biohack(BaseModel):
    # endpoint /biohacks/{topic}/{slug}
    # one day score dynamically from user config

    slug: str  # unique:  topic + action
    topic: str
    experiences: list[Experience]
    headline: Optional[str] = None
    summary: Optional[str] = None
    action_label: str
    health_disorder_labels: list[str]
    outcome_labels: list[str]
    mechanism_labels: Optional[list[str]] = None
    personal_context_labels: Optional[list[str]] = None
    study_count: int
    reddit_count: int
    ai_score: Optional[int] = None  # dynamic
    bm25_score: Optional[float] = None  # dynamic
    similarity_score: Optional[float] = None  # dynamic
    action_score: int
    outcomes_score: int
    unexpected_score: Optional[int] = None  # TODO
    search_type: Optional[str] = None  # dynamic for evaluation ONLY

    # bad_side_effects: Optional[str] = None  # dynamically generated per query

    @property
    def tags(self) -> str:
        tags = self.outcome_labels + self.health_disorder_labels
        return " & ".join(tags)

    @property
    def outcome_tags(self) -> str:
        tags = self.outcome_labels
        return " & ".join(tags)

    @property
    def title(self) -> str:
        return self.topic

    @property
    def etl_score(self) -> int:
        return self.action_score + self.outcomes_score


class TakeawaySummaryResponseSchema(BaseModel):
    headline: str = Field(
        title="Headline",
        description="""
            In ten words or less write a headline that captures the most important point for a biohacker
            to understand the content in this text.

            Guidelines:
            -----------

            - You must spell out acronyms in parentheses.
            - You must drop all words that are not critical to the biohacking topic.
            - Be succinct as possible and avoid redundancy.
        """,
    )
    summary: str = Field(
        title="Takeaway Summary",
        description="""
            In four sentences or less, what is the most important thing a health
            biohacker needs to know from this text to improve their health or
            performance?
            Get right to the point.
            Be as minimalistic as possible.
            Do not include any fluff.
            Do not include anything not in the text.
            Do not include a summary of what you already wrote - ie., nothing redundant.
        """,
    )


class TakeawaySummaryChain(Chain):
    # JUST OUTCOMES ????

    input_schema = Biohack
    output_schema = TakeawaySummaryResponseSchema

    @classmethod
    def make_input_text(cls, *, input: Biohack) -> str:
        biohack = input
        experiences = biohack.experiences
        takeaways = "\n".join(
            [
                experience.model_dump_json(
                    include={"action", "takeaway", "outcomes"}, indent=2
                )
                for experience in experiences
            ]
        )
        input_text = f"""
        Biohack name: {biohack.action_label}
        ----------------

        Experiences
        ------------

            {takeaways}
        """
        return input_text


class Candidate(BaseModel):
    label: str
    correlation: float


class MechanismResponse(BaseModel):
    mechanism: Optional[str] = Field(
        default=None,
        title="Scientific Mechanism",
        description="""
            In five words or less, what is the target physiological or psychological mechanism by
            which the antecedent action causes the consequent outcomes?

            Guidelines:
            -----------

            - Be minimalistic. Use as few words as possible.
            - Be as specific as possible.
            - You must provide a scientific mechanism.
            - Spell out acronyms in parentheses.
            - You must provide a mechanism that a doctor or scientist would think is plausible.
            - Leverage your rigorous medical knowledge, not your imagination or the common sense of a layperson.
            - Leave it blank if you are not certain.
            """,
    )


class MechanismInput(BaseModel):
    action: str
    outcomes: str


class MechanismChain(Chain):

    input_schema = MechanismInput
    output_schema = MechanismResponse

    @classmethod
    def make_input_text(cls, *, input: MechanismInput) -> str:
        input_text = f"""

            Antecedent Action: {input.action}

            Consequent Outcomes: {input.outcomes}

        """
        return input_text


def main():
    for topic in ["Biohacking", "Pregnancy", "Sleep"]:
        print(topic)
        if topic == "Biohacking":
            subreddits = biohacker_subreddits + new_biohacker_subreddits
        elif topic == "Pregnancy":
            subreddits = pregnancy_subreddits
        elif topic == "Sleep":
            subreddits = sleep_subreddits
        else:
            raise ValueError("Invalid topic")
        # TopicExperiences.from_all(
        #     topic=topic,
        #     subreddit_names=subreddits[:None],
        # )

        # o = TopicExperiences.load(name=topic)
        o = TopicExperiences.load(name=topic)
        # o.deduplicate_experiences()

        # START = 0
        # # Biohacking ...I think is done
        # # ACTION SCORING DONE FOR PREGNANCY
        # # SLEEP DONE
        # asyncio.run(
        #     o.action_score_experiences(
        #         size=None,
        #         batch_size=50,
        #         llm_name="gpt-4o-mini",
        #         max_tokens=50,
        #         max_retries=0,
        #         timeout=5,
        #         start=START,
        #     )
        # )
        # START = 0
        # SIZE = None
        # asyncio.run(
        #     o.extract_biohack_subtype(
        #         start=START,
        #         size=SIZE,
        #         batch_size=50,
        #         llm_name="gpt-4o-mini",
        #         max_tokens=100,
        #         max_retries=0,
        #         timeout=5,
        #     )
        # )
        # o.save()
        # # Biohacking ...I think is done
        # # Outcomes scoring done for pregnancy
        # # SLEEP DONE
        # START = 0
        # asyncio.run(
        #     o.outcomes_score_experiences(
        #         max_tokens=50,
        #         size=None,
        #         timeout=5,
        #         max_retries=0,
        #         batch_size=50,
        #         llm_name="gpt-4o-mini",
        #         # llm_name="gpt-4o",
        #         start=START,
        #     )
        # )
        # o.save()
        # START CLUSTERING
        # USE DBSCAN??
        # https://scikit-learn.org/1.5/modules/generated/sklearn.cluster.DBSCAN.html
        ## I DON'T THINK THIS IS NEEDED SINCE WE CANT CLUSTER 100,000 EXPERIENCES ??
        ## https://stackoverflow.com/questions/9156961/hierarchical-clustering-of-1-million-objects
        # ### RAISE CLUSTERING THRESHOLDS
        # o = TopicExperiences.load(name=topic)
        # action_labels = [e.action_label for e in o.experiences]
        # print(f"Unique actions: {len(set(action_labels))}")
        # # 732
        # attributes = ["health_disorder", "outcomes"]
        # attributes = ["action"]
        # attributes = ["mechanism", "action"]
        # attributes = ["action", "health_disorder", "outcomes", "mechanism", "personal_context"]
        # for attribute in attributes:
        #     logger.info(f"Clustering {attribute}")
        #     o.cluster_biohacks(
        #         thresholds={
        #             "action": 2.5,
        #             "health_disorder": 2.5,
        #             "outcomes": 2.5,
        #             "mechanism": 2.5,
        #             "personal_context": 2.5,
        #         },
        #         biohack_attribute=attribute,
        #     )
        # o.save()
        # NAME CLUSTERS
        # attributes = ["action", "health_disorder", "outcomes"]
        # attributes = ["action"]
        # for attribute in attributes:
        #     asyncio.run(
        #         o.name_clusters(
        #             max_tokens=200,
        #             max_retries=0,
        #             timeout=60,
        #             size=None,
        #             batch_size=50,
        #             llm_name="gpt-4o",
        #             biohack_attribute=attribute,
        #         )
        #     )
        # o.label_experiences()
        # action_labels = [e.action_label for e in o.experiences]
        # unique_actions = set(action_labels)
        # print(unique_actions)
        # print(f"Unique actions: {len(unique_actions)}")
        # # 732
        # # 308
        ### END CLUSTERING
        ### START ADD MECHANISMS TO EXPERIENCES
        # o = TopicExperiences.load(name=topic)
        # experiences = o.experiences
        # e_inputs = []
        # for experience in experiences:
        #     e_inputs.append(
        #         MechanismInput(action=experience.action, outcomes=experience.outcomes)
        #     )
        # batch_size = 300
        # responses = asyncio.run(
        #     MechanismChain.batch_predict(
        #         size=batch_size,
        #         llm_name="gpt-4o-mini",
        #         input_objects=e_inputs,
        #         max_tokens=250,
        #         max_retries=0,
        #         timeout=5,
        #     )
        # )
        # for experience, response in zip(experiences, responses):
        #     try:
        #         experience.mechanism = response.mechanism
        #     except Exception as e:
        #         experience.mechanism = None
        #         logger.error(e)
        # o.save()
        ### END ADD MECHANISMS TO EXPERIENCES

        # Biohacks.from_topic_experiences(topic=topic)
        # biohacks = Biohacks.load(name=topic)
        # experiences_x = []
        # e_inputs = []
        # for biohack in tqdm(biohacks.biohacks):
        #     for e in biohack.experiences:
        #         print(e.action, e.outcomes)
        #         experiences_x.append(e)
        #         e_inputs.append(MechanismInput(action=e.action, outcomes=e.outcomes))
        # responses = asyncio.run(
        #     MechanismChain.batch_predict(
        #         size=150,
        #         llm_name="gpt-4o-mini",
        #         input_objects=e_inputs,
        #         max_tokens=250,
        #         max_retries=0,
        #         timeout=5,
        #     )
        # )
        # for experience, response in zip(experiences_x, responses):
        #     try:
        #         experience.mechanism = response.mechanism
        #     except ValidationError as e:
        #         experience.mechanism = None
        #         logger.error(e)
        # biohacks.save()

        #
        # responses = asyncio.run(
        #     TakeawaySummaryChain.batch_predict(
        #         size=150,
        #         llm_name="gpt-4o",
        #         input_objects=b.biohacks,
        #         max_tokens=250,
        #         max_retries=1,
        #         timeout=10,
        #     )
        # )
        # for biohack, response in zip(b.biohacks, responses):
        #     try:
        #         biohack.headline = response.headline
        #         biohack.summary = response.summary
        #     except ValidationError as e:
        #         biohack.headline = "Error:  " + str(e)
        #         biohack.summary = "Error:  " + str(e)
        #         logger.error(e)
        #
        # b.save()
        # b.set_biohack_headline_of_experiences()
        # remember to add MECHANISMS for more indirect, backdoor, root cause biohacks
        # b.create_embeddings()
        # print(b.embeddings)
        ## set experience.biohack_slug -- so we can get to the biohack from the experience
        # for biohack in b.biohacks:
        #     for experience in biohack.experiences:
        #         experience.biohack_slug = biohack.slug
        #         console.print(experience.biohack_slug, style="info")
        # b.save()


if __name__ == "__main__":
    # source ls ../../../data/etl_store/study_deep_experiences/2020
    import json
    from pathlib import Path

    import nest_asyncio

    nest_asyncio.apply()

    source_dir = Path(
        "/Users/borisdev/workspace/nobsmed/data/etl_store/study_deep_experiences/"
    )
    sink_dir = Path(
        "/Users/borisdev/workspace/nobsmed/data/etl_store/study_deep_experiences_enriched/"
    )
    batch_size = 250
    # 10.1101_2020.12.25.20248860.json
    # get all the json files in the source directory
    files = [file for file in source_dir.rglob("*.json")]
    print(f"Files: {len(files)}")
    dicts = [json.loads(file.read_text()) for file in files]
    experiences = [Experience(**d) for d in dicts]
    experience_batches = list(itertools.batched(experiences, batch_size))
    for idx, experience_batch in enumerate(experience_batches):
        print(f"Batch: {idx}/{len(experience_batches)}")
        responses = asyncio.run(
            ActionScoreChain.batch_predict(
                size=batch_size,
                llm_name="gpt-4o-mini",
                input_objects=experience_batch,
                max_tokens=250,
                max_retries=0,
                timeout=5,
            )
        )
        # add the action_score to each experience in the batch
        for experience, response in zip(experience_batch, responses):
            try:
                experience.action_score = response.score
            except Exception as e:
                print(response)
                experience.action_score = 0

        responses = asyncio.run(
            OutcomesScoreChain.batch_predict(
                size=batch_size,
                llm_name="gpt-4o-mini",
                input_objects=experience_batch,
                max_tokens=250,
                max_retries=0,
                timeout=5,
            )
        )
        # add the outcomes_score to each experience in the batch
        for experience, response in zip(experience_batch, responses):
            try:
                experience.outcomes_score = response.score
            except Exception as e:
                print(response)
                experience.outcomes_score = 0

        # filter out None experiences
        valid_experiences = [
            experience
            for experience in experience_batch
            if experience.action_score is not None
            and experience.outcomes_score is not None
        ]
        if len(valid_experiences) == 0:
            continue
        inputs = [
            MechanismInput(action=e.action, outcomes=e.outcomes)
            for e in valid_experiences
        ]
        responses = asyncio.run(
            MechanismChain.batch_predict(
                size=batch_size,
                llm_name="gpt-4o-mini",
                input_objects=inputs,
                max_tokens=250,
                max_retries=0,
                timeout=5,
            )
        )
        # add the mechanism to each experience in the batch
        for experience, response in zip(valid_experiences, responses):
            try:
                experience.mechanism = response.mechanism
            except Exception as e:
                print(response)
                experience.mechanism = None
        for experience in valid_experiences:
            name = experience.permalink.replace("/", "_")
            sink_file = sink_dir / f"{name}.json"
            sink_file.parent.mkdir(parents=True, exist_ok=True)
            sink_file.write_text(experience.model_dump_json(indent=2))
            logger.info(f"Saved {sink_file}")
