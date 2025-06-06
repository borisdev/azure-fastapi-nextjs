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

I prefix names with `nobs` because my company is called Nobsmed.

```console
# create the registry

az acr create --resource-group nobsmed --name nobsregistry --sku Basic

# sanity check

az acr show --name nobsregistry --query loginServer --output table
Result
--------------------------
nobsmedregistry.azurecr.io
```

---

## Ongoing launch steps

```bash
# Build backend and frontend docker images:
cd backend
docker build --tag nobs_backend --file docker/Dockerfile .
cd ../frontend
docker build --tag nobs_frontend --file docker/Dockerfile .

# Tag the images for Azure Container Registry

docker tag nobs_backend nobsregistry.azurecr.io/nobs_backend:v1

# Sanity check

docker images
REPOSITORY                             TAG       IMAGE ID       CREATED        SIZE
nobsregistry.azurecr.io/nobs_backend      v1        585a4696bedd   44 hours ago   197MB
nobs_backend                           latest    585a4696bedd   43 hours ago   197MB
nobs_frontend                          latest    585a4696bedd   43 hours ago   197MB

# Login to Azure Container Registry

az acr login --name nobsregistry

# Push image to Azure Container Registry

docker push nobsregistry.azurecr.io/nobs_backend:v1

**# Sanity check .....you see the output below**

The push refers to repository [nobsregistry.azurecr.io/nobs_backend]
5f70bf18a086: Preparing
7d577052c02c: Preparing
ac42807ce093: Preparing
d54c60f73cbb: Preparing
d559dc6e6c29: Preparing
8f697a207321: Waiting


# Sanity check that the image is in the registry

az acr repository list --name nobsregistry
[
"nobs_backend",
]
```

```console
source azure_env
source azure_deploy

az containerapp create \
  --name $API_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT \
  --image $ACR_NAME.azurecr.io/$API_NAME \
  --target-port 8080 \
  --ingress external \
  --registry-server $ACR_NAME.azurecr.io \
  --user-assigned "$IDENTITY_ID" \
  --registry-identity "$IDENTITY_ID" \
  --query properties.configuration.ingress.fqdn

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
