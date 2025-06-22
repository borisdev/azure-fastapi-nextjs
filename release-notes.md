# Release Notes

## Latest Changes

### Fixes

### Refactors

### Internal

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
