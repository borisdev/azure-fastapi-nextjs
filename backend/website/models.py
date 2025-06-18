from __future__ import annotations

import base64
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, computed_field


class AISummary(BaseModel):
    balance: list[str]
    skeptical: list[str]
    curious: list[str]
    mechanisms: list[str]


class BiohackTypeEnum(Enum):
    diet = "diet"
    device = "device"
    exercise = "exercise"
    sleep_habit = "sleep habit"
    prescription_drug = "prescription drug"
    supplements = "supplements"
    nootropics_smart_drugs_or_psychedelics = "nootropics, smart drugs, or psychedelics"
    lifestyle_or_habit = "lifestyle or habit"
    environmental_exposure = "environmental exposure"
    social_context = "social context"
    physical_training_or_therapy = "physical training or therapy"
    mental_training_or_therapy = "mental training or therapy"
    diagnostic_method = "diagnostic method"
    light_exposure = "light exposure"
    vaccine = "vaccine"
    surgery = "surgery"
    other = "other"


# convert above to a Literal for type hinting
BiohackTypeLiteral = Literal[tuple(c.value for c in BiohackTypeEnum)]


class Experience(BaseModel):
    # surface: symptons, personal context
    # Biohacks action_topics
    # Biohacks should be unique tuples of (action topic, personal context topic)
    surprising: Optional[bool] = None
    impact: Optional[bool] = None
    irrelevant: Optional[bool] = None
    anti_premise: Optional[bool] = None
    tags: Optional[list[str]] = None
    cross_encoder_score: Optional[float] = None
    rationale: Optional[str] = None
    id: Optional[int] = None
    biohack_slug: Optional[str] = None
    permalink: str
    takeaway: Optional[str] = None
    clinical_trial_study: Optional[bool] = None
    biohack_topic: Optional[str] = None  # Enrichment based on clustered actions
    biohack_type: Optional[str] = None  # should this be a list? multiple biohack types?
    biohack_subtype: Optional[str] = (
        None  # DEPRECATED a distilled action that might have lost too much info
    )
    action: str
    action_tag: Optional[str] = None
    action_embedding: Optional[list[float]] = None
    health_disorder: str
    outcomes: str
    personal_context: Optional[str] = None
    mechanism: Optional[str] = None
    action_score: Optional[int] = None
    outcomes_score: Optional[int] = None

    class Config:
        arbitrary_types_allowed = True

    @property
    def pretty_json(self) -> str:
        return self.model_dump_json(indent=4)

    @property
    def score(self) -> int:
        if self.action_score is None:
            raise ValueError("Action score is None")
        if self.outcomes_score is None:
            raise ValueError("Outcomes score is None")
        return self.action_score + self.outcomes_score

    @computed_field
    @property
    def source_type(self) -> str:
        if "10." in self.permalink:
            return "study"
        else:
            return "reddit"

    @computed_field
    @property
    def url(self) -> str:
        if self.source_type == "study":
            return f"https://doi.org/{self.permalink}"
        elif self.source_type == "reddit":
            return f"https://www.reddit.com{self.permalink}"
        else:
            raise ValueError(
                f"Not implememted yet to make URL for this source type {self.source_type}"
            )

    @computed_field
    @property
    def key(self) -> bytes:
        data_bytes = self.permalink.encode("utf-8")
        encoded_bytes = base64.urlsafe_b64encode(data_bytes)
        return encoded_bytes

    def valid_biohack(self, *, action_score: int, outcomes_score: int) -> bool:
        if (
            self.biohack_type is None
            or self.action_score is None
            or self.outcomes_score is None
        ):
            return False
        if (
            self.biohack_type is not None
            and self.biohack_type != "other"
            and self.clinical_trial_study is not False
            and self.action_score >= 2
            and self.outcomes_score >= 2
        ):
            return True
        else:
            return False


class DynamicBiohack(BaseModel):
    biohack_topic: Optional[str] = None
    experiences: list[Experience]
    balance: Optional[bool] = None
    skeptical: Optional[bool] = None
    curious: Optional[bool] = None
    # bm25_score: Optional[float] = None
    # cosine_score: Optional[float] = None
    # ai_score: Optional[float] = None

    @property
    def biohack_type(self):
        return self.experiences[0].biohack_type

    @property
    def mechanisms(self):
        mechanisms = []
        for experience in self.experiences:
            if experience.mechanism is None:
                continue
            mechanisms.extend(experience.mechanism.split(","))
        # unique
        mechanisms = list(set(mechanisms))
        if len(mechanisms) == 0:
            mechanisms = ["None"]
        elif len(mechanisms) == 1:
            mechanisms = mechanisms[0]
        else:
            mechanisms = ", ".join(mechanisms)
        return mechanisms


class BiohackTypeGroup(BaseModel):
    biohack_type: str
    biohacks: list[DynamicBiohack]


class DynamicBiohackingTaxonomy(BaseModel):
    biohack_types: list[BiohackTypeGroup]
    count_experiences: int
    count_reddits: int
    count_studies: int


class EnrichBiohackInput(BaseModel):
    question: str
    biohack: DynamicBiohack
