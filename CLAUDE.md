# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack Azure-deployed application for biohacking search and AI insights, combining FastAPI backend with Next.js frontend (though currently serving HTMX templates from FastAPI).

## Commands

### Backend Development (Poetry + FastAPI)
```bash
cd backend
poetry install
poetry shell
uvicorn website.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development (Next.js)
```bash
cd frontend
npm install  # or pnpm install
npm run dev  # Development server with Turbopack
npm run build  # Production build
npm start  # Production server
```

### Testing & Quality
```bash
# Backend tests
cd backend
pytest  # Run all tests with configured options
pytest website/tests/test_file.py::test_function -v  # Single test
pyright  # Type checking

# Docker operations
docker compose up  # Run full stack locally
docker buildx build --platform linux/amd64 -t image:tag .  # AMD64 build for Azure
```

### Azure Deployment

#### Current Version: v8.1

#### Full Deployment Process
```bash
# 1. Navigate to backend directory
cd backend

# 2. Login to Azure Container Registry
az acr login --name nobsregistry

# 3. Build new Docker image (increment version number)
docker buildx build --platform linux/amd64 -t nobsregistry.azurecr.io/nobs_backend_amd64:v9 .

# 4. Push image to registry
docker push nobsregistry.azurecr.io/nobs_backend_amd64:v9

# 5. Update container app to use new image
az containerapp update --name nobswebsite --resource-group nobsmed --image nobsregistry.azurecr.io/nobs_backend_amd64:v9

# 6. Verify deployment
az containerapp show --name nobswebsite --resource-group nobsmed --query "properties.template.containers[0].image" --output tsv
```

#### Initial Infrastructure Setup (One-time)

For first-time Azure infrastructure setup, use these bash scripts in the root directory:

```bash
# 1. Create Azure Container Registry
./setup-registry.sh

# 2. Create Azure Search Service
./setup-search.sh

# 3. Create Container App Service
./setup-containerapp.sh
```

**Note**: These scripts should only be run once during initial setup. For ongoing deployments, use the Full Deployment Process above.

#### Quick Reference
- **Registry**: nobsregistry.azurecr.io
- **Image Name**: nobs_backend_amd64  
- **Container App**: nobswebsite
- **Resource Group**: nobsmed
- **Custom Domains**: nobsmed.com, www.nobsmed.com

#### Version History
- v8.1: Cleaner UI with search bar removal, fixed collapse button conflicts, improved UX
- v8: Added why_care field to search results, improved collapse functionality
- v7: Previous stable version

## Architecture

### Backend Structure (FastAPI)
- **Main App**: `backend/website/main.py` - FastAPI server with Jinja2 templating
- **Search Engine**: `backend/website/search.py` - Hybrid Azure Search + OpenAI embeddings
- **AI Processing**: `backend/website/chain.py` - Abstract LLM processing chains
- **Data Models**: `backend/website/models.py` - Pydantic models for biohacking experiences
- **Config**: `backend/website/settings.py` - Environment-based configuration

### Core Data Flow
1. **Search**: User query → Azure Search (BM25) + vector embeddings → relevance filtering
2. **AI Processing**: Background tasks for experience summarization using multiple LLM perspectives
3. **Real-time Updates**: HTMX/AJAX polling for asynchronous AI results
4. **Caching**: In-memory cache for search results and AI summaries

### Key Integrations
- **Azure Search**: Primary data store for biohacking experiences
- **Azure OpenAI**: Multiple regional deployments (GPT-4o, GPT-4o-mini, O3-mini)
- **Logfire**: Distributed tracing and observability
- **OpenTelemetry**: Comprehensive instrumentation

### Frontend Structure (Next.js)
- **App Router**: Next.js 15 with TypeScript and Tailwind CSS
- **Current State**: FastAPI serves HTMX templates; Next.js integration in progress
- **Components**: Dashboard UI, forms, authentication, search interfaces

## Development Practices

### Code Style (Backend)
- Python 3.12+ with full type hints and Pydantic validation
- Import order: standard library → third-party → local modules (alphabetized)
- Error handling with loguru logging and clear messages
- Functions under 50 lines, focused responsibilities
- snake_case for variables/functions, PascalCase for classes

### Frontend Template Development (Jinja2 + HTMX)
- **Unique ID Generation**: Use global counters with `{% set counter = namespace(value=0) %}` for truly unique IDs across nested loops
- **Defensive JavaScript**: Always check for element existence before DOM manipulation (`if (element) element.style...`)
- **Bootstrap Collapse**: Ensure each collapse button has unique `data-bs-target` and matching element ID
- **Mobile Touch Handling**: Use `touch-action: manipulation` and proper event handlers for mobile responsiveness
- **Console Debugging**: Add temporary logging for complex interactions during development

### Testing Configuration
- pytest with configured options: `--doctest-modules --capture=no --disable-warnings --tb=long`
- Type checking with pyright (configured in pyrightconfig.json)
- Test files in `backend/website/tests/`

### Environment Setup
- Backend uses Poetry for dependency management
- Frontend uses npm/pnpm with package.json
- Docker compose for local development
- Environment variables in `.secret` file for local dev

### Azure Cloud Architecture
- Multi-region OpenAI deployments for load balancing
- Container Registry (nobsregistry.azurecr.io) for image storage
- Container Apps for backend deployment
- Search service for data indexing and retrieval

## Important Notes

- Mac M1 users must use `--platform linux/amd64` for Azure-compatible builds
- **Infrastructure Scripts**: Azure setup scripts are located in the root directory for easy access (not in Python packages)
- Backend currently serves frontend via HTMX templates, not Next.js API routes
- AI processing runs as background tasks with polling endpoints for real-time updates
- Search combines traditional BM25 ranking with semantic vector similarity
- Multiple LLM models provide different perspectives (balanced, skeptical, curious)