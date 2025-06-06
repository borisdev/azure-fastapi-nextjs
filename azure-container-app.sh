#!/bin/bash

# Variables
RESOURCE_GROUP="myResourceGroup"
LOCATION="eastus"
CONTAINER_APP_ENVIRONMENT="myContainerAppEnv"
CONTAINER_APP_NAME="myContainerApp"
IMAGE="mcr.microsoft.com/azuredocs/aci-helloworld:latest"

# Create a resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create a Container Apps environment
az containerapp env create \
  --name $CONTAINER_APP_ENVIRONMENT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Create a Container App
az containerapp create \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINER_APP_ENVIRONMENT \
  --image $IMAGE \
  --target-port 80 \
  --ingress 'external'


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


# Output the URL of the Container App
echo "Container App URL:"
az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" -o tsv

