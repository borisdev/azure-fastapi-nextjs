"""
Blueprint for OpenSearch API calls
https://github.com/opensearch-project/ml-commons/blob/main/docs%2Fremote_inference_blueprints%2Fazure_openai_connector_embedding_blueprint.md


"""

import time

from loguru import logger
from opensearchpy import exceptions
from pydantic import BaseModel
from random_word import RandomWords
from rich import print

from website.chain import endpoints
from website.settings import opensearch_cloud_client, opensearch_local_client

r = RandomWords()

# 'Connector URL is not matching the trusted connector endpoint regex, URL is:
# https://boris-m3ndov9n-eastus2.cognitiveservices.azure.com/openai/deployments/text-embedding-3-large/embeddings?api-version=2023-05-15'


def step1_add_trusted_azure_endpoints():
    azure_trusted_connector_endpoints_regex = {
        "persistent": {
            "plugins.ml_commons.trusted_connector_endpoints_regex": [
                "^https:\/\/openai-rg-nobsmed\.openai\.azure\.com\/.*",
                "^https:\/\/.*\.azure\.com\/.*",
            ]
        }
    }

    response = client.cluster.put_settings(body=azure_trusted_connector_endpoints_regex)
    print(response)
    cluster_settings = client.cluster.get_settings()
    print(cluster_settings)


def step2_allow_model_access_control():
    settings = {
        "persistent": {"indices.recovery.max_bytes_per_sec": "50mb"},
        "transient": {"cluster.routing.allocation.enable": "all"},
        "transient": {"plugins.ml_commons.model_access_control_enabled": "true"},
    }
    response = client.cluster.put_settings(body=settings)
    print(response)


def step3_register_model_group():
    # POST /_plugins/_ml/model_groups/_register
    model_group_payload = {
        "name": "boris_embeddings_model_group",
        "description": "A model group for embedding the biohack dimensions",
        "access_mode": "public",
    }
    response = client.transport.perform_request(
        method="POST",
        url="/_plugins/_ml/model_groups/_register",
        body=model_group_payload,
    )
    print(response)
    # {'model_group_id': 'nzezN5QBUIURTgwVd_3M', 'status': 'CREATED'}


def step4_embedding_connector_old():
    """
    Blueprint: https://github.com/opensearch-project/ml-commons/blob/main/docs%2Fremote_inference_blueprints%2Fazure_openai_connector_embedding_blueprint.md#2-create-connector-for-azure-openai-embedding-model

    POST /_plugins/_ml/connectors/_create

    https://openai-rg-nobsmed.openai.azure.com/openai/deployments/text-embedding-3-large/embeddings?api-version=2023-05-15'

    """
    connector_payload = {
        "name": "text-embedding-3-large",
        "description": "AzureOpenAI's text-embedding-3-large",
        "version": "1",
        "protocol": "http",
        "parameters": {
            "endpoint": "openai-rg-nobsmed.openai.azure.com",
            "deploy-name": "text-embedding-3-large",
            "model": "text-embedding-3-large",
            "api-version": "2023-05-15",
        },
        "credential": {"openAI_key": "62ef467f1d4f435f8aa4d2b105bbf44e"},
        "actions": [
            {
                "action_type": "predict",
                "method": "POST",
                "url": "https://${parameters.endpoint}/openai/deployments/${parameters.deploy-name}/embeddings?api-version=${parameters.api-version}",
                "headers": {"api-key": "${credential.openAI_key}"},
                "request_body": '{ "input": ${parameters.input}}',
                "pre_process_function": "connector.pre_process.openai.embedding",
                "post_process_function": "connector.post_process.openai.embedding",
            }
        ],
    }
    response = client.transport.perform_request(
        method="POST",
        url="/_plugins/_ml/connectors/_create",
        body=connector_payload,
    )
    print(response)
    # {'connector_id': 'qDfpOJQBUIURTgwVE_2b'}


class EmbeddingConnector(BaseModel):
    name: str
    endpoint: str
    deploy_name: str
    model: str
    api_version: str
    openAI_key: str

    def create(self):
        """
        Blueprint: https://github.com/opensearch-project/ml-commons/blob/main/docs%2Fremote_inference_blueprints%2Fazure_openai_connector_embedding_blueprint.md#2-create-connector-for-azure-openai-embedding-model
        POST /_plugins/_ml/connectors/_create
        """
        connector_payload = {
            "name": self.name,
            "description": f"AzureOpenAI's {self.name}",
            "version": "2",
            "protocol": "http",
            "parameters": {
                "endpoint": self.endpoint,
                "deploy-name": self.deploy_name,
                "model": self.model,
                "api-version": self.api_version,
            },
            "credential": {"openAI_key": self.openAI_key},
            "actions": [
                {
                    "action_type": "predict",
                    "method": "POST",
                    "url": f"https://${{parameters.endpoint}}/openai/deployments/${{parameters.deploy-name}}/embeddings?api-version=${{parameters.api-version}}",
                    "headers": {"api-key": f"${{credential.openAI_key}}"},
                    "request_body": '{ "input": ${parameters.input}}',
                    "pre_process_function": "connector.pre_process.openai.embedding",
                    "post_process_function": "connector.post_process.openai.embedding",
                }
            ],
        }
        response = client.transport.perform_request(
            method="POST",
            url="/_plugins/_ml/connectors/_create",
            body=connector_payload,
        )
        print(response)
        # {'connector_id': 'UjizPZQBUIURTgwVbARa'}
        return response


def step4_embedding_connector():
    embedding_connector = EmbeddingConnector(
        name="text-embedding-3-large",
        endpoint="boris-m3ndov9n-eastus2.cognitiveservices.azure.com",
        deploy_name="text-embedding-3-large",
        model="text-embedding-3-large",
        api_version="2023-05-15",
        openAI_key="0348WHlAHbFs7btXVbY21gTSP6BK50IRXo5HGu76fIERhFfo8iZGJQQJ99AKACHYHv6XJ3w3AAAAACOGVbze",
    )
    embedding_connector.create()
    # {'connector_id': 'UjizPZQBUIURTgwVbARa'}


def step5_register_connector_to_model_group(*, model_payload: dict):
    response = client.transport.perform_request(
        method="POST", url="/_plugins/_ml/models/_register", body=model_payload
    )
    print(response)
    # {'task_id': 'qTftOJQBUIURTgwV-v1O', 'status': 'CREATED', 'model_id': 'qjftOJQBUIURTgwV-_0B'}
    # {'task_id': 'Uzi1PZQBUIURTgwViwQ5', 'status': 'CREATED', 'model_id': 'VDi1PZQBUIURTgwViwRe'}


def step6_deploy(*, model_id: str):
    response = client.transport.perform_request(
        method="POST", url=f"/_plugins/_ml/models/{model_id}/_deploy"
    )
    print(response)
    # {'task_id': 'qzf1OJQBUIURTgwVWv0A', 'task_type': 'DEPLOY_MODEL', 'status': 'COMPLETED'}


def step7_test_inference():
    """
    POST /_plugins/_ml/models/PSB1josB2yd36FqHAnl1/_predict
    {
      "parameters": {
        "input": [ "What is the meaning of life?" ]
      }
    }
    """
    model_id = "qjftOJQBUIURTgwV-_0B"
    payload = {
        "parameters": {
            "input": ["What is the meaning of life?"],
        }
    }
    response = client.transport.perform_request(
        method="POST",
        url=f"/_plugins/_ml/models/{model_id}/_predict",
        body=payload,
    )
    print(response)
    # {
    # 'inference_results': [
    #     {
    #         'output': [
    #             {
    #                 'name': 'sentence_embedding',
    #                 'data_type': 'FLOAT32',
    #                 'shape': [3072],
    #                 'data': [
    #                     -0.021217346,
    #                     -0.03009174,
    #                     -0.007905752,
    #                     0.034407135,
    #                     -0.077491455,
    #                     -0.003909374,
    #                     .
    #                     .
    #                     .
    #                     ]
    #             }
    #         ]
    #     }
    # ]
    # }


def step8_embedding_pipeline(*, mini_model_id: str, name: str, openai_model_id: str):
    # model_id = "VDi1PZQBUIURTgwViwRe"
    # name = "text-embedding-3-large-east2"
    ingest_pipeline = {
        "description": f"{name} pipeline",
        "processors": [
            {
                "text_embedding": {
                    "model_id": mini_model_id,
                    "field_map": {"action": "action_embedding"},
                }
            },
            {
                "text_embedding": {
                    "model_id": mini_model_id,
                    "field_map": {"health_disorder": "health_disorder_embedding"},
                }
            },
            {
                "text_embedding": {
                    "model_id": mini_model_id,
                    "field_map": {"outcomes": "outcomes_embedding"},
                }
            },
            {
                "text_embedding": {
                    "model_id": mini_model_id,
                    "field_map": {"mechanism": "mechanism_embedding"},
                }
            },
            {
                "text_embedding": {
                    "model_id": mini_model_id,
                    "field_map": {"personal_context": "personal_context_embedding"},
                }
            },
            {
                "text_embedding": {
                    "model_id": mini_model_id,
                    "field_map": {"biohack_subtype": "biohack_subtype_embedding"},
                }
            },
            {
                "text_embedding": {
                    "model_id": openai_model_id,
                    "field_map": {
                        "biohack_subtype": "biohack_subtype_openai_embedding"
                    },
                }
            },
        ],
    }
    response = client.ingest.put_pipeline(id=name, body=ingest_pipeline)
    print(response)


def step9_create_index_to_test_embedding_pipeline():
    config = {
        "settings": {
            "index.knn": True,
            "default_pipeline": "text-embedding-3-large-east2",
        },
        "mappings": {
            "properties": {
                "action": {"type": "text"},
                "action_embedding": {
                    "type": "knn_vector",
                    "dimension": 3072,
                    "method": {
                        "engine": "lucene",
                        "space_type": "l2",
                        "name": "hnsw",
                        "parameters": {},
                    },
                },
                "health_disorder": {"type": "text"},
                "health_disorder_embedding": {
                    "type": "knn_vector",
                    "dimension": 3072,
                    "method": {
                        "engine": "lucene",
                        "space_type": "l2",
                        "name": "hnsw",
                        "parameters": {},
                    },
                },
                "outcomes": {"type": "text"},
                "outcomes_embedding": {
                    "type": "knn_vector",
                    "dimension": 3072,
                    "method": {
                        "engine": "lucene",
                        "space_type": "l2",
                        "name": "hnsw",
                        "parameters": {},
                    },
                },
                "mechanism": {"type": "text"},
                "mechanism_embedding": {
                    "type": "knn_vector",
                    "dimension": 3072,
                    "method": {
                        "engine": "lucene",
                        "space_type": "l2",
                        "name": "hnsw",
                        "parameters": {},
                    },
                },
                "personal_context": {"type": "text"},
                "personal_context_embedding": {
                    "type": "knn_vector",
                    "dimension": 3072,
                    "method": {
                        "engine": "lucene",
                        "space_type": "l2",
                        "name": "hnsw",
                        "parameters": {},
                    },
                },
            }
        },
    }
    index_name = "test-embedding-pipe"
    try:
        logger.warning(f"Deleting index `{index_name}`")
        client.indices.delete(index=index_name)
        logger.warning(f"Index `{index_name}` deleted")
    except exceptions.NotFoundError:
        pass
    response = client.indices.create(index_name, body=config)
    print(response)


def step10_populate_index():
    """
    POST /test-embedding-pipe/_doc
    """
    docs = [
        {
            "action": "action1",
            "health_disorder": "health_disorder1",
            "outcomes": "outcomes1",
            "mechanism": "mechanism1",
        },
        {
            "action": "melatonin supplementation",
            "health_disorder": "insomnia",
            "outcomes": "improved sleep",
            "mechanism": "regulation of circadian rhythm",
        },
        {
            "action": "omega-3 supplementation",
            "health_disorder": "depression",
            "outcomes": "improved mood",
            "mechanism": "regulation of neurotransmitters",
        },
    ]
    for i in range(100):
        print(f"insert random docs {i}", end="")
        random_doc = {
            "action_label": r.get_random_word(),
            "health_disorder_label": r.get_random_word(),
            "outcomes_label": r.get_random_word(),
            "mechanism_label": r.get_random_word(),
            "personal_context_label": r.get_random_word(),
            "action": r.get_random_word(),
            "health_disorder": r.get_random_word(),
            "outcomes": r.get_random_word(),
            "mechanism": r.get_random_word(),
            "personal_context": r.get_random_word(),
        }
        docs.append(random_doc)
    for doc in docs:
        response = client.index(index="test-embedding-pipe", body=doc)
        print(response)


def step11_query_index():
    model_id = "VDi1PZQBUIURTgwViwRe"

    should = [
        {
            "script_score": {
                "query": {
                    "neural": {
                        "action_embedding": {
                            "query_text": "supplements",
                            "model_id": model_id,
                            "k": 10,
                        }
                    }
                },
                "script": {"source": "_score * 1.5"},
            }
        },
        {
            "script_score": {
                "query": {
                    "neural": {
                        "health_disorder_embedding": {
                            "query_text": "sadness",
                            "model_id": "qjftOJQBUIURTgwV-_0B",
                            "k": 10,
                        }
                    }
                },
                "script": {"source": "_score * 1.5"},
            }
        },
    ]

    # projection = ["action", "health_disorder", "outcomes", "mechanism"]
    projection = ["action_label", "health_disorder"]
    query = {"query": {"bool": {"should": should}}, "_source": projection}

    response = client.search(index="test-embedding-pipe", body=query)
    print(response)


# opensearch pretrained-models
def step0_cluster_settings():
    """
    # https://opensearch.org/blog/what-in-the-ml-is-going-on-around-here/
    https://opensearch.org/docs/latest/ml-commons-plugin/pretrained-models/
    PUT _cluster/settings
    {
      "persistent": {
        "plugins.ml_commons.only_run_on_ml_node": "false",
        "plugins.ml_commons.model_access_control_enabled": "true",
        "plugins.ml_commons.native_memory_threshold": "99"
      }
    }
    """
    settings = {
        "persistent": {
            "plugins.ml_commons.allow_registering_model_via_url": "true",
            "plugins.ml_commons.only_run_on_ml_node": "false",
            "plugins.ml_commons.model_access_control_enabled": "true",
            "plugins.ml_commons.native_memory_threshold": "99",
        }
    }
    response = client.cluster.put_settings(body=settings)
    print(response)


def step1_upload():
    """
    # https://opensearch.org/blog/what-in-the-ml-is-going-on-around-here/
    POST /_plugins/_ml/models/_upload
    {
      "name": "huggingface/sentence-transformers/all-MiniLM-L12-v2",
      "version": "1.0.1",
      "model_format": "TORCH_SCRIPT"
    }
    """
    model_payload = {
        "name": "huggingface/sentence-transformers/all-MiniLM-L12-v2",
        "version": "1.0.1",
        "model_format": "TORCH_SCRIPT",
    }
    response = client.transport.perform_request(
        method="POST", url="/_plugins/_ml/models/_upload", body=model_payload
    )
    print(response)


def step2_get_status(*, task_id: str):
    """
    GET /_plugins/_ml/tasks/K7sHR5QBBNwU8U85Exq1
    """
    task_id = "K7sHR5QBBNwU8U85Exq1"
    response = client.transport.perform_request(
        method="GET", url=f"/_plugins/_ml/tasks/{task_id}"
    )
    print(response)

    # payload = {
    #     "name": "huggingface/sentence-transformers/msmarco-distilbert-base-tas-b",
    #     "version": "1.0.2",
    #     "model_group_id": "SLs9R5QBBNwU8U85QBqP",
    #     "model_format": "TORCH_SCRIPT",
    # }


if __name__ == "__main__":
    client = opensearch_local_client
    ## opensearch pretrained-models
    # step0_cluster_settings()
    # response = client.transport.perform_request(
    #     method="POST",
    #     url="/_plugins/_ml/model_groups/_register",
    #     body={
    #         "name": "local_model_group",
    #         "description": "A model group for local models",
    #     },
    # )
    # print(response)
    # {'model_group_id': 'uN3SUZQBhhl9PJaTPPa7', 'status': 'CREATED'}
    model_group_id = "uN3SUZQBhhl9PJaTPPa7"
    # model_name = "all-MiniLM-L6-v2"
    # version = "1.0.1"
    # response = client.transport.perform_request(
    #     method="POST",
    #     url="/_plugins/_ml/models/_register",
    #     body={
    #         "name": f"huggingface/sentence-transformers/{model_name}",
    #         "version": version,
    #         "model_group_id": model_group_id,
    #         "model_format": "TORCH_SCRIPT",
    #     },
    # )
    # #
    # print(response)
    # task_id = "ud3UUZQBhhl9PJaTQvZ_"
    # response = client.transport.perform_request(
    #     method="GET", url=f"/_plugins/_ml/tasks/{task_id}"
    # )
    # # FOR all-MiniLM-L6-v2
    # print(response)
    """
    {
        'model_id': 'ut3UUZQBhhl9PJaTRvbM',
        'task_type': 'REGISTER_MODEL',
        'function_name': 'TEXT_EMBEDDING',
        'state': 'COMPLETED',
        'worker_node': ['LrPLqECuQjeY1XdBVpsU2Q'],
        'create_time': 1736539652733,
        'last_update_time': 1736539782232,
        'is_async': True
    }
    """
    mini_model_id = "ut3UUZQBhhl9PJaTRvbM"  # all-MiniLM-L6-v2
    # # # Step 3: Deploy the model
    # response = client.transport.perform_request(
    #     method="POST", url=f"/_plugins/_ml/models/{model_id}/_deploy"
    # )
    # print(response)
    # task_id = "VO-WSJQBDfMCDXedOp5H"
    # response = client.transport.perform_request(
    #     method="GET", url=f"/_plugins/_ml/tasks/{task_id}"
    # )
    # # FOR all-MiniLM-L6-v2
    # print(response)
    # # Step 4 (Optional): Test the model
    # response = client.transport.perform_request(
    #     method="POST",
    #     url=f"/_plugins/_ml/_predict/text_embedding/{model_id}",
    #     body={
    #         "text_docs": ["today is sunny"],
    #         "return_number": True,
    #         "target_response": ["sentence_embedding"],
    #     },
    # )
    # end = time.time()
    # print(response)
    # print("elapsed time:", end - start)
    # # # elapsed time: 0.3
    # step8_embedding_pipeline(model_id=model_id, name="all-MiniLM-L6-v2")
    ##### END NEW Mini ####

    # {'model_group_id': 'SLs9R5QBBNwU8U85QBqP', 'status': 'CREATED'}
    # step1_upload()
    # response = {"task_id": "RLs1R5QBBNwU8U85nBqW", "status": "CREATED"}
    # {'task_id': 'Rrs5R5QBBNwU8U85axpp', 'status': 'CREATED'}
    # step2_get_status(task_id="Rrs5R5QBBNwU8U85axpp")

    ##### START ######
    ## OpenAI embedding model
    # step1_add_trusted_azure_endpoints()
    # step2_allow_model_access_control()
    # step3_register_model_group()
    # step4_embedding_connector()
    # {'connector_id': 'sVfxZpQBt9Pse56uG892'}
    # step5_register_connector_to_model_group(
    #     model_payload={
    #         "name": "text-embedding-3-large",
    #         "function_name": "remote",
    #         "model_group_id": model_group_id,
    #         "description": "text-embedding-3-large",
    #         "connector_id": "sVfxZpQBt9Pse56uG892",
    #     }
    # )
    # {'task_id': 'slf1ZpQBt9Pse56uPs-q', 'status': 'CREATED', 'model_id': 's1f1ZpQBt9Pse56uP88Z'}

    # step6_deploy(model_id="s1f1ZpQBt9Pse56uP88Z")
    # {'task_id': 'tFf3ZpQBt9Pse56uJs81', 'task_type': 'DEPLOY_MODEL', 'status': 'COMPLETED'}
    # step7_test_inference()
    # step8_embedding_pipeline()
    # name = "text-embedding-3-large"
    openai_model_id = "s1f1ZpQBt9Pse56uP88Z"
    step8_embedding_pipeline(
        mini_model_id=mini_model_id,
        name="all-MiniLM-L6-v2-AND-text-embedding-3-large",
        openai_model_id=openai_model_id,
    )
    # step9_create_index_to_test_embedding_pipeline()
    # step10_populate_index()
    # step11_query_index()
