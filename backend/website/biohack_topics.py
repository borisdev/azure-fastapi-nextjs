"""
Tag biohack experiences with a topic name created by bertopic_easy_azure.py

Rationale:

- prunes near duplicates biohacks in search results
- opens up new possibilities for search O(1) w/ ML topic prediction from user search input
- opens up weighted topics per person

REMEMBER: Amazon Associates

"""

# step 1 unique_docs_for_each_type()
# step 2 cluster
# step 3 tag each experience with cluster name

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Type, Union

from dotenv import load_dotenv
from loguru import logger
from rich import print

from website.biohacks import TopicExperiences
from website.models import BiohackTypeEnum
from website.settings import ETL_STORE_DIR

load_dotenv()
action_score = 2
outcomes_score = 2

named_clusters: dict[str, list[str]] = {}


def get_docs_file_path(
    *,
    biohack_type: BiohackTypeEnum,
):
    file_path = (
        ETL_STORE_DIR / "biohack_topics" / f"{biohack_type.value}_unique_docs.json"
    )
    return file_path


def get_cluster_file_path(*, biohack_type: BiohackTypeEnum):
    # Create output directory
    output_dir = ETL_STORE_DIR / "biohack_clusters"
    output_dir.mkdir(parents=True, exist_ok=True)
    sink_file = output_dir / f"{biohack_type.value}_topic_docs.json"
    return sink_file


def get_unique_actions(
    *,
    subreddit_type: Literal["Pregnancy", "Sleep", "Biohacking"],
    biohack_type: BiohackTypeEnum,
) -> list[str]:
    o = TopicExperiences.load(name=subreddit_type)
    actions: list[str] = []
    # Extract relevant actions
    target_experiences = [
        experience
        for experience in o.experiences
        if experience.biohack_type == biohack_type.value
    ]
    valid_experiences = [
        experience
        for experience in target_experiences
        if experience.valid_biohack(
            action_score=action_score, outcomes_score=outcomes_score
        )
    ]
    actions = [experience.action for experience in valid_experiences]
    unique_actions = list(set(actions))
    logger.info(
        f"Found {len(unique_actions)} unique actions for {subreddit_type}/{biohack_type.value}"
    )

    return unique_actions


def get_unique_actions_studies(*, biohack_type: BiohackTypeEnum) -> list[str]:
    from website.experiences import Experience

    source_dir = Path(
        "/Users/borisdev/workspace/nobsmed/data/etl_store/study_deep_experiences_enriched/"
    )
    files = [file for file in source_dir.rglob("*.json")]
    print(f"Files: {len(files)}")
    dicts = [json.loads(file.read_text()) for file in files]
    experiences = [Experience(**d) for d in dicts]
    target_experiences = [
        experience
        for experience in experiences
        if experience.biohack_type == biohack_type.value
    ]
    valid_experiences = [
        experience
        for experience in target_experiences
        if experience.valid_biohack(
            action_score=action_score, outcomes_score=outcomes_score
        )
    ]
    actions = [experience.action for experience in valid_experiences]
    unique_actions = list(set(actions))
    return unique_actions


def write_unique_actions(*, biohack_type: BiohackTypeEnum) -> None:
    grand_total_count = 0
    report = {}
    test_action = "Increased omega-3 fatty acid intake through fish consumption and supplements during pregnancy"

    all_actions: list[str] = []
    biohack_type_count = 0
    for subreddit_type in ["Pregnancy", "Sleep", "Biohacking"]:
        actions = get_unique_actions(
            subreddit_type=subreddit_type, biohack_type=biohack_type
        )
        unique_actions = list(set(actions))
        all_actions.extend(unique_actions)
        grand_total_count += len(unique_actions)
        biohack_type_count += len(unique_actions)
    report[biohack_type.value] = biohack_type_count
    file_path = get_docs_file_path(biohack_type=biohack_type)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if biohack_type.value == "diet":
        try:
            assert test_action in all_actions
        except AssertionError:
            logger.error(f"Test failed: {test_action} not found in {file_path}")
            raise

    unique_actions_studies = get_unique_actions_studies(biohack_type=biohack_type)
    all_actions.extend(unique_actions_studies)
    print(f"Type: {biohack_type.value}")
    print(f"Unique actions from studies: {len(unique_actions_studies)}")
    print(f"Unique actions from reddit: {len(all_actions)}")
    print(f"Total unique actions: {len(set(all_actions))}")
    print("---" * 100)
    with open(
        file_path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(all_actions, f)
        logger.info(f"Saved {len(all_actions)} unique actions to {file_path}")

    print("=" * 100)
    print("Report:")
    print(report)

    print(f"Total count: {grand_total_count}")


def cluster(*, biohack_type: BiohackTypeEnum, docs: list[str]) -> None:
    # from bertopic_easy import bertopic_easy
    # need import here to avoid long delay on startup when never required
    from bertopic_easy.main import bertopic_easy_azure
    from bertopic_easy.models import AzureOpenAIConfig

    print(f"Loaded {len(docs)} documents from {docs_file}")
    # check = [d for d in docs if "C to MSM" in d]
    # assert len(check) == 1, f"Expected 1 match, found {len(check)}"

    logger.info(f"Clustering {len(docs)} documents for {type_value}")
    start_time = time.time()

    azure_openai_json = os.environ.get("text-embedding-3-large")
    if azure_openai_json is None:
        raise ValueError(
            "add the AzureOpenAI's `text-embedding-3-large` config to .env file"
        )
    azure_openai_config = AzureOpenAIConfig(**json.loads(azure_openai_json))
    embedding_config = AzureOpenAIConfig(
        api_version=azure_openai_config.api_version,
        azure_endpoint=azure_openai_config.azure_endpoint,
        azure_deployment="text-embedding-3-large",
        api_key=azure_openai_config.api_key,
        timeout=azure_openai_config.timeout,
    )

    naming_config = AzureOpenAIConfig(
        api_version="2024-12-01-preview",
        azure_endpoint="https://boris-m3ndov9n-eastus2.openai.azure.com/",
        azure_deployment="o3-mini",
        api_key=azure_openai_config.api_key,
        timeout=None,
    )

    classifier_config = AzureOpenAIConfig(
        api_version="2024-12-01-preview",
        azure_endpoint="https://boris-m3ndov9n-eastus2.openai.azure.com/",
        azure_deployment="o3-mini",
        api_key=azure_openai_config.api_key,
        timeout=None,
    )
    clusters = bertopic_easy_azure(
        texts=docs,
        reasoning_effort="low",
        subject=f"personal health interventions and outcomes relating to {type_value}",
        azure_embeder_config=embedding_config,
        azure_namer_config=naming_config,
        azure_classifier_config=classifier_config,
    )
    end_time = time.time()
    ## save clusters
    sink_file = get_cluster_file_path(biohack_type=biohack_type)
    clusters_json = clusters.model_dump_json(indent=2)
    with open(sink_file, "w", encoding="utf-8") as f:
        f.write(clusters_json)
    time_taken = end_time - start_time
    logger.info(f"Saved clusters to {sink_file}")
    logger.info(f"Clustering took {time_taken:.2f} seconds")


def tag_study_experiences_with_topics(*, biohack_type: BiohackTypeEnum) -> None:
    UNCLASSIFIED = "unclassified"
    missing_in_lookup = []
    grand_total_count = 0
    if biohack_type.value == "other":
        raise ValueError("Biohack type 'other' is not supported.")
    logger.info(f"Tagging experiences for biohack type: {biohack_type.value}")
    cluster_file_path = get_cluster_file_path(biohack_type=biohack_type)
    with open(cluster_file_path, "r", encoding="utf-8") as f:
        clusters = json.load(f)
    clusters = clusters["clusters"]

    # Create document -> topic lookup
    lookup: dict[str, str] = {}
    for topic, members in clusters.items():
        print(f"Topic: {topic}")
        print(f"Members: {len(members)}")
        for member in members:
            print(f"Member: {member}")
            if topic == UNCLASSIFIED:
                lookup[member["doc"]] = member["doc"]
            else:
                lookup[member["doc"]] = topic

    source_dir = Path(
        "/Users/borisdev/workspace/nobsmed/data/etl_store/study_deep_experiences_enriched/"
    )
    files = [file for file in source_dir.rglob("*.json")]
    print(f"Files: {len(files)}")
    from website.experiences import Experience

    for file in files:
        print(f"Processing file: {file}")
        experience = Experience(**json.loads(file.read_text()))
        if not experience.valid_biohack(
            action_score=action_score, outcomes_score=outcomes_score
        ):
            continue
        action_text = getattr(experience, "action")
        # Look up the topic
        try:
            topic = lookup[action_text]
        except KeyError:
            logger.warning(f"KeyError for action_text: {action_text}")
            print(f"Cluster file: {cluster_file_path}")
            print(f"Type: {biohack_type.value}")
            print(f"Action: {action_text}")
            print(f"Experience:")
            print(experience)
            logger.warning(f"No topic found for action: {action_text}")
            missing_in_lookup.append(action_text)
            continue
        setattr(experience, "biohack_topic", topic)
        grand_total_count += 1
        file.write_text(json.dumps(experience.model_dump(), indent=2))


def tag_experiences_with_topics(*, biohack_type: BiohackTypeEnum) -> None:
    UNCLASSIFIED = "unclassified"
    missing_in_lookup = []
    grand_total_count = 0
    if biohack_type.value == "other":
        raise ValueError("Biohack type 'other' is not supported.")
    logger.info(f"Tagging experiences for biohack type: {biohack_type.value}")
    cluster_file_path = get_cluster_file_path(biohack_type=biohack_type)
    with open(cluster_file_path, "r", encoding="utf-8") as f:
        clusters = json.load(f)
    clusters = clusters["clusters"]

    # Create document -> topic lookup
    lookup: dict[str, str] = {}
    for topic, members in clusters.items():
        print(f"Topic: {topic}")
        print(f"Members: {len(members)}")
        for member in members:
            print(f"Member: {member}")
            if topic == UNCLASSIFIED:
                lookup[member["doc"]] = member["doc"]
            else:
                lookup[member["doc"]] = topic

    for subreddit_type in ["Pregnancy", "Sleep", "Biohacking"]:
        logger.info(f"Processing subreddit type: {subreddit_type}")
        o = TopicExperiences.load(name=subreddit_type)
        updated_count = 0
        target_experiences = [
            experience
            for experience in o.experiences
            if experience.biohack_type == biohack_type.value
        ]
        valid_experiences = [
            experience
            for experience in target_experiences
            if experience.valid_biohack(
                action_score=action_score, outcomes_score=outcomes_score
            )
        ]
        for experience in valid_experiences:
            action_text = getattr(experience, "action")
            # Look up the topic
            try:
                topic = lookup[action_text]
            except KeyError:
                logger.warning(f"KeyError for action_text: {action_text}")
                print(f"Cluster file: {cluster_file_path}")
                print(f"Type: {biohack_type.value}")
                print(f"Action: {action_text}")
                print(f"Subreddit: {subreddit_type}")
                print(f"Experience:")
                print(experience)
                logger.warning(f"No topic found for action: {action_text}")
                missing_in_lookup.append(action_text)
                continue

            setattr(experience, "biohack_topic", topic)
            grand_total_count += 1
            updated_count += 1

        # Save if any experiences were updated
        if updated_count > 0:
            logger.info(
                f"Total tagged experiences for {subreddit_type}/{biohack_type.value}: {grand_total_count}"
            )
            o.save()

    logger.success(f"Total tagged experiences: {grand_total_count}")
    print("Missing in lookup:")
    print(missing_in_lookup)


def test_get_unique_actions_omega3_in_pregnancy_diet():
    result = get_unique_actions(
        subreddit_type="Pregnancy", biohack_type=BiohackTypeEnum.diet
    )

    # Check that the result is a list
    assert isinstance(result, list)

    target_action = "Increased omega-3 fatty acid intake through fish consumption and supplements during pregnancy"
    assert target_action in result
    logger.success(f"Test passed: {target_action} found in the result.")


def test_file_contains_omega3_in_pregnancy_diet():
    file_path = get_docs_file_path(
        biohack_type=BiohackTypeEnum.diet,
    )
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        print(data)
        breakpoint()
        try:
            assert (
                "Increased omega-3 fatty acid intake through fish consumption and supplements during pregnancy"
                in data
            )
            logger.success("Test passed: File contains the expected action.")
        except AssertionError:
            logger.error("Test failed: File does not contain the expected action.")
            raise


if __name__ == "__main__":
    # Sanity check
    # test_get_unique_actions_omega3_in_pregnancy_diet()
    # write_unique_actions(biohack_type=BiohackTypeEnum.diet)
    # test_file_contains_omega3_in_pregnancy_diet()
    # STEP 1
    # for biohack_type in BiohackTypeEnum:
    #     write_unique_actions(biohack_type=biohack_type)
    # STEP 2: about 5 minutes per biohack type?
    # START_HERE = False
    # start_time = time.time()
    # for biohack_type in BiohackTypeEnum:
    #     if biohack_type == BiohackTypeEnum.mental_training_or_therapy:
    #         START_HERE = True
    #     if biohack_type == BiohackTypeEnum.other or START_HERE is False:
    #         print(f"Skipping {biohack_type}")
    #         continue
    #     type_value = biohack_type.value
    #     docs_file = get_docs_file_path(biohack_type=biohack_type)
    #     with open(docs_file, "r", encoding="utf-8") as f:
    #         docs = json.load(f)
    #     print(f"Clustering {len(docs)} documents for {biohack_type}")
    #     cluster(biohack_type=biohack_type, docs=docs)
    # end_time = time.time()
    # print(f"Clustering took {end_time - start_time:.2f} seconds")
    # STEP 3
    # for biohack_type in BiohackTypeEnum:
    #     if biohack_type == BiohackTypeEnum.other:
    #         continue
    #     logger.info(f"Tagging for {biohack_type}")
    #     tag_experiences_with_topics(biohack_type=biohack_type)
    # logger.success("Done tagging experiences with topics.")
    # # STEP 4
    # ### TAG STUDIES!!!
    for biohack_type in BiohackTypeEnum:
        if biohack_type == BiohackTypeEnum.other:
            continue
        logger.info(f"Tagging studies for {biohack_type}")
        tag_study_experiences_with_topics(biohack_type=biohack_type)

    # Bug ...below experience.action is missing from the lookup, exists in raw unique texts, missing from clusters file
    # "action": "Adding vitamin C to MSM supplements or lemon juice to improve effectiveness"
    # cluster(biohack_type=BiohackTypeEnum.supplements)
