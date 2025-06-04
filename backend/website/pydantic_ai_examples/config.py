import logfire
from dotenv import load_dotenv
from pydantic_ai import Agent

load_dotenv()

Agent.instrument_all()
logfire.configure()
logfire.info("Loaded PydanticAI examples config.py with logfire and dotenv.")
