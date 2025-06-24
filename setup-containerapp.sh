#!/bin/bash

# Script to create a new Azure Container App (one-time setup) with CLI arguments
# Use deploy-containerapp.sh for subsequent deployments

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
    echo "  $0 v8.6                    # Create container app with v8.6 in prod"
    echo "  $0 v8.6 dev                # Create container app with v8.6 in dev"
    echo "  $0 v8.7 staging            # Create container app with v8.7 in staging"
    echo ""
    echo "Note: This script should only be run once for initial setup."
    echo "      Use deploy-containerapp.sh for subsequent deployments."
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

echo "🚀 Creating Container App $CONTAINER_APP_NAME"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   Environment: $CONTAINER_APP_ENVIRONMENT" 
echo "   DB Environment: $DB_ENV"
echo "   Initial Image: $IMAGE_NAME"
echo "   Registry: $ACR_NAME"
echo "   Identity: $IDENTITY_ID"
echo "=================================="

# Check if container app already exists
if az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "❌ Container App '$CONTAINER_APP_NAME' already exists!"
    echo "Use deploy-containerapp.sh to update an existing app."
    exit 1
fi

# Create environment if not already created (uncomment if needed)
# echo "🏗️ Creating Container App Environment..."
# az containerapp env create \
#   --name $CONTAINER_APP_ENVIRONMENT \
#   --resource-group $RESOURCE_GROUP \
#   --location $LOCATION

# Verify image exists in registry
echo "📦 Checking available images in registry..."
az acr repository list --name $ACR_NAME --output table
echo ""
echo "🏷️ Available tags for $IMAGE_REPO:"
az acr repository show-tags --name $ACR_NAME --repository $IMAGE_REPO --output table

# Verify the specific image exists
echo ""
echo "🔍 Verifying initial image exists..."
if ! az acr repository show-tags --name $ACR_NAME --repository $IMAGE_REPO --output tsv | grep -q "^${API_VERSION}$"; then
    echo "❌ Image tag '$API_VERSION' not found in registry!"
    echo "Build and push the image first:"
    echo "   cd backend"
    echo "   docker buildx build --platform linux/amd64 -t nobsregistry.azurecr.io/$IMAGE_REPO:$API_VERSION ."
    echo "   docker push nobsregistry.azurecr.io/$IMAGE_REPO:$API_VERSION"
    exit 1
fi

# Create the container app
echo ""
echo "🔨 Creating container app..."
az containerapp create --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINER_APP_ENVIRONMENT \
    --user-assigned $IDENTITY_ID \
    --registry-server "${REGISTRY_NAME}.azurecr.io" \
    --image "${IMAGE_NAME}" \
    --env-vars LOGFIRE_TOKEN=$LOGFIRE_TOKEN AZURE_OPENAI_API_KEY=$AZURE_OPENAI_API_KEY WEST_API_KEY=$WEST_API_KEY EASTUS2_API_KEY=$EASTUS2_API_KEY API_KEY=$API_KEY OPENSEARCH_HOST=nlp.nobsmed-api.com LOGFIRE_SEND_TO_LOGFIRE=0 LOGFIRE_ENVIRONMENT=PROD WEB_APP_ENV=PROD AZURE_SEARCH_SERVICE_ENDPOINT=$AZURE_SEARCH_SERVICE_ENDPOINT AZURE_SEARCH_API_KEY=$AZURE_SEARCH_API_KEY

# Enable ingress
echo ""
echo "🌐 Enabling ingress..."
az containerapp ingress enable -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --type external --allow-insecure --target-port 80 --transport auto

# Configure scaling
echo ""
echo "⚖️ Configuring scaling rules..."
az containerapp update --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --min-replicas 1 \
    --max-replicas 10 \
    --scale-rule-name my-http-scale-rule \
    --scale-rule-http-concurrency 1

# Show final status
echo ""
echo "✅ Container App created successfully!"
echo "🔗 Container App URLs:"
az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query "{FQDN:fqdn, IP:ipAddress.ip}" --output table
echo ""
echo "📍 Direct URL:"
az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" -o tsv

echo ""
echo "🎉 Setup complete!"
echo "💡 Future deployments:"
echo "   ./deploy-containerapp.sh v8.7     # Deploy new version"
echo "   ./check-deployed-version.sh       # Check current version"