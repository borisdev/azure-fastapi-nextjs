#!/bin/bash

source .secret
source .env


## Pre-requisites steps
az identity create --name $IDENTITY --resource-group $RESOURCE_GROUP
IDENTITY_ID=$(az identity show --name $IDENTITY --resource-group $RESOURCE_GROUP --query id --output tsv)
echo "Managed Identity ID: $IDENTITY_ID"

# Create registry if not already created
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true
az acr show --name $ACR_NAME --query loginServer --output table

echo "List image repos in registry $ACR_NAME:"
az acr repository list --name $ACR_NAME --output table
echo "List tags in image repo $IMAGE_REPO in registry $ACR_NAME:"
az acr repository show-tags --name $ACR_NAME --repository $IMAGE_REPO --output table
