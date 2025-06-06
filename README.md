# Deploy cheatsheet

Run my python AI stack (Nobsmed.com) on Azure Container Apps

## Base Templates

-   https://github.com/fastapi/full-stack-fastapi-template

## Current Stack

-   Poetry
-   Docker multi-stage builds
-   Backend: FastAPI serving HTMX and Typescript
-   OpenSearch DB
-   Azure Registry
-   Azure Container app

## Upcoming stack changes

-   `uv`, one repo holds a deployment composed of packages versioned by different branches
-   deploy with [az containerapp compose](https://learn.microsoft.com/en-us/cli/azure/containerapp/compose?view=azure-cli-latest)
-   Backend: [Fast API - LangGraph Platform](https://www.langchain.com/langgraph-platform))
-   Frontend: Next.js, React components, Tailwind CSS, TypeScript
-   Azure Search DB
-   Azure Redis

---

## Limit scope because of 1 person team

Transparency over automation

-   No Github actions
-   No Terraform - Azure CLI

---

## Steps to run my stack

1. Build the images locally
2. Push the images to cloud registry
3. Deploy cloud container based on new image in registry

Source: [Azure Container Registry for launch in Azure Container Apps.](https://learn.microsoft.com/en-us/azure/container-instances/container-instances-tutorial-prepare-acr#create-azure-container-registry)

Assumptions:

-   Azure: Azure CLI installed and your logged into it
-   you have created a resource group in Azure (e.g., for me its `nobsmed`)

## Pre-requisites steps

`nobs` denotes my personal project's prefixing.

```console
az acr create --resource-group nobsmed --name nobsregistry --sku Basic
az acr show --name nobsregistry --query loginServer --output table
# Result
# --------------------------
# nobsmedregistry.azurecr.io
```

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
az container delete --name sampleapp --resource-group nobsmed
```

Table here

## How is the different from the best full stack template, [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template)?

-   Extended for Azure multi-service container app deploys
-   Pruned down to meet my simpler requirements
-   Replacing `nginx` frontend server with `NextJS` frontend server
-   Multi-layer docker build from 3x smaller image

## How different from other FASTAPI-NEXTJS template?

-   `uv` not `poetry` for python dependency management
