#!/bin/bash

#az search service delete --name $SEARCH_SERVICE_NAME --resource-group $RESOURCE_GROUP

# Create Azure Search Service Resource if not already created
# free stops after adding a few experimental indexes, so use Standard for production
az search service create \
    --name $SEARCH_SERVICE_NAME \
    --resource-group $RESOURCE_GROUP \
    --sku Standard \
    --partition-count 1 \
    --replica-count 1 \

echo ""
echo "List all search services in subscription:"
az resource list --resource-type Microsoft.Search/searchServices --output table
echo ""
echo "List of Search Services in Resource Group $RESOURCE_GROUP:"
az search service list --resource-group $RESOURCE_GROUP --output table
echo ""
echo "Search Service Hostname:"
az search service show --name $SEARCH_SERVICE_NAME --resource-group $RESOURCE_GROUP --query "hostName" --output table
echo ""
echo "Search Service API Key:"
az search admin-key show --service-name $SEARCH_SERVICE_NAME --resource-group $RESOURCE_GROUP --query "primaryKey" --output tsv
echo ""
# Manually Get URL from Azure Portal
# https://nobssearch.search.windows.net
#Search Service API Key:
