# Cheatsheet: Azure + FastAPI + NextJS

> [!CAUTION]
> Don't use this repo. It is completely under construction.

## Stack

### Now

-   Poetry
-   Docker multi-stage builds
-   Backend: FastAPI serving fronted: HTMX and Typescript
-   Azure Cloud: Search, Container Registry, and Container Apps

## In progress

-   `uv` allows each backend deployment to combine python packages sourced from other branches
-   `git submodules` - allows A/B testing deployments by simply changing frontend commits and keeping backend same
-   Backend: [Fast API - LangGraph Platform](https://www.langchain.com/langgraph-platform))
-   Frontend: Next.js, React components, Tailwind CSS, TypeScript

---

## Design considerations

### Constraints

-   Scale for a one person developer team.
-   Use the MS Azure start-up grant.

### Balance

-   balance automation's speed against automation's risk of harder debugging

### Scope reduction

-   Delay Github actions
-   Delay Terraform

---

## Build + Deploy

### Overview: How local docker builds are deployed to Azure Cloud

-   We deploy the app using Azure Container Apps service, which depends on ...
-   Azure Container service pulling a new image from the Azure cloud registry, which depends on...
-   Azure cloud registry being hydrated with the latest images, which depends on...
-   Locally we build the images first, and then push the images to the registry

### Build Docker Images

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

### Azure Deploy

Assumptions:

-   Azure: Azure CLI installed and your logged into it
-   you have created a resource group in Azure (e.g., for me its `nobsmed`)

Run scripts in `azure_deploy` folder to create and hydrate the Azure resources:

```bash
ls azure_deploy
 create_api_app_container_service.sh
 create_docker_image_registry.sh
 create_search_service.sh
 search_add_index.py
 search_add_jsons.py
```

### References

-   [Azure Container Registry for launch in Azure Container Apps.](https://learn.microsoft.com/en-us/azure/container-instances/container-instances-tutorial-prepare-acr#create-azure-container-registry)
-   From FastAPI maker: [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template)
-   From NextJS makers: [Vercel Labs's ai-sdk-preview-python-streaming](https://github.com/vercel-labs/ai-sdk-preview-python-streaming)
-   [From Vinta Software (uses `uv` for python package management)](https://github.com/vintasoftware/nextjs-fastapi-template)
