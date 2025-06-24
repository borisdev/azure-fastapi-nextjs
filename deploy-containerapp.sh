#!/bin/bash

# Script to deploy/update an existing Azure Container App with CLI arguments
# Use setup-containerapp.sh for initial container app creation

set -e

# Default values
DEFAULT_DB_ENV="prod"
DEFAULT_API_VERSION="v8.5"

# Usage function
usage() {
    echo "Usage: $0 <API_VERSION> [DB_ENV]"
    echo ""
    echo "Arguments:"
    echo "  API_VERSION    Docker image version tag (e.g., v8.6)"
    echo "  DB_ENV         Database environment (default: $DEFAULT_DB_ENV)"
    echo ""
    echo "Examples:"
    echo "  $0 v8.6                    # Deploy v8.6 to prod environment"
    echo "  $0 v8.6 dev                # Deploy v8.6 to dev environment"
    echo "  $0 v8.7 staging            # Deploy v8.7 to staging environment"
    echo ""
    echo "Current deployed version:"
    if command -v az &> /dev/null; then
        CURRENT=$(az containerapp show --name nobswebsite --resource-group nobsmed --query "properties.template.containers[0].image" --output tsv 2>/dev/null | cut -d':' -f2)
        echo "  $CURRENT"
    else
        echo "  (az CLI not available)"
    fi
    exit 1
}

# Parse arguments
if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
fi

API_VERSION="$1"
DB_ENV="${2:-$DEFAULT_DB_ENV}"

# Validate API_VERSION format
if [[ ! "$API_VERSION" =~ ^v[0-9]+(\.[0-9]+)*$ ]]; then
    echo "❌ Error: API_VERSION must follow format 'vX.Y' (e.g., v8.6)"
    echo "   Provided: $API_VERSION"
    exit 1
fi

# Source environment variables
source .secret
source .env

# Construct dynamic variables
IMAGE_NAME="nobsregistry.azurecr.io/$IMAGE_REPO:$API_VERSION"
AZURE_SEARCH_SERVICE_NAME="nobssearch-$DB_ENV"  
AZURE_SEARCH_SERVICE_ENDPOINT="https://nobssearch-$DB_ENV.search.windows.net"

echo "🚀 Deploying to Container App"
echo "   Container App: $CONTAINER_APP_NAME"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   Environment: $DB_ENV"
echo "   New Image: $IMAGE_NAME"
echo "   Registry: $ACR_NAME"
echo "=================================="

# Check if container app exists
if ! az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "❌ Container App '$CONTAINER_APP_NAME' does not exist!"
    echo "Use setup-containerapp.sh to create it first."
    exit 1
fi

# Show current deployed version
echo "📋 Current deployment status:"
CURRENT_IMAGE=$(az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query "properties.template.containers[0].image" --output tsv)
CURRENT_VERSION=$(echo "$CURRENT_IMAGE" | cut -d':' -f2)
echo "   Current: $CURRENT_VERSION"
echo "   New: $API_VERSION"

if [ "$CURRENT_VERSION" = "$API_VERSION" ]; then
    echo "⚠️  Warning: Deploying same version ($API_VERSION). Continue? (y/N)"
    read -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled."
        exit 0
    fi
fi

# Verify new image exists in registry
echo ""
echo "🔍 Verifying image exists in registry..."
if ! az acr repository show-tags --name $ACR_NAME --repository $IMAGE_REPO --output tsv | grep -q "^${API_VERSION}$"; then
    echo "❌ Image tag '$API_VERSION' not found in registry!"
    echo "Available tags:"
    az acr repository show-tags --name $ACR_NAME --repository $IMAGE_REPO --output table
    exit 1
fi

# Update the container app
echo ""
echo "🔄 Updating container app with new image..."
az containerapp update --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --image "$IMAGE_NAME"

# Wait for deployment to complete
echo ""
echo "⏳ Waiting for deployment to complete..."
sleep 10

# Verify deployment
echo ""
echo "✅ Deployment verification:"
NEW_IMAGE=$(az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query "properties.template.containers[0].image" --output tsv)
NEW_VERSION=$(echo "$NEW_IMAGE" | cut -d':' -f2)
echo "   Deployed Version: $NEW_VERSION"

REVISION_STATUS=$(az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query "properties.provisioningState" --output tsv)
echo "   Status: $REVISION_STATUS"

# Show latest revision info
echo ""
echo "📋 Latest revision:"
az containerapp revision list --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query "[0].{Name:name,CreatedTime:properties.createdTime,Active:properties.active,Image:properties.template.containers[0].image}" --output table

# Show app URLs
echo ""
echo "🔗 Application URLs:"
az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" -o tsv

echo ""
if [ "$NEW_VERSION" = "$API_VERSION" ] && [ "$REVISION_STATUS" = "Succeeded" ]; then
    echo "🎉 Deployment successful!"
    echo "💡 Next steps:"
    echo "   - Run integration tests: poetry run python test-deployment.py"
    echo "   - Check version: ./check-deployed-version.sh"
    echo "   - Update release notes with v$API_VERSION changes"
else
    echo "❌ Deployment may have failed. Check Azure portal for details."
    exit 1
fi