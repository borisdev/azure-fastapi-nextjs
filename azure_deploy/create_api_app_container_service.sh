#!/bin/bash

source .secret
source .env


# Create environment if not already created
# az containerapp env create \
#   --name $CONTAINER_APP_ENVIRONMENT \
#   --resource-group $RESOURCE_GROUP \
#   --location $LOCATION

echo "List image repos in registry $ACR_NAME:"
az acr repository list --name $ACR_NAME --output table
echo "List tags in image repo $IMAGE_REPO in registry $ACR_NAME:"
az acr repository show-tags --name $ACR_NAME --repository $IMAGE_REPO --output table



az containerapp create --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINER_APP_ENVIRONMENT \
    --user-assigned $IDENTITY_ID \
    --registry-identity $IDENTITY_ID \
    --registry-server "${REGISTRY_NAME}.azurecr.io" \
    --image "${IMAGE_NAME}" \
    --env-vars LOGFIRE_TOKEN=$LOGFIRE_TOKEN AZURE_OPENAI_API_KEY=$AZURE_OPENAI_API_KEY WEST_API_KEY=$WEST_API_KEY EASTUS2_API_KEY=$EASTUS2_API_KEY API_KEY=$API_KEY OPENSEARCH_HOST=nlp.nobsmed-api.com LOGFIRE_SEND_TO_LOGFIRE=0 LOGFIRE_ENVIRONMENT=PROD WEB_APP_ENV=PROD AZURE_SEARCH_SERVICE_ENDPOINT=$AZURE_SEARCH_SERVICE_ENDPOINT AZURE_SEARCH_API_KEY=$AZURE_SEARCH_API_KEY

# To access container app, you need to enable ingress over https
# az containerapp ingress enable -n nobswebsite -g nobsmed --type external --target-port 80 --transport auto
az containerapp ingress enable -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --type external --allow-insecure --target-port 80 --transport auto
echo "Container App URL:"
az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query "{FQDN:fqdn, IP:ipAddress.ip}" --output table
az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" -o tsv
az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_APP_NAME --query " {IP:ipAddress.ip, FQDN:ipAddress.fqdn} " --output table
