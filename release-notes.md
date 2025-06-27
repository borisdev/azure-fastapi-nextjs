# Release Notes

## Latest Changes

### Fixes

### Refactors

### Internal

## v8.8 (2025-06-27)

### Code Quality & Architecture
- 🏗️ **Unified Data Model**: Consolidated all Amazon product data to use single `AmazonProduct` class with consistent fields (title, url, category, pros, cons, price_range)
- 🧹 **Code Organization**: Split monolithic `jennas_amazon_products.py` into focused modules:
  - `questions.py` - Question data and logic
  - `amazon_products.py` - Product catalog and display logic
- 🗑️ **Technical Debt**: Removed obsolete `InfantProduct` and `HealthHackProduct` classes
- ⚡ **Template Simplification**: Streamlined products page template by removing complex dynamic table configuration

### Bug Fixes
- 🔧 **Data Consistency**: All product categories now display with consistent column structure
- 🛠️ **Template Reliability**: Fixed template rendering issues caused by mixed data structures

### Development Experience
- 📊 **Better Maintainability**: Cleaner separation of concerns between questions and products
- 🧪 **Comprehensive Testing**: Full integration test coverage for all domains and product pages

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

### Previous releases
- Various improvements to search functionality and AI processing
