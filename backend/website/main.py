import asyncio
from pathlib import Path
from typing import Any

import logfire
import uvicorn
from fastapi import BackgroundTasks, FastAPI, Request, Response, status
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from jinja2_fragments.fastapi import Jinja2Blocks
from logfire.propagate import attach_context, get_context
from pydantic import BaseModel
from rich import print
from rich.traceback import install
from website.models import AISummary, DynamicBiohackingTaxonomy, Experience
from website.search import (make_taxonomy, run_search_and_enrich,
                            run_search_query)
from website.settings import azure_search_client, web_app_env

install()


class MiniTopic(BaseModel):
    slug: str
    title: str


app = FastAPI()

try:
    logfire.configure(distributed_tracing=True)
    logfire.instrument_fastapi(
        app,
        excluded_urls=[
            "/health",
            "/static",
            "/robots.txt",
            "/poll_ai_summary",
            "/poll_ai_search",
        ],
        capture_headers=True,
    )
except Exception as e:
    from loguru import logger

    logger.error(f"Error configuring logfire: {e}")
    raise e

cache: dict[str, Any] = {}
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)


static_directory = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_directory)), name="static")
# app.mount(
#     "/images",
#     StaticFiles(directory=str(static_directory / "images")),
#     name="images",
# )
templates_directory = Path(__file__).parent / "templates"
templates = Jinja2Blocks(directory=str(templates_directory))
# <link rel="icon" href="/static/no-bs-logo-144.png" type="image/png" />
# favicon_path = os.path.join("images", "favicon.ico")
favicon_path = str(static_directory / "favicon.ico")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)


@app.get("/health", status_code=status.HTTP_200_OK, response_class=PlainTextResponse)
def health_check():
    """
    Endpoint for health check, returns HTTP 200 status code.
    """
    return "OK"


@app.get("/")
def home_page(request: Request):
    return templates.TemplateResponse(
        name="index.html",
        context={
            "request": request,
        },
    )


# subject_slug examples: berberine, ashwagandha, pregnancy, sleep, etc
@app.get(
    "/faqs/{subject_slug}",
    response_class=HTMLResponse,
)
def topic(request: Request, subject_slug: str):
    print(f"subject_slug: {subject_slug}")
    return templates.TemplateResponse(
        name="index.html",
        context={
            "request": request,
        },
    )


@app.middleware("http")
async def subdomain_middleware(request: Request, call_next):
    request.state.web_app_env = web_app_env
    host = request.headers.get("host")
    if host:
        subdomain = host.split(".")[0]
        request.state.subdomain = subdomain
    response = await call_next(request)
    return response


@app.get("/robots.txt", response_class=PlainTextResponse)
def robots(request: Request):
    if request.state.subdomain == "test":
        data = """
            User-agent: *
            Disallow: /
        """
    else:
        # data = """User-agent: *\nAllow: /"""
        # User-agent: SemrushBot Disallow: /
        data = """
            User-agent: SEMrushBot
            Disallow: /

            User-agent: *
            Disallow: /
            Allow: /faq
            Allow: /about
        """

        return data


@app.get("/about")
def about(request: Request):
    return templates.TemplateResponse(
        name="about.html",
        context={
            "request": request,
        },
    )


@app.get("/faq")
def faq(request: Request):
    return templates.TemplateResponse(
        name="faqs.html",
        context={
            "request": request,
        },
    )


@app.get("/tech")
def tech(request: Request):
    return templates.TemplateResponse(
        name="tech.html",
        context={
            "request": request,
        },
    )


async def ai_search_task(
    *,
    question: str,
    experiences: list[Experience],
    batch_size: int,
    llm_name: str,
    max_tokens: int,
    max_retries: int,
    timeout: int,
):
    question = question.strip()
    question = question.replace("?", "")
    cache_result = cache.get("taxonomy" + question)
    if cache_result is not None and isinstance(cache_result, DynamicBiohackingTaxonomy):
        logfire.info(f"Found valid taxonomy in cache, skipping ai search task")
        return
    # taxonomy = await relevance_chain(
    taxonomy = await enrich_search_results_chain(
        experiences=experiences,
        question=question,
        batch_size=batch_size,
        llm_name=llm_name,
        max_tokens=max_tokens,
        max_retries=max_retries,
        timeout=timeout,
    )
    cache["taxonomy" + question] = taxonomy
    logfire.info(f"AI Search saved to cache with key: `taxonomy{question}`")
    return


async def ai_summary_task(
    *,
    question: str,
):
    question = question.strip().replace("?", "")
    ai_summary = cache.get("summary" + question)
    if ai_summary is not None and isinstance(ai_summary, AISummary):
        if len(ai_summary.curious) > 0:
            logfire.info(f"Found valid ai summary in cache, skipping summary task")
            return
        else:
            logfire.info(
                "No curious items found in cache, starting ai summary task again"
            )
    taxonomy = cache["taxonomy" + question]
    if taxonomy is None or not isinstance(taxonomy, DynamicBiohackingTaxonomy):
        logfire.error("No valid taxonomy found in cache, skipping ai summary task")
        return
    try:
        ai_summary = await new_ai_summary(  # summary = await summary_chain(
            question=question,
            taxonomy=taxonomy,
        )
    except Exception as e:
        logfire.error(f"Error starting ai summary task: {e}")
        cache["summary" + question] = "Error starting ai summary task"
        return
    if isinstance(ai_summary, AISummary) and len(ai_summary.curious) > 0:
        cache["summary" + question] = ai_summary
        logfire.info(f"AI Summary saved to cache with key: `summary{question}`")
    elif isinstance(ai_summary, AISummary) and len(ai_summary.curious) == 0:
        logfire.error("AI summary task returned no curious items")
        cache["summary" + question] = "AI summary task returned no curious items"
    else:
        logfire.error("AI summary task returned an invalid result")
        cache["summary" + question] = "AI summary task returned an invalid result"
    return


@app.get(
    "/search",
    response_class=HTMLResponse,
)
async def search(
    request: Request,
    question: str,
    background_tasks: BackgroundTasks,
):
    # Part 0 check cache
    question = question.strip().replace("?", "")
    cache_result = cache.get("taxonomy" + question)
    if cache_result is not None and isinstance(cache_result, DynamicBiohackingTaxonomy):
        logfire.info(f"Found valid taxonomy in cache, skipping ai search task")
        return templates.TemplateResponse(
            name="search.html",
            context={
                "question": question,
                "request": request,
                "relevance_polling": "finished",
                "summary_polling": "on",
                "biohack_types": cache_result.biohack_types,
                "count_experiences": cache_result.count_experiences,
                "count_reddits": cache_result.count_reddits,
                "count_studies": cache_result.count_studies,
            },
        )

    # Part 1 of 3: Search candidate biohacks - recall
    limit = 100
    taxonomy = await run_search_and_enrich(
        question=question,
        client=azure_search_client,
        limit=limit,
        batch_size=300,
        llm_name="gpt-4o",
        max_tokens=100,
        max_retries=0,
        timeout=2,
    )
    # experiences = run_search_query(
    #     question=question, client=azure_search_client, limit=limit
    # )
    # count_experiences = len(experiences)
    count_biohacks = len(taxonomy.biohack_types)
    # if count_experiences > 1:
    if count_biohacks > 1:
        # taxonomy = make_taxonomy(experiences=experiences)
        biohack_types = taxonomy.biohack_types
        count_reddits = taxonomy.count_reddits
        count_studies = taxonomy.count_studies
        cache["taxonomy" + question] = taxonomy
        logfire.info(f"AI Search saved to cache with key: `taxonomy{question}`")
        relevance_polling = "finished"

        # # Perform the search immediately rather than in a background task
        # try:
        #     taxonomy = await enrich_search_results_chain(
        #         experiences=experiences,
        #         question=question,
        #         batch_size=limit + 1,
        #         llm_name="gpt-4o-mini",
        #         max_tokens=100,
        #         max_retries=0,
        #         timeout=4,
        #     )
        #     cache["taxonomy" + question] = taxonomy
        #     logfire.info(f"AI Search saved to cache with key: `taxonomy{question}`")
        #     relevance_polling = "finished"
        #     biohack_types = taxonomy.biohack_types
        #     count_reddits = taxonomy.count_reddits
        #     count_studies = taxonomy.count_studies
        # except Exception as e:
        #     logfire.error(f"Error in synchronous search: {e}")
        #     # Fall back to polling approach
        #     background_tasks.add_task(
        #         ai_search_task,
        #         question=question,
        #         experiences=experiences,
        #         batch_size=limit + 1,
        #         llm_name="gpt-4o-mini",
        #         max_tokens=100,
        #         max_retries=0,
        #         timeout=4,
        #     )
        #     logfire.info(
        #         "Started ai_relevance background task, telling FE to start polling"
        #     )
        #     relevance_polling = "on"
        #     biohack_types = []
        #     count_reddits = 0
        #     count_studies = 0
    else:
        relevance_polling = "not_started"
        logfire.warning("No experiences found, so no AI task started")
        count_reddits = 0
        count_studies = 0
        biohack_types = []

    # {"traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"}
    trace_headers = {}
    trace_headers.update(get_context())
    context = {
        "question": question,
        "request": request,
        "relevance_polling": relevance_polling,
        "summary_polling": "off",
        "count_experiences": taxonomy.count_experiences,
        "traceparent": trace_headers["traceparent"],
        "first_poll": "true",
    }

    # Add the biohack data if available
    if relevance_polling == "finished":
        context.update(
            {
                "biohack_types": biohack_types,
                "count_reddits": count_reddits,
                "count_studies": count_studies,
            }
        )
    if "HX-Request" in request.headers:
        # ajax request so just need a partial page update
        # NOT TOTAL REFRESH
        # if accept json header return json
        if "accept" in request.headers:
            # for future e2e testing
            if "application/json" in request.headers["accept"]:
                return Response(content=context, media_type="application/json")
        response = templates.TemplateResponse(
            name="search.html",
            context=context,
            block_name="ai_search_results",
        )
        return response
    else:
        # a shared link might trigger this
        # fresh page load so return the full page
        if "accept" in request.headers:
            # for future e2e testing
            if "application/json" in request.headers["accept"]:
                return Response(content=context, media_type="application/json")
        return templates.TemplateResponse(
            name="search.html",
            context=context,
        )


# polling hits this endpoint
@app.get(
    "/poll_ai_search/{question}",
    response_class=HTMLResponse,
)
async def ai_search(request: Request, question: str, background_tasks: BackgroundTasks):
    with attach_context(request.headers):
        first_poll = request.headers.get("first_poll")
        if first_poll == "true":
            logfire.info(f"started polling `/poll_ai_search/{question}")
        trace_headers = {}
        trace_headers.update(get_context())
        # ctx = get_context()
        # with attach_context(ctx):
        #     logfire.info("poll_ai_search")  # This log will be a child of the parent span.
        # Handle empty question case
        if not question or question.strip() == "":
            error_message = (
                "Empty `question param` in req to ai_search endpoint from polling"
            )
            logfire.error(error_message)
            return templates.TemplateResponse(
                name="search.html",
                context={
                    "request": request,
                    "biohack_types": [],
                    "relevance_polling": "not_started",
                    "summary_polling": "off",
                    "error": error_message,
                    "first_poll": "false",
                },
                block_name="ai_search_results",
            )

        question = question.strip()
        question = question.replace("?", "")
        cache_result = cache.get("taxonomy" + question)
        if cache_result is None:
            return templates.TemplateResponse(
                name="search.html",
                context={
                    "question": question,
                    "biohack_types": [],
                    "request": request,
                    "polling": 1,
                    "relevance_polling": "on",
                    "summary_polling": "off",
                    "first_poll": "false",
                    "traceparent": trace_headers["traceparent"],
                },
                block_name="ai_search_results",
            )
        elif isinstance(cache_result, DynamicBiohackingTaxonomy):
            # propagation means making children
            # next polling should be a child of this polling
            trace_headers = {}
            trace_headers.update(get_context())
            logfire.info(f"Found valid taxonomy in cache using `poll_ai_search`")
            return templates.TemplateResponse(
                name="search.html",
                context={
                    "question": question,
                    "count_experiences": cache_result.count_experiences,
                    "count_reddits": cache_result.count_reddits,
                    "count_studies": cache_result.count_studies,
                    "biohack_types": cache_result.biohack_types,
                    "error": None,
                    "request": request,
                    "relevance_polling": "finished",
                    "summary_polling": "off",
                    "traceparent": trace_headers["traceparent"],
                    "first_poll": "false",
                },
                block_name="ai_search_results",
            )
            # try:
            #     background_tasks.add_task(
            #         ai_summary_task,
            #         question=question,
            #     )
            #     logfire.info(f"Starting ai summary task for question: {question}")
            #     return templates.TemplateResponse(
            #         name="search.html",
            #         context={
            #             "question": question,
            #             "count_experiences": cache_result.count_experiences,
            #             "count_reddits": cache_result.count_reddits,
            #             "count_studies": cache_result.count_studies,
            #             "biohack_types": cache_result.biohack_types,
            #             "error": None,
            #             "request": request,
            #             "relevance_polling": "finished",
            #             "summary_polling": "on",
            #             "traceparent": trace_headers["traceparent"],
            #             "first_poll": "false",
            #         },
            #         block_name="ai_search_results",
            #     )
            #
            # except Exception as e:
            #     logfire.error(f"Error starting ai search task: {e}")
            #     return templates.TemplateResponse(
            #         name="search.html",
            #         context={
            #             "question": question,
            #             "count_experiences": cache_result.count_experiences,
            #             "count_reddits": cache_result.count_reddits,
            #             "count_studies": cache_result.count_studies,
            #             "biohack_types": None,
            #             "error": "Invalid AI search result in cache -- retry",
            #             "request": request,
            #             "relevance_polling": "finished",
            #             "summary_polling": "off",
            #             "first_poll": "false",
            #         },
            #         block_name="ai_search_results",
            #     )
            #


# FE polling for AI summary hits this endpoint
@app.get(
    "/poll_ai_summary/{question}",
    response_class=HTMLResponse,
)
async def ai_summary(request: Request, question: str):
    # website  | traceparent: 00-0195afeea9866c5788d7aa51c76ffeec-4c74c8f6fa174f85-01
    with attach_context(request.headers):
        logfire.info(f"/poll_ai_summary/{question}")
        trace_headers = {}
        trace_headers.update(get_context())
        if not question or question.strip() == "":
            error_message = (
                "Empty `question param` in req to ai_summary endpoint from polling"
            )
            logfire.error(error_message)
            return templates.TemplateResponse(
                name="search.html",
                context={
                    "request": request,
                    "relevance_polling": "finished",
                    "summary_polling": "off",
                    "ai_summary_error_message": error_message,
                },
                block_name="ai_summary",
            )

        question = question.strip()
        question = question.replace("?", "")
        cache_result = cache.get("summary" + question)
        # {"traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"}

        if cache_result is None:
            logfire.info("No valid ai summary in cache, starting ai summary task")
            # tell client to continue polling for summary
            return templates.TemplateResponse(
                name="search.html",
                context={
                    "request": request,
                    "relevance_polling": "finished",
                    "question": question,  # Include the question parameter for polling
                    "summary_polling": "on",
                    "traceparent": trace_headers.get("traceparent"),
                },
                block_name="ai_summary",
            )
        elif isinstance(cache_result, AISummary):
            logfire.info(f"Found valid ai summary in cache using `poll_ai_summary`")

            for field_name in AISummary.model_fields.keys():
                field_value = getattr(cache_result, field_name)
                if not bool(field_value):
                    logfire.warning(f"Field {field_name} is empty: {field_value}")
                else:
                    logfire.info(f"Field {field_name} has {len(field_value)} items")

            return templates.TemplateResponse(
                name="search.html",
                context={
                    "request": request,
                    "mechanisms": cache_result.mechanisms,
                    "contra_biohacks": cache_result.skeptical,
                    "cool_biohacks": cache_result.curious,
                    "balance_biohacks": cache_result.balance,
                    "relevance_polling": "finished",
                    "summary_polling": "finished",
                },
                block_name="ai_summary",  # Use the ai_summary block for targeted updates
            )
        else:
            error_message = "Invalid AI summary result in cache -- retry"
            logfire.error(error_message)
            cache.pop("summary" + question, None)
            return templates.TemplateResponse(
                name="search.html",
                context={
                    "request": request,
                    "ai_summary_error_message": error_message,
                    "relevance_polling": "finished",
                    "summary_polling": "finished_due_to_error",
                },
                block_name="ai_summary",
            )

    # search = (
    #     QuestionAnswerDoc.search()
    #     .filter("term", **{"question.raw": question})
    #     .filter("term", llm_chain=llm_chain)
    # )
    # response = search.execute()
    # # print(response.hits)
    # doc = response.hits[0] if len(response.hits) > 0 else None
    #     question_answer = doc.to_pydantic()


if __name__ == "__main__":

    logfire.info("Starting uvicorn webserver...")
    if web_app_env == "LAPTOP" or web_app_env == "LOCAL":
        try:
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=80,
                log_level="debug",
                proxy_headers=True,
                reload=True,
                timeout_keep_alive=360,
                workers=1,
            )
        except Exception as e:
            logfire.error(f"Error starting uvicorn: {e}")
            raise e
    else:
        try:
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=80,
                log_level="info",
                proxy_headers=True,
                timeout_keep_alive=360,
                workers=10,
            )
        except Exception as e:
            logfire.error(f"Error starting uvicorn: {e}")
            raise e
