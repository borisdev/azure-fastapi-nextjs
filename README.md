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

Facts to design around:

-   I am a one person developer team.
-   My intention is to experiment with cutting-edge python language AI tools.
-   I got an MS Azure start-up grant.

Project specific design principles:

-   avoid minimal speed gains for a 1 person team that make debugging harder since I can't call Ghost Busters
-   over-engineering for learning is fine since this is a personal project
-   make it easy to run mix-and-match experiments since that is the key to increasing the quality of the user content

Scope reduction:

-   No Github actions
-   No Terraform (stick with Azure CLI)

---

## Deploy steps

1. Build the images locally
2. Push the images to cloud registry
3. Deploy cloud container based on new image in registry

> [!IMPORTANT]  
> A Mac M1 image will not work in the cloud. Use `docker buildx build --platform linux/amd64 -t nobs_backend_amd64 .`

Source: [Azure Container Registry for launch in Azure Container Apps.](https://learn.microsoft.com/en-us/azure/container-instances/container-instances-tutorial-prepare-acr#create-azure-container-registry)

Assumptions:

-   Azure: Azure CLI installed and your logged into it
-   you have created a resource group in Azure (e.g., for me its `nobsmed`)

> [!NOTE]  
> `nobs` in this doc denotes my personal project's prefixing.

---

## Deploy steps

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

#### comment and uncomment the lines in azure-container-app.sh

```bash
./azure-container-app.sh
```
