# Cheatsheet: Azure + FastAPI + NextJS

## This repo was hacked from looking at these repos

-   From FastAPI maker: [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template)
-   From NextJS makers: [Vercel Labs's ai-sdk-preview-python-streaming](https://github.com/vercel-labs/ai-sdk-preview-python-streaming)
-   [From Vinta Software (uses `uv` for python package management)](https://github.com/vintasoftware/nextjs-fastapi-template)

## Current Stack

-   Poetry
-   Docker multi-stage builds
-   Backend: FastAPI serving HTMX and Typescript
-   OpenSearch DB
-   Azure Registry
-   Azure Container app

## Upcoming stack changes

-   `uv` for rapid python experiments - each deployment branch is composed of diff combos of packages sourced from other branches
-   git submodules - for flip-flopping between diff frontends w/ each deployment branch experiment
-   Backend: [Fast API - LangGraph Platform](https://www.langchain.com/langgraph-platform))
-   Frontend: Next.js, React components, Tailwind CSS, TypeScript

---

## Design

### Facts to design around:

-   I am a one person developer team.
-   My intention is to experiment with cutting-edge python language AI tools.
-   I got an MS Azure start-up grant.

### Project specific design principles:

-   avoid minimal speed gains for a 1 person team that make debugging harder since I can't call Ghost Busters
-   over-engineering for learning is fine since this is a personal project. More specifically, make it easy to run mix-and-match experiments since that is the key to increasing the quality of the user content by trying out the new AI tools.

### Scope reduction:

-   No Github actions
-   No Terraform (stick with Azure CLI)

---

## Deployment

Steps

1. Build the images locally and push the images to your Azure cloud registry
2. Deploy cloud container that pulls the new image from the Azure cloud registry

### Docker Images

> [!NOTE]  
> `nobs` in this doc denotes my personal project's prefixing.

> [!IMPORTANT]  
> A Mac M1 image will not work in the cloud. Use `docker buildx build --platform linux/amd64 -t nobs_backend_amd64 .`

```bash
cd backend
docker build --tag nobs_backend --file docker/Dockerfile .
docker buildx build --platform linux/amd64 -t nobs_backend_amd64 .
cd ../frontend
docker build --tag nobs_frontend --file docker/Dockerfile .
docker tag nobs_backend nobsregistry.azurecr.io/nobs_backend:v1
docker tag nobs_backend_amd64 nobsregistry.azurecr.io/nobs_backend:latest
docker images
# REPOSITORY                             TAG       IMAGE ID       CREATED        SIZE
# nobsregistry.azurecr.io/nobs_backend      v1        585a4696bedd   44 hours ago   197MB
# nobs_backend                           latest    585a4696bedd   43 hours ago   197MB
# nobs_frontend                          latest    585a4696bedd   43 hours ago   197MB

az login
az acr login --name nobsregistry
docker push nobsregistry.azurecr.io/nobs_backend:v1
az acr repository list --name nobsregistry
# [
#   "nobs_backend",
# ]
az acr repository show-tags --name nobsregistry --repository nobs_backend
# [
#   "aws_prod"
# ]
```

### Azure Container App Deploy

Source: [Azure Container Registry for launch in Azure Container Apps.](https://learn.microsoft.com/en-us/azure/container-instances/container-instances-tutorial-prepare-acr#create-azure-container-registry)

comment and uncomment the lines in azure-container-app.sh

Assumptions:

-   Azure: Azure CLI installed and your logged into it
-   you have created a resource group in Azure (e.g., for me its `nobsmed`)

```bash
./azure-container-app.sh
```
