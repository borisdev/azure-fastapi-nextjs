#!/bin/bash

# keep changing this.....
#docker tag nobs_backend_amd64 nobsregistry.azurecr.io/nobs_backend:latest
# docker push nobsregistry.azurecr.io/nobs_backend_amd64:v1
TAG="v1"
#TAG="latest"

# these stay the same
RESOURCE_GROUP="nobsmed"
LOCATION="westus"
CONTAINER_APP_ENVIRONMENT="prod"
CONTAINER_APP_NAME="nobswebsite"
#IMAGE_REPO="nobs_backend"
IMAGE_REPO="nobs_backend_amd64"
IMAGE_NAME="nobsregistry.azurecr.io/$IMAGE_REPO:$TAG"
ACR_NAME="nobsregistry"
IDENTITY="nobsmed-identity"
REGISTRY_NAME="nobsregistry"

## Pre-requisites steps
# DOC: https://learn.microsoft.com/en-us/azure/container-apps/managed-identity-image-pull?tabs=bash&pivots=bicep
# az extension add --name containerapp --upgrade --allow-preview true
# az identity create --name $IDENTITY --resource-group $RESOURCE_GROUP
IDENTITY_ID=$(az identity show --name $IDENTITY --resource-group $RESOURCE_GROUP --query id --output tsv)
echo "Managed Identity ID: $IDENTITY_ID"

# Create registry if not already created
# az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true
# az acr show --name $ACR_NAME --query loginServer --output table
#
# Create environment if not already created
# az containerapp env create \
#   --name $CONTAINER_APP_ENVIRONMENT \
#   --resource-group $RESOURCE_GROUP \
#   --location $LOCATION

echo "List image repos in registry $ACR_NAME:"
az acr repository list --name $ACR_NAME --output table
echo "List tags in image repo $IMAGE_REPO in registry $ACR_NAME:"
az acr repository show-tags --name $ACR_NAME --repository $IMAGE_REPO --output table

# az containerapp create --name $CONTAINER_APP_NAME \
#     --resource-group $RESOURCE_GROUP \
#     --environment $CONTAINER_APP_ENVIRONMENT \
#     --user-assigned $IDENTITY_ID \
#     --registry-identity $IDENTITY_ID \
#     --registry-server "${REGISTRY_NAME}.azurecr.io" \
#     --image "${IMAGE_NAME}" \
# #    --dns-name-label  "XXXX" \
#
# # To access container app, you need to enable ingress over https
# az containerapp ingress enable -n nobswebsite -g nobsmed --type external --target-port 80 --transport auto
az containerapp ingress enable -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --type external --allow-insecure --target-port 80 --transport auto
#
#
echo "Container App URL:"
az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query "{FQDN:fqdn, IP:ipAddress.ip}" --output table
az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" -o tsv

# az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_APP_NAME --query " {IP:ipAddress.ip, FQDN:ipAddress.fqdn} " --output table
