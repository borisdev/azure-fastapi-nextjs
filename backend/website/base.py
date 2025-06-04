from __future__ import annotations

import gzip
import json
from abc import ABCMeta
from pathlib import Path
from typing import Any, Optional, Union

from loguru import logger
from pydantic import BaseModel
from website.settings import console


class SubredditAttributes(BaseModel):
    display_name: str
    title: str
    public_description: str
    subscribers: Optional[int] = None

    @classmethod
    def from_subreddit(cls, subreddit: FetchedSubreddit) -> SubredditAttributes:
        return cls(
            display_name=subreddit.display_name,
            title=subreddit.title,
            public_description=subreddit.public_description,
            subscribers=subreddit.subscribers,
        )


class Base(BaseModel, metaclass=ABCMeta):
    title: Optional[str] = None
    subreddit: Optional[Union[SubredditAttributes, list[SubredditAttributes]]] = None

    class Config:
        use_enum_values = True

    @classmethod
    def subreddit_metadata(cls, subreddit_name: str) -> SubredditAttributes:
        f = FetchedSubreddit.load_from_subreddit_name(subreddit_name)
        return SubredditAttributes.from_subreddit(f)

    @classmethod
    def get_stored_file_names(cls) -> list[str]:
        files = []
        # get all the files in the store directory
        for path in Path(ETL_STORE_DIR).iterdir():
            if f"{cls.__name__}.json" in path.name:
                files.append(path.stem.split(".")[0])
        return files

    @classmethod
    def load(cls, *, name: str) -> Any:
        # name must be the subreddit name or the topic/title name
        source_path = Path(ETL_STORE_DIR) / f"{name}.{cls.__name__}.json"
        print(source_path)
        with open(source_path, "r") as f:
            data = json.load(f)
        console.print(f"Loaded {cls.__name__} from {source_path}", style="info")
        return cls(**data)

    def name(self) -> str:
        raise NotImplementedError

    def save(self) -> None:
        non_subreddit_classes = [
            "Topic",
            "StudyExperiences",
            "StudyRelevantExperiences",
            "Biohacks",
        ]
        if self.__class__.__name__ in non_subreddit_classes or isinstance(
            self.subreddit, list
        ):
            if self.title is None:
                raise ValueError(
                    f"Title is required for {self.__class__.__name__} to save"
                )
            name = self.title
        else:
            try:
                name = self.subreddit.display_name
            except AttributeError:
                logger.warning(
                    f"Check if you need to add this class name to the non_subreddit_classes list: {self.__class__.__name__}"
                )
                raise Exception(
                    f"Cant save {self.__class__.__name__}. Add it to the non_subreddit_classes list in base.py"
                )

        sink_path = Path(ETL_STORE_DIR) / f"{name}.{self.__class__.__name__}.json"
        with open(sink_path, "w") as f:
            json_dump = self.model_dump_json(indent=2)
            f.write(json_dump)
        console.print(f"Saved to {sink_path}", style="info")

        if self.__class__.__name__ == "Topic":

            zip_sink_path = (
                Path(DEPLOY_DATA_DIR) / f"{name}.{self.__class__.__name__}.json.gz"
            )
            with gzip.open(zip_sink_path, "wt", encoding="utf-8") as f:
                # f.write(
                #     self.model_dump_json(exclude={"enriched_submissions", "post_index"})
                # )
                f.write(self.model_dump_json())
            console.print(f"Saved to {zip_sink_path}", style="info")
