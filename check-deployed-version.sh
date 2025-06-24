#!/bin/bash

# Script to check the currently deployed container version on Azure

echo "🔍 Checking deployed container version..."
echo "=================================="

# Get the current deployed image
DEPLOYED_IMAGE=$(az containerapp show --name nobswebsite --resource-group nobsmed --query "properties.template.containers[0].image" --output tsv 2>/dev/null)

if [ $? -eq 0 ]; then
    echo "✅ Currently deployed image: $DEPLOYED_IMAGE"
    
    # Extract just the version tag
    VERSION=$(echo $DEPLOYED_IMAGE | cut -d':' -f2)
    echo "📦 Version: $VERSION"
    
    # Get deployment status
    echo ""
    echo "🚀 Container App Status:"
    az containerapp show --name nobswebsite --resource-group nobsmed --query "properties.provisioningState" --output tsv 2>/dev/null
    
    # Get last revision status
    echo ""
    echo "📋 Latest Revision Info:"
    az containerapp revision list --name nobswebsite --resource-group nobsmed --query "[0].{Name:name,CreatedTime:properties.createdTime,Active:properties.active}" --output table 2>/dev/null
    
else
    echo "❌ Failed to retrieve container app information"
    echo "Please ensure you are logged into Azure CLI with: az login"
    exit 1
fi