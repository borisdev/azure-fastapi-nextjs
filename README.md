# Cheatsheet: Azure + FastAPI + NextJS

> [!CAUTION]
> NextJS is not hooked up yet, FastAPI backend is serving the HTML pages using HTMX, for now.

### Assumptions

-   Docker setup
-   Poetry setup
-   Azure CLI SDK setup, with a resource group created

## Stack

### Now

-   Poetry
-   Docker multi-stage builds
-   Backend: FastAPI serving fronted: HTMX and Typescript
-   Azure Cloud: Search, Container Registry, and Container Apps

## In progress

-   `uv` allows each backend deployment to combine python packages sourced from other branches
-   `git submodules` - allows A/B testing deployments by simply changing frontend commits and keeping backend same
-   Backend: [Fast API - LangGraph Platform](https://www.langchain.com/langgraph-platform)
-   Frontend: Next.js, React components, Tailwind CSS, TypeScript

---

## Design

-   Scale for a one person developer team.
-   Use the MS Azure start-up grant.
-   balance automation's speed against automation's risk of harder debugging
-   Delay Github actions
-   Delay Terraform

---

## Build + Deploy

### Overview

-   We deploy the app using Azure Container Apps service, which depends on ...
-   Azure Container service pulling a new image from the Azure cloud registry, which depends on...
-   Azure cloud registry being hydrated with the latest images, which depends on...
-   Locally we build the images first, and then push the images to the registry

### Build Deployable Docker Image

Keep track of the version in the `.env` file.

```bash
API_VERSION="v5"
```

> [!NOTE] > `nobs` in this doc denotes my personal project's prefixing.

> [!IMPORTANT]
> A Mac M1 image will not work in the cloud. Use `docker buildx build --platform linux/amd64 -t nobs_backend_amd64 .`

```bash
cd backend
docker buildx build --platform linux/amd64 -t nobsregistry.azurecr.io/nobs_backend_amd64:v7 .
az login
az acr login --name nobsregistry
docker push nobsregistry.azurecr.io/nobs_backend_amd64:v7
az acr repository list --name nobsregistry
[
  "nobs_backend",
  "nobs_backend_amd64"
]
az acr repository show-tags --name nobsregistry --repository nobs_backend_amd64
[
  "aws_prod",
  "v6"
]
```

### References

-   [Azure Container Registry for launch in Azure Container Apps.](https://learn.microsoft.com/en-us/azure/container-instances/container-instances-tutorial-prepare-acr#create-azure-container-registry)
-   From FastAPI maker: [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template)
-   From NextJS makers: [Vercel Labs's ai-sdk-preview-python-streaming](https://github.com/vercel-labs/ai-sdk-preview-python-streaming)
-   [From Vinta Software (uses `uv` for python package management)](https://github.com/vintasoftware/nextjs-fastapi-template)
