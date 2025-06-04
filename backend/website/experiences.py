"""
shared --> surface --> cluster --> deep (hack) --> opensearch index
"""

from __future__ import annotations

import asyncio
import enum
import itertools
import json
import re
import time
from abc import ABCMeta, abstractmethod
from typing import (Annotated, Any, Iterable, Literal, Optional, Type, TypeVar,
                    Union)

from loguru import logger
from opensearchpy import Search
from pydantic import BaseModel, Field, PlainSerializer, field_validator
from rich import print
from tqdm import tqdm
from website.base import Base, SubredditAttributes
from website.chain import Chain
from website.models import BiohackTypeLiteral, Experience
from website.settings import opensearch_client
from website.subreddit import Comment, Submission


def ser_type(value: type[Any]) -> str:
    return value.__name__


T = TypeVar("T")

JSONSerializableType = Annotated[
    type[T], PlainSerializer(ser_type, when_used="json-unless-none")
]


class MyType:
    pass


class Test(BaseModel):
    a: JSONSerializableType[MyType]


print(Test(a=MyType).model_dump(mode="json"))


class StudyField(enum.Enum):
    title = "title"
    content = "content"
    keywords = "keywords"
    subjects = "subjects"


class Study(BaseModel):
    doi: str
    title: str
    keywords: str
    subjects: str
    content: str
    abstract: dict
    published: str

    @field_validator("doi")
    def validate_doi(cls, v):
        # A simple regex for DOI validation
        if not re.match(r"^10.\d{4,9}/[-._;()/:A-Z0-9]+$", v, re.IGNORECASE):
            raise ValueError("Invalid DOI format")
        return v

    @classmethod
    def from_hit(cls, hit: dict) -> Study:
        keywords = hit["keywords"]
        if keywords is not None:
            keywords = " & ".join(keywords)
        else:
            keywords = ""
        subjects = hit["subjects"]
        if subjects is not None:
            subjects = " & ".join(subjects)
        else:
            subjects = ""
        content = hit["content"]
        try:
            abstract = json.loads(content.split("\n\n")[0])
        except Exception as e:
            logger.warning(f"{e}")
            logger.warning(f"Failed to parse abstract for study: {hit['title']}")
            abstract = {}
        study = Study(
            title=hit["title"],
            keywords=keywords,
            subjects=subjects,
            published=hit["published"],
            content=hit["content"],
            doi=hit["doi"],
            abstract=abstract,
        )
        return study


class Biohack(BaseModel):
    action: str = Field(
        title="Antecedent Action (Biohack, Treatment, or Intervention)",
        description="""
            Use one simple sentence to describe the biohack, treatment, or intervention.

            This must be an antecedent action that is physically or mentally
            undertaken by the writer or study participants which resulted in a
            consequent outcome that you will describe below.

            Leave it blank if you see no very clear action that is a biohack, treatment, or intervention
            that resulted in a change in health or performance of the author or study participants.

            Valid actions include:
            ------------------------------------------

                - new diet
                - new device usage
                - new exercise
                - new sleep habit
                - new nootropic
                - new pharmaceutical medication
                - new dosage
                - new supplement usage
                - new therapy
                - new habit
                - new environmental exposure
                - new social context
                - new physical training or therapy
                - new mental training or therapy
                - new diagnostic method
                - new surgical intervention
                - new light exposure
                - new vaccine
                - other


            Style Guide:
            =============

            - Include all proper names of devices, products, drugs, brands, therapies, books, etc.
            - You must include all products you see that can easily be purchased via Amazon.com
            - Spell out abbreviations in parentheses
        """,
    )
    health_disorder: str = Field(
        title="Health Disorder",
        description="""
            Use three words of less to classify the health disorder that the author or study participants are trying to improve.

            Style Guide:
            =============

            - spell out abbreviations in parentheses.
            """,
    )


class SurfaceExperienceResponseSchema(BaseModel):

    takeaway: Optional[str] = Field(
        default=None,
        title="Takeaway",
        description="""
            In one sentence, what is the most important thing a health
            biohacker needs to know from this text to improve their health or
            performance? If you see nothing important, leave it blank.
        """,
    )
    biohack: Optional[Biohack] = Field(
        default=None,
        title="Biohack",
        description="""
            Make a biohack object. If its not clear what the biohack is, leave it blank.
        """,
    )
    clinical_trial_study: Optional[bool] = Field(
        default=None,
        title="Clinical Trial Study",
        description="""
            Is this a clinical trial study? If its not clear, leave it blank.

            A clinical trial study is a research study that tests how well new
            medical approaches work in study partipants and reports their
            outcomes in an emperical way.
            It is not a review, opinion, meta-analysis or epidemiological study.
            If its not clear, leave it blank.
        """,
    )

    biohack_type: Optional[BiohackTypeLiteral] = Field(
        default=None,
        title="Biohack Type",
        description="""
            Classifiy the biohack action into one of the given biohack types.

            Guidelines
            ==========

            - never use `treatment`, instead use `other` or a more specific biohack type
            - never use `vaccination`, instead use `vaccine`
            - if its not clear, leave it blank
            - user `other` only if the biohack type is not listed in the given possible values
        """,
    )
    outcomes: Optional[str] = Field(
        default=None,
        title="Consequent Outcomes",
        description="""
            What outcomes were caused by the biohack action?

            Style Guide:
            ------------

            - Don't guess. Leave it blank if you are not certain that you see
            any clear health or performance outcomes.
            - Include all specific health and performance details on each study participant or for the author.
            - Never make anything up. Only include what is clearly stated in the text.
            - Be succinct. Use the least words possible.
        """,
    )
    personal_context: Optional[str] = Field(
        default=None,
        title="Personal Context",
        description="""
            In one concise sentence, what personal context did the author or
            study participants have that may have influenced the outcomes?

            Style Guide:
            ------------
            - Include all personal details that may have influenced the outcomes.
            - Never make anything up. Only include what is clearly stated in the text.
            - Be succinct. Use the least words possible.
            - If its not clear, leave it blank.
        """,
    )
    health_disorder: Optional[str] = Field(
        default=None,
        title="Health Disorder",
        description="""
            Use three words of less to classify the health disorder that the author or study participants are trying to improve.

            Style Guide:
            =============

            - spell out abbreviations in parentheses.
            """,
    )


class SurfaceStudyExperienceResponseSchema(SurfaceExperienceResponseSchema):

    clinical_trial_study: Optional[bool] = Field(
        default=None,
        title="Clinical Trial Study",
        description="""
            Is this a clinical trial study? If its not clear, leave it blank.

            A clinical trial study is a research study that tests how well new
            medical approaches work in study partipants and reports their
            outcomes in an emperical wayi.
            It is not a review, opinion, meta-analysis or epidemiological study.
            If its not clear, leave it blank.
        """,
    )


class SubmissionChain(Chain):

    input_schema = Submission
    output_schema = SurfaceExperienceResponseSchema

    @classmethod
    def make_input_text(cls, *, input: Submission) -> str:
        submission_body = input.selftext
        if submission_body is None:
            submission_body = ""
        submission_title = input.title
        input_text = f"""
            Title: {submission_title}
            =================

            {submission_body}
        """
        return input_text


class CommentInputSchema(BaseModel):
    permalink: str
    comment: Comment
    submission: Submission


class CommentChain(Chain):

    input_schema = CommentInputSchema
    output_schema = SurfaceExperienceResponseSchema

    @classmethod
    def make_input_text(cls, *, input: CommentInputSchema) -> str:
        input_text = f"""

            Author's Comment
            ----------------

            {input.comment.body}


            Context
            ----------------

            The author of this comment is responding to the following thread:

            Thread Title: {input.submission.title}
        """
        return input_text


class StudyChain(Chain):
    input_schema = Study
    output_schema = SurfaceStudyExperienceResponseSchema

    @classmethod
    def make_input_text(cls, *, input: Study) -> str:
        input_text = f"""
            Title: {input.title}
            =================

            {input.content}
        """
        return input_text


class Experiences(Base, metaclass=ABCMeta):
    # subreddit: str
    experiences: Optional[list[Experience]] = None

    @abstractmethod
    def get_relevant_input_objects(self, *, size: int) -> Iterable[Any]:
        pass

    async def set_experiences(
        self,
        *,
        size: Union[int, None],
        subreddit: Optional[FetchedSubreddit] = None,
        chain: Type[Chain],
        batch_size: int,
        llm_name: str,
        max_retries: int,
        max_tokens: int,
        timeout: int,
    ) -> None:
        if subreddit is not None:
            print(f"Topic: {self.title} , Subreddit: {self.subreddit.display_name}")
        else:
            print(f"Topic: {self.title}")
        input_objects = self.get_relevant_input_objects(size=size)
        responses = await chain.batch_predict(
            size=batch_size,
            input_objects=input_objects,
            llm_name=llm_name,
            max_retries=max_retries,
            max_tokens=max_tokens,
            timeout=timeout,
        )
        experiences = []
        for inp, response in zip(input_objects, responses):
            if isinstance(response, Exception):
                continue
            elif response.biohack is None:
                continue
            elif response.outcomes is None:
                continue
            elif response.biohack.action is None:
                continue
            elif response.biohack.health_disorder is None:
                continue
            elif response.takeaway is None:
                continue
            else:
                if hasattr(inp, "doi"):
                    ID = inp.doi
                elif hasattr(inp, "permalink"):
                    ID = inp.permalink
                else:
                    raise ValueError(
                        "Input object must have a permalink or doi attribute"
                    )

                experience = Experience(
                    permalink=ID,
                    action=response.biohack.action,
                    health_disorder=response.biohack.health_disorder,
                    takeaway=response.takeaway,
                    biohack_type=response.biohack_type,
                    clinical_trial_study=response.clinical_trial_study,
                    outcomes=response.outcomes,
                )
                # mechanism=response.mechanism,
                # personal_context=response.personal_context,
                experiences.append(experience)
        self.experiences = experiences
        self.save()


class StudyExperiences(Experiences):
    query: Optional[str] = None

    @classmethod
    def subreddit_metadata(cls, subreddit_name: str) -> SubredditAttributes:
        print(f"Subreddit name: {subreddit_name} -- should be None")
        s = SubredditAttributes(
            display_name="__STUDIES__",
            title="__STUDIES__",
            public_description="__STUDIES__",
            subscribers=None,
        )
        return s

    def get_relevant_input_objects(self, *, size: int) -> list[Submission]:
        topic = self.title
        covid = "COVID-19"
        must_not = [
            {"match": {StudyField.title.value: {"query": covid}}},
            {"match": {StudyField.subjects.value: {"query": covid}}},
            {"match": {StudyField.keywords.value: {"query": covid}}},
            {"match": {StudyField.content.value: {"query": covid}}},
        ]
        should = [
            {"match": {StudyField.title.value: {"query": self.query, "boost": 3.0}}},
            {"match": {StudyField.subjects.value: {"query": self.query, "boost": 3.0}}},
            {"match": {StudyField.keywords.value: {"query": self.query, "boost": 2.0}}},
            {"match": {StudyField.content.value: {"query": self.query, "boost": 1.0}}},
        ]
        index_name = "submissions_2"
        s = (
            Search(using=opensearch_client, index=index_name)
            .query(
                "bool",
                should=should,
                must_not=must_not,
            )
            .extra(size=size)
        )

        # Execute with retries for timeout issues
        max_retries = 3
        retry_count = 0
        input_objects = []

        while retry_count < max_retries:
            try:
                results = s.execute()
                for hit in results:
                    input_objects.append(Study.from_hit(hit.to_dict()))
                break  # Success, exit the retry loop
            except Exception as e:
                retry_count += 1
                logger.warning(f"OpenSearch query attempt {retry_count} failed: {e}")
                if retry_count >= max_retries:
                    logger.error(f"All {max_retries} OpenSearch query attempts failed")
                    raise  # Re-raise the last exception if all retries failed
                # Wait before retrying (exponential backoff)
                import time

                time.sleep(2**retry_count)

        for input_object in input_objects:
            print(input_object.title)
        print(f"Count studies from opensearch: {len(input_objects)}")
        return input_objects


class SubmissionExperiences(Experiences, Base):

    @classmethod
    async def from_subreddit(
        cls,
        *,
        size: Union[int, None],
        subreddit_name: str,
        llm_name: str,
        batch_size: int,
        max_retries: int,
        max_tokens: int,
        timeout: int,
    ) -> None:
        subreddit_name = subreddit_name.split("/")[-1]
        instance = cls(
            subreddit=cls.subreddit_metadata(subreddit_name),
        )
        await instance.set_experiences(
            chain=SubmissionChain,
            size=size,
            llm_name=llm_name,
            batch_size=batch_size,
            max_retries=max_retries,
            max_tokens=max_tokens,
            timeout=timeout,
        )
        instance.save()

    def get_relevant_input_objects(  # type: ignore
        self, *, size: Union[int, None]
    ) -> list[Submission]:
        subreddit = FetchedSubreddit.load_from_subreddit_name(
            self.subreddit.display_name
        )
        submissions = subreddit.submissions[:size]
        return submissions


class CommentExperiences(Experiences, Base):

    @classmethod
    async def from_subreddit(
        cls,
        subreddit_name: str,
        llm_name: str,
        batch_size: int,
        size: Union[int, None],
        max_retries: int,
        max_tokens: int,
        timeout: int,
    ) -> None:
        subreddit_name = subreddit_name.split("/")[-1]
        subreddit = FetchedSubreddit.load_from_subreddit_name(subreddit_name)
        instance = cls(
            subreddit=cls.subreddit_metadata(subreddit_name),
        )
        await instance.set_experiences(
            size=size,
            subreddit=subreddit,
            chain=CommentChain,
            batch_size=batch_size,
            llm_name=llm_name,
            max_retries=max_retries,
            max_tokens=max_tokens,
            timeout=timeout,
        )
        instance.save()

    def get_relevant_input_objects(self, *, size: int) -> list[Comment]:  # type: ignore
        subreddit = FetchedSubreddit.load_from_subreddit_name(
            self.subreddit.display_name
        )
        submissions = subreddit.submissions[:size]
        input_objects = []
        for submission in submissions:
            if submission.comments is not None:
                for comment in submission.comments:
                    comment_input = CommentInputSchema(
                        permalink=comment.permalink,  # type: ignore
                        comment=comment,
                        submission=submission,
                    )
                    input_objects.append(comment_input)
        input_objects = input_objects[:size]
        return input_objects


def main():
    import nest_asyncio

    nest_asyncio.apply()
    from website.subreddit import (biohacker_subreddits,
                                   new_biohacker_subreddits,
                                   pregnancy_subreddits, sleep_subreddits)

    ## BEGIN ETL CONFIG ##
    for topic in ["Biohacking", "Pregnancy", "Sleep"]:
        print(topic)
        ### CHANGE THIS ###
        # sleep_subreddits = sleep_subreddits[4:]
        # pregnancy_subreddits = pregnancy_subreddits[18:]
        SKIP_STUDIES = False
        ################

        SUBREDDIT_TEST_SIZE = None  # 1  # 1  # or None
        STUDY_RESULTS_SIZE = 1000  # 10  # or 1000
        POSTS_TEST_SIZE = None  # None  # 10  # or None
        BATCH_SIZE = 250
        llm_name = "gpt-4o-mini"
        max_retries = 0
        max_tokens = 400
        timeout = 5
        ## END ETL CONFIG ##
        if topic == "Biohacking":
            subreddits = biohacker_subreddits + new_biohacker_subreddits
            studies_query = "biohacking, smart drugs, nootropics, or psychedelics"
        elif topic == "Pregnancy":
            subreddits = pregnancy_subreddits
            studies_query = "pre-natal care, pregnancy, or childbirth"
        elif topic == "Sleep":
            subreddits = sleep_subreddits
            studies_query = "sleep, insomnia, or sleep disorders, sleep apnea"
        else:
            raise ValueError("Invalid topic")
        subreddits = subreddits[:SUBREDDIT_TEST_SIZE]
        print(subreddits)

        if not SKIP_STUDIES:
            study_surface_experiences = StudyExperiences(
                title=topic,
                subreddit=None,
                query=studies_query,
            )
            asyncio.run(
                study_surface_experiences.set_experiences(
                    size=STUDY_RESULTS_SIZE,
                    chain=StudyChain,
                    batch_size=BATCH_SIZE,
                    llm_name=llm_name,
                    max_retries=max_retries,
                    max_tokens=max_tokens,
                    timeout=timeout,
                )
            )
        # def main_comments(*, size: Union[int, None], batch_size: int, llm_name: str) -> None:
        # for subreddit in tqdm(subreddits[:1]):
        for subreddit in tqdm(subreddits):
            print(subreddit)
            subreddit = subreddit.split("r/")[-1]
            asyncio.run(
                CommentExperiences.from_subreddit(
                    size=POSTS_TEST_SIZE,
                    max_retries=max_retries,
                    max_tokens=max_tokens,
                    subreddit_name=subreddit,
                    batch_size=BATCH_SIZE,
                    llm_name=llm_name,
                    timeout=timeout,
                )
            )
            asyncio.run(
                SubmissionExperiences.from_subreddit(
                    size=POSTS_TEST_SIZE,
                    subreddit_name=subreddit,
                    batch_size=BATCH_SIZE,
                    llm_name=llm_name,
                    max_retries=max_retries,
                    max_tokens=max_tokens,
                    timeout=timeout,
                )
            )


if __name__ == "__main__":
    import nest_asyncio

    nest_asyncio.apply()
    from pathlib import Path

    from opensearchpy import OpenSearch
    from settings import ETL_STORE_DIR

    sink_path = Path(ETL_STORE_DIR) / "study_deep_experiences"

    index_name = "submissions_2"
    client = OpenSearch(
        hosts=[{"host": "nlp.nobsmed-api.com", "port": 9200}],
        http_auth=("admin", "Boris@nobsmed.com-123"),
        use_ssl=True,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
    )
    count = client.count(index=index_name)["count"]

    with open("study_opensearch_ids_for_submissions_2.json", "r") as f:
        ids_to_search = json.load(f)

    id_batches = list(itertools.batched(ids_to_search, 100))
    # get last permalink
    with open("last_permalink.txt", "r") as f:
        last_permalink = f.read().strip()
    # last_saved = "10.1101/2022.04.25.22274279"
    last_saved = last_permalink
    reached_last_saved = False
    new_batches = []
    for batch in tqdm(id_batches):
        if last_saved in batch:
            reached_last_saved = True

        if not reached_last_saved:
            continue
        new_batches.append(batch)

    id_batches = new_batches
    total_batches = len(id_batches)
    batches_to_process = total_batches
    average_time_per_batch = None
    for batch in tqdm(id_batches):

        start_time = time.time()
        studies = []
        s = (
            Search(using=client, index=index_name)
            .query("ids", values=batch)
            .extra(size=200)
        )
        response = s.execute()

        for hit in response:
            study = Study.from_hit(hit.to_dict())
            studies.append(study)

        responses = asyncio.run(
            StudyChain.batch_predict(
                size=200,
                input_objects=studies,
                llm_name="gpt-4o-mini",
                max_retries=1,
                max_tokens=1000,
                timeout=4,
            )
        )

        experiences = []
        for inp, response in zip(studies, responses):
            if isinstance(response, Exception):
                continue
            elif response.biohack is None:
                continue
            elif response.outcomes is None:
                continue
            elif response.biohack.action is None:
                continue
            elif response.biohack.health_disorder is None:
                continue
            elif response.takeaway is None:
                continue
            else:
                if hasattr(inp, "doi"):
                    ID = inp.doi
                elif hasattr(inp, "permalink"):
                    ID = inp.permalink
                else:
                    raise ValueError(
                        "Input object must have a permalink or doi attribute"
                    )

                experience = Experience(
                    permalink=ID,
                    action=response.biohack.action,
                    health_disorder=response.biohack.health_disorder,
                    takeaway=response.takeaway,
                    biohack_type=response.biohack_type,
                    clinical_trial_study=response.clinical_trial_study,
                    outcomes=response.outcomes,
                    personal_context=response.personal_context,
                )
                year = inp.published.split("-")[0]
                sink_dir = sink_path / year
                sink_dir.mkdir(parents=True, exist_ok=True)
                new_id = experience.permalink.replace("/", "_")
                sink_file = sink_dir / f"{new_id}.json"
                with open(sink_file, "w") as f:
                    f.write(experience.model_dump_json(indent=4))
                # logger.info(f"Saved experience to {sink_file}")
        elapsed_time = time.time() - start_time
        logger.info(f"Elapsed time: {elapsed_time:.2f} seconds")
        batches_to_process -= 1
        if average_time_per_batch is None:
            average_time_per_batch = elapsed_time
        else:
            average_time_per_batch = (average_time_per_batch + elapsed_time) / 2
        last_permalink = batch[-1]
        logger.info(f"Last permalink: {last_permalink}")
        # log last permalink
        with open("last_permalink.txt", "w") as f:
            f.write(last_permalink)
        logger.info(f"Batches left: {batches_to_process}")
        logger.info(f"Average time per batch: {average_time_per_batch:.2f} seconds")
        # estimate time left
        time_left = average_time_per_batch * batches_to_process
        logger.info(f"Estimated time left: {time_left/60.0:.2f} minutes")

        # Experience(
        #     id=None,
        #     biohack_slug=None,
        #     permalink='10.1101/2022.09.07.22278977',
        #     takeaway='Watching stressful football matches can significantly increase mortality risk for susceptible individuals.',
        #     clinical_trial_study=None,
        #     biohack_topic=None,
        #     biohack_type='lifestyle or habit',
        #     biohack_subtype=None,
        #     action='Increase awareness of emotional stress during football matches',
        #     action_tag=None,
        #     action_embedding=None,
        #     health_disorder='circulatory diseases',
        #     outcomes='Mortality doubled for men two days after watching a stressful football match.',
        #     personal_context=None,
        #     mechanism=None,
        #     action_score=None,
        #     outcomes_score=None
        # ),
