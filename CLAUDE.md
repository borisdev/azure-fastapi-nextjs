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

### ETL Operations (Azure Search Indexing)
```bash
# Navigate to ETL directory
cd etl

# Install dependencies
poetry install

# Upload experiences to Azure Search using CLI
poetry run python upload_to_azure_search.py --index my-index --all  # Upload everything
poetry run python upload_to_azure_search.py --index my-index --reddit --reddit-limit 100  # Reddit only
poetry run python upload_to_azure_search.py --index my-index --studies  # Studies only
poetry run python upload_to_azure_search.py --index my-index --all --dry-run  # Preview upload
poetry run python upload_to_azure_search.py --index my-index --studies --studies-dir /custom/path  # Custom directory
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

#### Current Version: v9.2

#### Full Deployment Process
```bash
# 1. Navigate to backend directory
cd backend

# 2. Login to Azure Container Registry
az acr login --name nobsregistry

# 3. Build new Docker image (increment version number)
docker buildx build --platform linux/amd64 -t nobsregistry.azurecr.io/nobs_backend_amd64:v9.3 .

# 4. Push image to registry
docker push nobsregistry.azurecr.io/nobs_backend_amd64:v9.3

# 5. Update container app to use new image
az containerapp update --name nobswebsite --resource-group nobsmed --image nobsregistry.azurecr.io/nobs_backend_amd64:v9.3

# 6. Verify deployment
az containerapp show --name nobswebsite --resource-group nobsmed --query "properties.template.containers[0].image" --output tsv

# 7. Run integration tests
cd .. && poetry run python test-deployment.py
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
- v9.1: Fixed robots.txt formatting issues - removed leading whitespace and added explicit SEMrushBot disallow to resolve Google Search Console "Indexed, though blocked by robots.txt" errors
- v9.0: gtag analytics and Docker build improvements - added Google Analytics tracking, fixed Docker Poetry install with --no-root flag for better layer caching
- v8.9: Quick bug fix on links for 2 books - hotfix deployment addressing broken book references
- v8.8: Refactored Amazon Products with unified AmazonProduct model - consolidated data structures, split jennas_amazon_products.py into focused modules (questions.py, amazon_products.py), improved template reliability and maintainability
- v8.7: Fixed all broken Amazon product links - consolidated to single amazon_url field, updated 650+ products with working URLs and referral tags
- v8.6: Dynamic table system for Amazon Products - automatically hides N/A columns, cleaned up price ranges, improved page layout
- v8.5: Added Amazon Products page with pregnancy-focused product listings and affiliate links
- v8.4: Enhanced button UX with type-specific labeling - separate buttons for personal experiences, scientific studies, and mixed content
- v8.3: Infrastructure improvements - reorganized scripts, added integration testing, updated docs
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

### ETL Data Processing
- **CLI Tool**: `etl/upload_to_azure_search.py` provides simplified interface for Azure Search uploads
- **Data Sources**: 
  - Reddit experiences from TopicExperiences (Biohacking, Sleep, Pregnancy topics)
  - Study experiences from JSON files in configured directory
- **Quality Filtering**: Only experiences with action_score >= 2 and outcomes_score >= 2 are uploaded
- **Embeddings**: Automatic generation for health_disorder field using Azure OpenAI
- **Batch Processing**: Uses 50-document batches for efficient upload
- **Result Tracking**: 2,421 studies successfully uploaded from 44,567 files in last test run

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
- **Integration Testing**: `test-deployment.py` verifies production deployments across all domains
- Run tests with: `poetry run python test-deployment.py`

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