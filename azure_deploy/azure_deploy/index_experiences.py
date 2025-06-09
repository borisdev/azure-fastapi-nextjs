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


class ExperienceDoc4(Document):
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
