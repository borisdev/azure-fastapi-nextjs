import os
from pathlib import Path

# import redis
from loguru import logger
from opensearchpy import OpenSearch
from rich import print
from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({"info": "dim cyan", "warning": "magenta", "danger": "bold red"})
console = Console(theme=custom_theme)

AZURE_OPENAI_API_KEY = os.environ["AZURE_OPENAI_API_KEY"]
west_api_key = os.environ["WEST_API_KEY"]
eastus2_api_key = os.environ["EASTUS2_API_KEY"]
api_key = os.environ["API_KEY"]


# try:
#     redis_host = os.environ[
#         "REDIS_HOST"
#     ]  # 54.191.128.221 in docker-compose env vars or app run env vars
# except KeyError:
#     redis_host = "localhost"
#     logger.error("REDIS_HOST not set")
try:
    opensearch_host = os.environ["OPENSEARCH_HOST"]
except KeyError:
    logger.error("OPENSEARCH_HOST not set")
    opensearch_host = "nlp.nobsmed-api.com"
try:
    logfire_send_to_logfire = os.environ["LOGFIRE_SEND_TO_LOGFIRE"]
except KeyError:
    logfire_send_to_logfire = "true"
    logger.error("LOGFIRE_SEND_TO_LOGFIRE not set")


try:
    web_app_env = os.environ["WEB_APP_ENV"]
except KeyError:
    logger.error("WEB_APP_ENV not set")
    web_app_env = "local"
try:
    logfire_env = os.environ["LOGFIRE_ENVIRONMENT"]
except KeyError:
    logger.error("LOGFIRE_ENVIRONMENT not set")
    logfire_env = "local"

# console.print(f"redis_host: {redis_host}", style="info")
console.print(f"opensearch_host: {opensearch_host}", style="info")
console.print(f"logfire_send_to_logfire: {logfire_send_to_logfire}", style="info")
console.print(f"web_app_env: {web_app_env}", style="info")
console.print(f"logfire_env: {logfire_env}", style="info")
console.print("THIS IS NEW ************************ FIXED LOGFIRE BUG", style="info")

# try:
#     redis_client = redis.Redis(
#         health_check_interval=10,
#         host=redis_host,
#         port=6379,
#         password="Boris@nobsmed.com-123",
#         # decode_responses=True,
#     )
#     memory_info = redis_client.info("memory")
#     print(f"Reddit memory used: {memory_info['used_memory_human']}")
#     print("Redis ping", redis_client.ping())
# except Exception as e:
#     if web_app_env == "local":
#         logger.error(f"Redis connection error: {e}")
#         print(f"Redis connection error: {e}")
#     else:
#         raise ValueError(f"Redis connection error: {e}")

if opensearch_host == "nlp.nobsmed-api.com":
    opensearch_client = OpenSearch(
        hosts=[{"host": "nlp.nobsmed-api.com", "port": 9200}],
        http_auth=("admin", "Boris@nobsmed.com-123"),
        use_ssl=True,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
        timeout=30,  # Increase timeout to 30 seconds
        retry_on_timeout=True,
        max_retries=3,
    )

    logger.info("Using cloud opensearch")

elif opensearch_host == "localhost":
    opensearch_client = OpenSearch(
        hosts=[{"host": "localhost", "port": 9200}],
    )
    logger.info("Using local opensearch")
elif opensearch_host == "opensearch":
    opensearch_client = OpenSearch(
        hosts=[{"host": "opensearch", "port": 9200}],
    )
else:
    logger.error("OPENSEARCH_HOST not set correctly")
    raise ValueError("OPENSEARCH_HOST not set correctly")
