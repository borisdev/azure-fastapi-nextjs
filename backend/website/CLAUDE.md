# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# NOBSMED Development Guide

## Commands
- Setup env: `poetry install`
- Run server locally: `poetry run uvicorn website.main:app --reload`
- Run all tests: `poetry run pytest`
- Run single test: `poetry run pytest website/tests/test_file.py::test_function -v`
- Test options: `--doctest-modules --capture=no --disable-warnings --tb=long`
- Type check: `poetry run pyright`
- Docker build: `docker build -f website.Dockerfile -t nobsmed-website .`
- **IMPORTANT**: Always use `poetry run` prefix for Python commands in backend directory
- **TESTING**: Use existing Docker container server for testing - it auto-reloads on file changes, much faster than starting new processes

## Code Style
- Imports: Standard library → Third-party → Local modules (alphabetized within groups)
- Type hints required with Pydantic models for all functions and return values
- Use Python 3.12+ features including pattern matching and Self type
- Naming: snake_case for variables/functions, PascalCase for classes, UPPERCASE for constants
- Error handling: Use try/except with loguru for logging, clear error messages
- Cache expensive operations with joblib
- Document functions with docstrings explaining purpose, params, and return values
- Use f-strings for string formatting
- Keep functions focused and under 50 lines

## Architecture
- FastAPI web app with Jinja2 templates
- OpenSearch for data storage and search
- OpenAI integration for embeddings and completions
- Pydantic for data validation and serialization