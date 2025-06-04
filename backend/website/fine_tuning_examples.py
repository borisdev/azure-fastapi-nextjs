from __future__ import annotations

import itertools
import json
import random
from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar, Literal, Optional

from pydantic import BaseModel, Field
from rich import print
from sentence_transformers import InputExample, SentenceTransformer, losses
from torch.utils.data import DataLoader
from tqdm import tqdm

from website.biohacks import TopicExperiences
from website.chain import Chain
from website.settings import ETL_STORE_DIR, console


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
    other = "other"


class Biohack(BaseModel):
    biohack_subtype: str
    action: str  # context to help shape the training on similarity

    class Config:
        frozen = True

    def __hash__(self):
        return hash((self.biohack_subtype, self.action))


class BiohackPair(BaseModel):
    biohack_1: Biohack
    biohack_2: Biohack

    class Config:
        frozen = True  # Makes the model immutable

    def __hash__(self):
        # Use a tuple of the fields to compute the hash
        return hash((self.biohack_1, self.biohack_2))


class SubtypeActionPair(BaseModel):
    subtype: str
    action: str

    class Config:
        frozen = True  # Makes the model immutable

    def __hash__(self):
        # Use a tuple of the fields to compute the hash
        return hash((self.subtype, self.action))


class Record(BaseModel):
    text1: str
    text2: str
    label: Any


class Examples(BaseModel):
    """
    One embedding model per biohack type
    One file of examples per biohack type: device, diet, exercise, etc.

    Examples to fine-tune the embedding model to dynamically fuzzy cluster experiences into biohacks (topics)

    Approach:

        1. Get all unique values for (biohack_subtype, action)
        2. actual pairs set similarity score = 1
        3. Use LLM to score all other random sampled pairs
        4. to_csv --> sentence_transformers


    def to_csv(self) -> file:
    """

    topics: ClassVar[list[str]] = ["Biohacking", "Pregnancy", "Sleep"]
    # step 1A
    biohack_type: BiohackTypeEnum
    all_biohack_subtypes: list[str]
    all_actions: list[str]
    all_biohacks: list[Biohack]
    # step 1B
    actual_subtype_action_pairs: list[SubtypeActionPair]  # set score to 1
    # step 2
    random_subtype_action_pairs: Optional[list[SubtypeActionPair]] = (
        None  # itertools.product(subtypes, actions) - positives
    )
    # step 3
    random_biohack_pairs: Optional[list[BiohackPair]] = (
        None  # random sample from itertool.combinations
    )
    random_subtype_action_pair_labels: Optional[Record] = None
    random_biohack_pair_labels: Optional[Any] = None  # Optional[Record] = None

    class Config:
        use_enum_values = True

    def describe(self) -> None:
        # count the number of unique subtypes and actions
        num_subtypes = len(self.all_biohack_subtypes)
        num_actions = len(self.all_actions)
        # count the number of actual pairs
        num_actual_subtype_action_pairs = len(self.actual_subtype_action_pairs)
        # count the number of random pairs
        try:
            num_random_subtype_action_pairs = len(self.random_subtype_action_pairs)
        except TypeError:
            num_random_subtype_action_pairs = 0
        try:
            num_random_biohack_pairs = len(self.random_biohack_pairs)
        except TypeError:
            num_random_biohack_pairs = 0
        report = f"""
        Biohack Type: {self.biohack_type}
        Number of unique biohacks: {len(self.all_biohacks)}
        Number of unique subtypes: {num_subtypes}
        Number of unique actions: {num_actions}
        Number of actual subtype-action pairs: {num_actual_subtype_action_pairs}
        Number of random subtype-action pairs: {num_random_subtype_action_pairs}
        Number of random biohack pairs: {num_random_biohack_pairs}
        """
        print(report)

    @classmethod
    def file_path(cls, biohack_type) -> Path:
        return Path(ETL_STORE_DIR) / f"{biohack_type}.{cls.__name__}.json"

    @classmethod
    def load(cls, *, biohack_type: BiohackTypeEnum) -> Examples:
        source_path = cls.file_path(biohack_type.value)
        print(f"Loading {source_path}")
        with open(source_path, "r") as f:
            data = json.load(f)
        console.print(f"Loaded {cls.__name__} from {source_path}", style="info")
        return cls(**data)

    def save(self) -> None:
        sink_path = self.file_path(self.biohack_type)
        with open(sink_path, "w") as f:
            json_dump = self.model_dump_json(indent=2)
            f.write(json_dump)
        console.print(f"Saved to {sink_path}", style="info")

    @classmethod
    def step_1(cls, *, biohack_type: BiohackTypeEnum) -> None:
        all_subtypes = set()
        all_actions = set()
        all_biohacks = set()
        positive_subtype2action = defaultdict(list)
        for topic in cls.topics:
            o = TopicExperiences.load(name=topic)
            for e in tqdm(o.experiences):
                if e.biohack_type is not None:
                    if e.biohack_type == biohack_type.value:
                        if e.biohack_subtype is not None:
                            if e.action_score < 2:
                                continue
                            if e.outcomes_score < 2:
                                continue
                            if e.clinical_trial_study is False:
                                continue
                            positive_subtype2action[e.biohack_subtype].append(e.action)
                            all_subtypes.add(e.biohack_subtype)
                            all_actions.add(e.action)
                            all_biohacks.add(
                                Biohack(
                                    biohack_subtype=e.biohack_subtype, action=e.action
                                )
                            )

        actual_subtype_action_pairs: list[SubtypeActionPair] = []
        for k, v in positive_subtype2action.items():
            for v in v:
                actual_subtype_action_pairs.append(
                    SubtypeActionPair(subtype=k, action=v)
                )
        # dedup
        actual_subtype_action_pairs = list(set(actual_subtype_action_pairs))
        instance = cls(
            biohack_type=biohack_type,
            all_biohack_subtypes=list(all_subtypes),
            all_actions=list(all_actions),
            actual_subtype_action_pairs=actual_subtype_action_pairs,
            all_biohacks=list(all_biohacks),
        )
        instance.save()

    def step2_set_random_biohack_pairs(self) -> None:
        """
        1. Get 10,000 unique random pairs of biohacks_subtypes-w-action-context.
        2. LLM looks at two biohacks-w-action-context to generate synthetic similiarity scores.
        3. Then fine-tune the opensource model with just the biohack_subtype and no action-context.
        """
        biohacks = self.all_biohacks

        def random_sample_batch():
            # 5000 x 5000 is too large a number of pairs so we will take 1 of 100 sample pairs
            it = itertools.combinations(biohacks, 2)
            while True:
                batch = list(itertools.islice(it, 1000))
                if not batch:
                    return
                yield random.sample(batch, 10)

        items = []
        for idx, random_sample in enumerate(random_sample_batch()):
            print(f"No. {idx} random sample")
            for biohack_1, biohack_2 in random_sample:
                biohack_pair = BiohackPair(biohack_1=biohack_1, biohack_2=biohack_2)
                items.append(biohack_pair)
        console.print(f"Created {len(items)} pairwise sim score inputs")
        self.random_biohack_pairs = items
        self.save()

    def step3_set_random_biohack_subtype_action_pairs(self) -> None:
        subtypes = self.all_biohack_subtypes
        actions = self.all_actions

        def random_sample_batch():
            # 5000 x 5000 is too large a number of pairs so we will take 1 of 100 sample pairs
            it = itertools.product(subtypes, actions)
            while True:
                batch = list(itertools.islice(it, 1000))
                if not batch:
                    return
                yield random.sample(batch, 10)

        items = []
        for idx, random_sample in enumerate(random_sample_batch()):
            print(f"No. {idx} random sample")
            for subtype, action in random_sample:
                subtype_action_pair = SubtypeActionPair(subtype=subtype, action=action)
                items.append(subtype_action_pair)
        items = list(set(items))
        console.print(f"Created {len(items)} random unique subtype-action pairs")
        self.random_subtype_action_pairs = items
        self.save()

    async def step4_label_random_biohack_pairs(
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
        class LabelInput(BaseModel):
            biohack_1: Biohack
            biohack_2: Biohack

        class LabelResponse(BaseModel):
            label: Literal["POS", "HARD_POS", "HARD_NEG", "NEG"] = Field(
                title="Subsumed",
                description="""
                    Biohack 1 is the anchor in fine-tuning an embedding model with MNR.

                    Guidelines:
                    -----------------------

                    - Write POS if Biohack 1 subsumes Biohack 2, i.e. Biohack 1 is a parent of Biohack 2.
                    - Write POS is Biohack 1 and Biohack 2 look like duplicates to most people.
                    - Write HARD_POS is Biohack 1 and Biohack 2 look different, but also like siblings of the same parent.
                    - Write HARD_NEG if Biohack 2 subsumes Biohack 1, i.e. Biohack 2 is a parent of Biohack 1.
                    - Write NEG if they are unrelated, ie. neither is a parent or sibbling of the other.
                """,
            )

        class LabelChain(Chain):

            input_schema = LabelInput
            output_schema = LabelResponse

            @classmethod
            def make_input_text(cls, *, input: LabelInput) -> str:
                input_text = f"""

                    Biohack 1
                    ---------------

                    Biohack 1 name: {input.biohack_1.biohack_subtype}
                    Biohack 1 example action: {input.biohack_1.action}

                    Biohack 2
                    -----------------

                    Biohack 2 name: {input.biohack_2.biohack_subtype}
                    Biohack 2 example action: {input.biohack_2.action}


                """
                return input_text

        responses = await LabelChain.batch_predict(
            size=batch_size,
            llm_name=llm_name,
            input_objects=[
                LabelInput(biohack_1=pair.biohack_1, biohack_2=pair.biohack_2)
                for pair in self.random_biohack_pairs[start : start + size]
            ],
            max_tokens=max_tokens,
            max_retries=max_retries,
            timeout=timeout,
        )
        records = []
        for biohack_pair, response in zip(self.random_biohack_pairs, responses):
            records.append(
                Record(
                    text1=biohack_pair.biohack_1.model_dump_json(indent=2),
                    text2=biohack_pair.biohack_2.model_dump_json(indent=2),
                    label=response.label,
                )
            )
        print(records)
        print(f"Got {len(records)} labels")
        self.random_biohack_pair_labels = records
        self.save()

    def step5_label_random_subtype_action_pairs(self) -> None:
        pass

    def mmr_fine_tune(self, epochs=7) -> None:
        # https://medium.com/@jithinanievarghese/hard-mining-negatives-for-semantic-similarity-model-using-sentence-transformers-c3e271af6c25
        # Training or Fine Tuning a sentence transformer model with MNR Loss
        # where all-MiniLM-L6-v2 is a pre-trained  sentence-transformer model
        base_model = "all-MiniLM-L6-v2"
        model = SentenceTransformer(f"sentence-transformers/{base_model}", device="cpu")
        train_examples = [
            InputExample(texts=[pair.subtype, pair.action])
            for pair in self.actual_subtype_action_pairs
        ]

        train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=32)
        train_loss = losses.MultipleNegativesRankingLoss(model=model)
        model.fit(
            train_objectives=[(train_dataloader, train_loss)],
            epochs=epochs,
            warmup_steps=100,
        )
        model.save(f"{ETL_STORE_DIR}/{base_model}-mmr")


if __name__ == "__main__":
    # Anchor - Positive (Maybe I cant do this since I have too many false negatives)
    # Train biohack-action model for clustering
    # Train outcomes field for search
    # Examples.step_1(biohack_type=BiohackTypeEnum.device)
    examples = Examples.load(biohack_type=BiohackTypeEnum.device)
    # examples.step2_set_random_biohack_pairs()
    # examples.step3_set_random_biohack_subtype_action_pairs()
    # print(examples.actual_subtype_action_pairs)
    # print(examples.actual_subtype_action_pairs)
    # examples.describe()
    # asyncio.run(
    #     examples.step4_label_random_biohack_pairs(
    #         start=0,
    #         size=100,
    #         batch_size=100,
    #         llm_name="gpt-4o",
    #         max_tokens=10,
    #         max_retries=1,
    #         timeout=6,
    #     )
    # )
    # # print(examples.random_biohack_pair_labels)
    # examples.describe()
    examples.mmr_fine_tune(epochs=7)
    """
Asymmetrical Anchor Positives: This concept might refer to a scenario where the relationship between anchors and positives is not uniform or symmetrical. For example, the positive examples might vary in their degree of similarity to the anchor, or the model might be trained to focus on certain aspects of similarity over others. This can help in capturing more nuanced relationships within subsets of data.

    SHOULD THIS BE A HARD NEGATIVE?

        Record(
        text1='{\n  "biohack_subtype": "auto-titrating positive airway pressure (APAP) therapy",\n  "action": "Utilizing auto-titrating positive airway pressure (APAP) therapy for Obstructive Sleep Apnea (OSA)
treatment"\n}',
        text2='{\n  "biohack_subtype": "CPAP machine",\n  "action": "Using a CPAP machine to manage sleep apnea"\n}',
        label=True
    ),
    """
