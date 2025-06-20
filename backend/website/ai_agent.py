def main(*, question: str, biohacks: list[DynamicBiohack]):
    llm_name = "o3-mini"
    endpoint = "https://boris-m3ndov9n-eastus2.openai.azure.com"
    api_version = "2024-12-01-preview"
    api_key = azure_openai_api_key

    llm_name = "gpt-4o"
    endpoint = "https://west-us-4000-quota-gpt-4o-mini.openai.azure.com/openai/deployments/gpt-4o/"
    api_version = "2024-11-20"
    api_key = west_api_key

    # "gpt-4o-mini": "https://west-us-4000-quota-gpt-4o-mini.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-08-01-preview",
    llm_name = "gpt-4o-mini"
    endpoint = "https://west-us-4000-quota-gpt-4o-mini.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-08-01-preview"
    api_version = "2024-08-01-preview"

    max_retries = 0
    max_tokens = 200
    tasks = []
    from openai import AsyncAzureOpenAI
    from pydantic_ai import Agent, RunContext
    from pydantic_ai.models.openai import OpenAIModel
    from pydantic_ai.providers.openai import OpenAIProvider

    client = AsyncAzureOpenAI(
        max_retries=0,
        api_version=api_version,
        azure_endpoint=endpoint,
        azure_deployment=llm_name,
        api_key=api_key,
    )
    logfire.instrument_openai(client)
    model = OpenAIModel(
        "gpt-4o",
        provider=OpenAIProvider(openai_client=client),
    )
    from dataclasses import dataclass

    @dataclass
    class RuntimeDependecies:
        biohack: DynamicBiohack

    system_prompt = """
        The health problem is: {question}
        What are the top actions and impacts of the biohack?
    """.strip()

    class ActionImpactResponse(BaseModel):
        impacts: list[str] = Field(
            title="Action impacts",
            description=f"""
                What are coolest impacts of the biohack that is being described?
                Don't be flowery or verbose, just quickly get to the point using words or short phrases.
                Don't repeat yourself.
                """,
        )

    agent = Agent(
        model,
        deps_type=RuntimeDependecies,
        result_type=ActionImpactResponse,
        system_prompt=system_prompt,
    )

    @agent.system_prompt
    async def add_biohack(ctx: RunContext[RuntimeDependecies]) -> str:
        # invoked to update the system prompt based on run time state (dependencies)
        return f"The diet intervention labels are {ctx.deps.biohack!r}"

    for biohack in biohacks:
        result = agent.run_sync(question, deps=RuntimeDependecies(biohack=biohack))
        print("========================")
        print("Biohack:", biohack.biohack_topic)
        print(result.data)
