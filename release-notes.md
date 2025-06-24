# Release Notes

## Latest Changes

### Fixes

### Refactors

### Internal

## v8.6 (2025-06-24)

### Developer Experience Improvements
- 🚀 **CLI-Based Deployment**: Scripts now accept version as command-line arguments instead of requiring .env file updates
- 🧹 **Simplified Configuration**: Removed redundant variables from .env (API_VERSION, DB_ENV, IMAGE_NAME, AZURE_SEARCH_SERVICE_*)
- 📝 **Better Documentation**: Clear usage examples and help text for all deployment scripts
- ⚡ **Faster Deployments**: Streamlined workflow with version validation and current-state checking

### Technical Changes
- 🔧 **Dynamic Variable Construction**: IMAGE_NAME and search service URLs now built automatically by scripts
- 🛡️ **Input Validation**: Version format validation with clear error messages
- 📊 **Enhanced Feedback**: Better deployment status reporting and next-step suggestions

### Usage Examples
```bash
./deploy-containerapp.sh v8.6           # Deploy to prod
./deploy-containerapp.sh v8.6 staging   # Deploy to staging
./setup-containerapp.sh v8.6            # Initial setup
```

## v8.5 (2025-06-23)

### New Features
- 🛒 **Amazon Products Page**: Added new Amazon Products section with initial product and placeholder content
- 🤰 **Pregnancy Focus**: Started curating pregnancy-related health products with affiliate integration
- 🔗 **Affiliate Links**: Implemented Amazon affiliate link structure for monetization

### Infrastructure  
- 📦 **Container Deployment**: Successfully deployed to Azure Container Apps as v8.5
- 🌐 **Domain Integration**: Available across all configured domains (nobsmed.com, www.nobsmed.com)

## v8.4 (2025-06-22)

### UX Improvements
- 🏷️ **Enhanced Button Labels**: Improved button UX with type-specific labeling
- 🔍 **Content Type Separation**: Added separate buttons for personal experiences, scientific studies, and mixed content
- 📊 **Better User Guidance**: Users can now easily distinguish between different types of search results

## v8.3 (2025-06-22)

### Infrastructure Improvements
- 🛠️ **Script Organization**: Moved Azure setup scripts from `azure_deploy/` package to root directory
- 📝 **Simplified Naming**: Renamed deployment scripts for clarity:
  - `create_docker_image_registry.sh` → `setup-registry.sh`
  - `create_search_service.sh` → `setup-search.sh`  
  - `create_api_app_container_service.sh` → `setup-containerapp.sh`
- 🧪 **Integration Testing**: Added comprehensive deployment verification with `test-deployment.py`
- 📚 **Documentation**: Updated deployment workflows and script references in CLAUDE.md

### Development Experience
- ⚡ **Better DevOps**: Infrastructure scripts now follow standard conventions at repository root
- 🔍 **Automated Verification**: Production deployments now include automated health checks
- 📖 **Clearer Instructions**: Updated documentation reflects actual file locations and best practices

## v8.1 (2025-06-22)

### UI/UX Improvements
- ✨ **Cleaner Results Interface**: Removed search bar from results page for improved focus and cleaner appearance
- 📍 **Clear Search Context**: Added prominent display of user's search question at the top of results page with visual highlighting
- 🏷️ **Better Button Labels**: Changed collapse button text from "X Health hack results" to "X resulting experiences" for clarity
- 📝 **Enhanced Context**: Updated "Why this matters:" to "Why this health matters to your question:" for better relevance indication

### Bug Fixes
- 🐛 **Fixed Collapse Button Issues**: Resolved critical bug where clicking one card's button would affect other cards
- 🔧 **Unique ID Generation**: Implemented global counter system for truly unique collapse IDs across all cards
- 🛡️ **JavaScript Error Handling**: Added null checks to prevent crashes when DOM elements are conditionally rendered
- ⚡ **Improved Button Reliability**: Enhanced touch handling and click responsiveness for mobile devices

### Technical Improvements
- 🔨 **Template Engine**: Improved Jinja2 template ID generation with namespace counters
- 🎯 **Event Handling**: Better click event management with proper blur() and console debugging
- 📱 **Mobile Optimization**: Enhanced touch-action properties for better mobile experience

## v8.0

### Core Features
- 💡 **Why Care Field**: Added why_care field to search results for better context
- 🔄 **Improved Collapse**: Enhanced collapse functionality for better user interaction
- 🔍 **Search Enhancements**: Various improvements to search functionality and AI processing
