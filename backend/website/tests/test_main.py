import os

from fastapi.testclient import TestClient
from rich import print
from rich.traceback import install

from website.main import app
from website.plan_of_attack import plan_of_attack
from website.search import search_biohacks
from website.settings import opensearch_local_client

install(show_locals=True)

client = TestClient(app)

## Unit tests


def test_search_biohacks():
    client = opensearch_local_client
    # PART 1 of 2: Search candidate biohacks - recall
    question = "REM sleep"
    question = "Blueprint diet"
    taxonomy = search_biohacks(
        question=question, client=client, topic_index="experiences_3"
    )
    print(taxonomy)


## E2E tests


def test_read_main():
    response = client.get("/", headers={"Accept": "application/json"})
    assert response.status_code == 200
    print(response.json())
    # assert response.json() == {"msg": "Hello World"}


def test_search_biohacks_e2e():
    response = client.get("/search?question=Blueprint%20diet")
    assert response.status_code == 200
    print(response)


def test_plan():
    question = "Blueprint diet"

    file_path = "tests/fixtures/taxonomy_fixture.json"
    from website.search import DynamicBiohackingTaxonomy

    with open(file_path, "r") as f:
        taxonomy = DynamicBiohackingTaxonomy.model_validate_json(f.read())

    response = plan_of_attack(
        question=question,
        taxonomy=taxonomy,
    )
    print(response)
