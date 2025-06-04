from __future__ import annotations

import itertools
import json
import time
from pathlib import Path
from typing import Any, Iterable, Optional

from loguru import logger
from opensearchpy import Document, Integer, Keyword, Text, exceptions, helpers
from opensearchpy.helpers import field
from rich import print
from rich.traceback import install
from tqdm import tqdm

from website.biohacks import TopicExperiences
from website.experiences import Experience
from website.settings import console, opensearch_client

# install(show_locals=True)
install(show_locals=True)


class UserLogRecord(BaseModel):
    user_id: str
    timestamp: datetime


class UserLogRecordDoc(Document):
    user_id = Keyword()
    timestamp = Date()

    def to_pydantic(self) -> UserLogRecord:
        return UserLogRecord(**self.to_dict())

    @classmethod
    def from_pydantic(cls, user_log: UserLogRecord) -> UserLogRecordDoc:
        return cls(
            **user_log.model_dump(),
        )


class QuestionAnswer(BaseModel):
    question: str
    answer: str
    llm_chain: str
    user_logs: list[UserLogRecord] = []


class QuestionAnswerDoc(Document):

    question = Text(
        fields={
            "raw": Keyword(),
            "english": Text(analyzer="english"),
        }
    )
    answer = Text(index=False)
    llm_chain = Keyword()
    user_log = Nested(UserLogRecordDoc)

    class Index:
        name = "question_answer"
        using = opensearch_client

    def to_pydantic(self) -> QuestionAnswer:
        return QuestionAnswer(**self.to_dict())

    @classmethod
    def from_pydantic(cls, qa: QuestionAnswer) -> QuestionAnswerDoc:
        return cls(
            **qa.model_dump(),
        )

    @classmethod
    def count(cls) -> int:
        client = cls.Index.using
        index_name = cls.Index.name
        count = client.count(index=index_name)["count"]
        logger.info(f'The index "{index_name}" contains {count} documents.')
        return count

    @classmethod
    def re_create_index(cls):
        client = cls.Index.using
        index_name = cls.Index.name
        try:
            client.indices.delete(index=index_name)
            logger.warning(f"Index `{index_name}` deleted")
        except exceptions.NotFoundError:
            pass
        index_body = {"settings": {"index": {"number_of_shards": 4}}}
        response = client.indices.create(index_name, body=index_body)
        cls.init(using=client)
        logger.info(f"Index count: {cls.count()}")
        logger.info(f"Index creation response: {response}")

    @classmethod
    def _get_using(cls: Any, using: Any = None) -> Any:
        return using or cls._index._using

    def save(self, **kwargs: Any) -> Any:  # type: ignore
        skip_empty = kwargs.pop("skip_empty", False)
        return super().save(skip_empty=skip_empty, **kwargs)

    class Index:  # type: ignore
        name = "embedding_experiences"
        # name = "sleep_experiences"
        using = opensearch_client

    def to_pydantic(self) -> Experience:
        return Experience(**self.to_dict())

    @classmethod
    def from_pydantic(cls, experience: Experience) -> EmbeddingExperienceDoc:
        return cls(
            **experience.model_dump(),
            source_type=experience.source_type,
        )

    @classmethod
    def re_create_index(cls, use_client, embedding_pipeline: str) -> None:
        if use_client is None:
            client = cls.Index.using
        else:
            client = use_client
        index_name = cls.Index.name
        logger.warning(f"Deleting index `{index_name}`")
        try:
            client.indices.delete(index=index_name)
            logger.warning(f"Index `{index_name}` deleted")
        except exceptions.NotFoundError:
            pass
        # index_body = {"settings": {"index": {"number_of_shards": 4}}}
        # step8_embedding_pipeline(model_id="UbtpR5QBBNwU8U85ihpN", name="all-MiniLM-L6-v2")
        index_body = {
            "settings": {
                "index.knn": True,
                # "default_pipeline": "all-MiniLM-L6-v2",
                "default_pipeline": embedding_pipeline,
            }
        }
        response = client.indices.create(index_name, body=index_body)
        cls.init(using=client)
        print(response)

    @classmethod
    def rehydrate_index(
        cls,
        *,
        topics: Iterable[str],
        limit: Optional[int] = None,
        use_client=None,
        embedding_pipeline: str,
    ) -> None:
        """
        Takes hour one by one

        Does batch work??
        """
        if use_client is None:
            client = cls.Index.using
        else:
            client = use_client
        try:
            before_count = cls.count(use_client=client)
            print(f"Before count: {before_count}")
        except exceptions.NotFoundError:
            before_count = 0
        cls.re_create_index(use_client=client, embedding_pipeline=embedding_pipeline)
        console.print(f"Topics: {topics}", style="info")
        start = time.time()
        success = 0
        errors = 0
        docs = []
        for topic in topics:
            print(topic)
            o = TopicExperiences.load(name=topic)
            target_experiences = [experience for experience in o.experiences]
            valid_experiences = [
                experience
                for experience in target_experiences
                if experience.valid_biohack(action_score=2, outcomes_score=2)
            ]
            for experience in tqdm(valid_experiences[:limit]):
                doc = cls.from_pydantic(experience)
                docs.append(doc)
        console.print(f"Topics: {topics}", style="info")
        console.print(f"Bulk loading experiences: {len(docs)}", style="info")
        start = time.time()
        save_batch_size = 500
        docs_batches = list(itertools.batched(docs, save_batch_size))
        number_of_batches = len(docs_batches)
        all_success = []
        all_errors = []

        for idx, docs_batch in enumerate(docs_batches):
            success, errors = helpers.bulk(
                client=client,
                actions=[doc.to_dict(include_meta=True) for doc in docs_batch],
                chunk_size=100,
            )
            console.print(
                f"Batch {idx}/{number_of_batches} Success: {success}, Errors: {errors}",
                style="info",
            )
            all_success.append(success)
            all_errors.append(errors)

        """
        22K took 1 hour one by one on local
        """
        end = time.time()

        console.print(f"Time taken: {end - start}", style="info")
        after_count = cls.count(use_client=client)
        console.print(f"Success: {success}, Errors: {errors}", style="info")
        cls.describe(test_phrases=["REM"], use_client=client)
        console.print(
            f"Before count: {before_count}, After count: {after_count}",
            style="info",
        )


def test_question_answer(*, question: str):
    question = question.strip()
    if question[-1] == "?":
        question = question[:-1]
    console.print(
        "QuestionAnswerDoc doc count", QuestionAnswerDoc.count(), style="info"
    )
    user = "anonymous"
    # question = "What are the benefits of REM sleep?"
    llm_chain = "ajay-01"
    search = (
        QuestionAnswerDoc.search()
        .filter("term", **{"question.raw": question})
        .filter("term", llm_chain=llm_chain)
    )
    response = search.execute()
    doc = response.hits[0] if len(response.hits) > 0 else None
    if doc is None:
        user_log_record = UserLogRecord(user_id=user, timestamp=datetime.now())
        user_log_record_doc = UserLogRecordDoc.from_pydantic(user_log_record)

        question_answer = QuestionAnswer(
            question=question,
            answer="NO SEARCH RESULTS",
            llm_chain=llm_chain,
            user_logs=[user_log_record],
        )
        x = QuestionAnswerDoc.from_pydantic(question_answer)
        x.save()
        console.print("Cached question and NO answer", x.to_pydantic(), style="info")
    else:
        console.print("Document already exists", doc, style="info")
        user_log_record = UserLogRecord(user_id=user, timestamp=datetime.now())
        user_log_record_doc = UserLogRecordDoc.from_pydantic(user_log_record)
        doc.user_logs.append(user_log_record.model_dump())
        doc.save()
        console.print("Updated document", doc.to_pydantic(), style="info")


def embedding_experiences_reindex(*, client, embedding_pipeline):
    # 10 minutes to reindex 22K experiences with full embeddings
    # But then lost opensearch client connection and docker container went down
    # Opensearch embedings aremt really need for KNN ANN search....so should all memory of the graph??
    if input("Are you sure you want to wipe out and re-index? (y/n)") == "y":
        EmbeddingExperienceDoc.rehydrate_index(
            topics=["Biohacking", "Pregnancy", "Sleep"],
            limit=None,
            use_client=client,
            embedding_pipeline=embedding_pipeline,
        )
    else:
        sys.exit(0)


class KNNVector(field.Float):
    name: Optional[str] = "knn_vector"

    def __init__(self, dimension: Any, **kwargs: Any) -> None:
        kwargs["multi"] = True
        super().__init__(dimension=dimension, **kwargs)


class ExperienceDoc4(Document):
    # outcomes_embedding = KNNVector(
    #     dimension=384,
    #     type="knn_vector",
    #     method={
    #         "engine": "lucene",
    #         "space_type": "l2",
    #         "name": "hnsw",
    #         "parameters": {},
    #     },
    # )
    permalink = Keyword(index=False)
    url = Keyword(index=False)
    source_type = Keyword()
    action = Text(analyzer="english")
    health_disorder = Text(analyzer="english")
    outcomes = Text(analyzer="english")
    personal_context = Text(analyzer="english")
    mechanism = Text(analyzer="english")
    biohack_type = Keyword()
    biohack_topic = Keyword()
    action_score = Integer()
    outcomes_score = Integer()

    class Index:  # type: ignore
        name = "experiences_4"
        using = opensearch_client

    @classmethod
    def count(cls, use_client=None) -> int:
        if use_client is None:
            client = cls.Index.using
        else:
            client = use_client
        index_name = cls.Index.name
        count = client.count(index=index_name)["count"]
        console.print(
            f'The index "{index_name}" contains {count} documents in {client}',
            style="info",
        )
        return count

    @classmethod
    def re_create_index(cls, use_client=None):
        if use_client is None:
            client = cls.Index.using
        else:
            client = use_client
        cls.init(using=client)
        index_name = cls.Index.name
        try:
            client.indices.delete(index=index_name)
            logger.warning(f"Index `{index_name}` deleted")
        except exceptions.NotFoundError:
            pass
        index_body = {"settings": {"index": {"number_of_shards": 1}}}
        response = client.indices.create(index_name, body=index_body)
        print(response)

    @classmethod
    def _get_using(cls: Any, using: Any = None) -> Any:
        return using or cls._index._using

    def save(self, **kwargs: Any) -> Any:  # type: ignore
        self.meta.id = self.permalink
        skip_empty = kwargs.pop("skip_empty", False)
        return super().save(skip_empty=skip_empty, **kwargs)

    def to_pydantic(self) -> Experience:
        return Experience(**self.to_dict())

    @classmethod
    def from_pydantic(cls, experience: Experience) -> ExperienceDoc4:
        return cls(
            **experience.model_dump(
                include={
                    "permalink",
                    "url",
                    "source_type",
                    "action",
                    "health_disorder",
                    "outcomes",
                    "personal_context",
                    "mechanism",
                    "biohack_type",
                    "action_score",
                    "outcomes_score",
                    "biohack_topic",
                }
            ),
            # source_type=experience.source_type,
        )

    @classmethod
    def rehydrate_index_studies(
        cls,
        *,
        action_score: int,
        outcomes_score: int,
        limit: Optional[int] = None,
        use_client=None,
    ) -> None:
        """
        Takes hour one by one

        Does batch work??
        """
        if use_client is None:
            client = cls.Index.using
        else:
            client = use_client
        try:
            before_count = cls.count(use_client=client)
            print(f"Before count: {before_count}")
        except exceptions.NotFoundError:
            before_count = 0
        # cls.re_create_index(use_client=client)

        source_dir = Path(
            "/Users/borisdev/workspace/nobsmed/data/etl_store/study_deep_experiences_enriched/"
        )
        files = [file for file in source_dir.rglob("*.json")]
        print(f"Files: {len(files)}")
        experiences = [Experience(**json.loads(file.read_text())) for file in files]
        start = time.time()
        success = 0
        errors = 0
        docs = []
        for experience in tqdm(experiences):
            docs = [
                cls.from_pydantic(experience)
                for experience in experiences
                if experience.valid_biohack(
                    action_score=action_score, outcomes_score=outcomes_score
                )
            ]
        console.print(f"Bulk loading experiences: {len(docs)}", style="info")
        start = time.time()
        save_batch_size = 500
        docs_batches = list(itertools.batched(docs, save_batch_size))
        number_of_batches = len(docs_batches)
        all_success = []
        all_errors = []

        for idx, docs_batch in enumerate(docs_batches):
            success, errors = helpers.bulk(
                client=client,
                actions=[doc.to_dict(include_meta=True) for doc in docs_batch],
                chunk_size=100,
            )
            console.print(
                f"Batch {idx}/{number_of_batches} Success: {success}, Errors: {errors}",
                style="info",
            )
            all_success.append(success)
            all_errors.append(errors)

        end = time.time()

        console.print(f"Time taken: {end - start}", style="info")
        after_count = cls.count(use_client=client)
        console.print(f"Success: {success}, Errors: {errors}", style="info")
        console.print(
            f"Before count: {before_count}, After count: {after_count}",
            style="info",
        )

    @classmethod
    def rehydrate_index_reddits(
        cls,
        *,
        topics: Iterable[str],
        limit: Optional[int] = None,
        use_client=None,
    ) -> None:
        """
        Takes hour one by one

        Does batch work??
        """
        if use_client is None:
            client = cls.Index.using
        else:
            client = use_client
        try:
            before_count = cls.count(use_client=client)
            print(f"Before count: {before_count}")
        except exceptions.NotFoundError:
            before_count = 0
        cls.re_create_index(use_client=client)
        console.print(f"Topics: {topics}", style="info")
        start = time.time()
        success = 0
        errors = 0
        docs = []
        for topic in topics:
            print(topic)
            o = TopicExperiences.load(name=topic)
            target_experiences = [experience for experience in o.experiences]
            valid_experiences = [
                experience
                for experience in target_experiences
                if experience.valid_biohack(action_score=2, outcomes_score=2)
                and experience.source_type == "reddit"
            ]
            for experience in tqdm(valid_experiences[:limit]):
                doc = cls.from_pydantic(experience)
                docs.append(doc)
        console.print(f"Topics: {topics}", style="info")
        console.print(f"Bulk loading experiences: {len(docs)}", style="info")
        start = time.time()
        save_batch_size = 500
        docs_batches = list(itertools.batched(docs, save_batch_size))
        number_of_batches = len(docs_batches)
        all_success = []
        all_errors = []

        for idx, docs_batch in enumerate(docs_batches):
            success, errors = helpers.bulk(
                client=client,
                actions=[doc.to_dict(include_meta=True) for doc in docs_batch],
                chunk_size=100,
            )
            console.print(
                f"Batch {idx}/{number_of_batches} Success: {success}, Errors: {errors}",
                style="info",
            )
            all_success.append(success)
            all_errors.append(errors)

        """
        22K took 1 hour one by one on local
        """
        end = time.time()

        console.print(f"Time taken: {end - start}", style="info")
        after_count = cls.count(use_client=client)
        console.print(f"Success: {success}, Errors: {errors}", style="info")


if __name__ == "__main__":
    client = opensearch_client
    ExperienceDoc4.re_create_index(use_client=client)
    ExperienceDoc4.rehydrate_index_reddits(
        use_client=client,
        topics=["Biohacking", "Sleep", "Pregnancy"],  # topics are sets of subreddits
    )
    print("ExperienceDoc4 count:", ExperienceDoc4.count(use_client=client))
    ExperienceDoc4.rehydrate_index_studies(
        use_client=client, action_score=1, outcomes_score=1
    )
    print("ExperienceDoc4 count:", ExperienceDoc4.count(use_client=client))
