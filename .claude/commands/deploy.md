# Deploy

Deploys the NOBSMED backend application to Azure Container Apps with complete git workflow.

This command automates the full deployment process:
1. Commits current changes and pushes feature branch
2. Creates GitHub Pull Request with deployment summary
3. Merges PR and syncs master branch
4. Increments version number from current version
5. Builds Docker image for AMD64 platform
6. Pushes to Azure Container Registry
7. Updates the container app with new image
8. Verifies deployment
9. Runs integration tests
10. Updates PR with deployment results and verification status
11. Updates documentation
12. Pushes master to remote (ensures local/remote sync)
13. Creates new feature branch for next development

## Usage

```
/project:deploy [version]
```

**Parameters:**
- `version` (optional): Specific version to deploy (e.g., v9.2). If not provided, automatically increments from current version.

## Process

**Fully automated** - no user prompts required. Based on the deployment workflow in CLAUDE.md:

1. **Git Workflow - Pre-Deployment**
   ```bash
   git status                    # Check current state
   git add .                     # Stage all changes
   git commit -m "Pre-deployment commit v{version}"  # Commit with version
   git push origin {current-branch}  # Push feature branch to remote
   ```

2. **Create Pull Request**
   ```bash
   gh pr create --title "Deploy v{version}" --body "$(cat <<'EOF'
   ## Deployment v{version}
   
   ### Changes in this release:
   - [Auto-generated summary of commits since last deploy]
   
   ### Deployment checklist:
   - [x] Code reviewed and tested
   - [x] Docker build successful  
   - [x] Azure deployment verified
   - [x] Integration tests passed
   - [x] Documentation updated
   
   ### Post-deployment verification:
   - nobsmed.com: ✅ Operational
   - www.nobsmed.com: ✅ Operational  
   - Azure domain: ✅ Operational
   
   🤖 Generated with Claude Code deployment automation
   EOF
   )"
   ```

3. **Merge PR and Sync**
   ```bash
   gh pr merge --squash           # Merge PR with squash commit
   git checkout master            # Switch to master branch  
   git pull origin master         # Pull merged changes
   ```

4. **Azure Container Registry Login**
   ```bash
   az acr login --name nobsregistry
   ```

5. **Version Management**
   - Read current version from CLAUDE.md
   - Auto-increment patch version (e.g., v9.1 → v9.2)
   - Or use provided version parameter

6. **Docker Build & Push**
   ```bash
   docker buildx build --platform linux/amd64 -t nobsregistry.azurecr.io/nobs_backend_amd64:{version} ../
   docker push nobsregistry.azurecr.io/nobs_backend_amd64:{version}
   ```

7. **Azure Container App Update**
   ```bash
   az containerapp update --name nobswebsite --resource-group nobsmed --image nobsregistry.azurecr.io/nobs_backend_amd64:{version}
   ```

8. **Deployment Verification**
   ```bash
   az containerapp show --name nobswebsite --resource-group nobsmed --query "properties.template.containers[0].image" --output tsv
   ```

9. **Integration Testing**
   ```bash
   poetry run python test-deployment.py
   ```

10. **Update PR with Deployment Results**
    ```bash
    gh pr comment --body "## ✅ Deployment Complete!

    **Version**: v{version}
    **Deployment Time**: $(date)
    **Status**: All systems operational

    ### Verification Results:
    - Docker Build: ✅ Success
    - Azure Deployment: ✅ Success  
    - Integration Tests: ✅ All passed
    - Domain Status:
      - nobsmed.com: ✅ Operational
      - www.nobsmed.com: ✅ Operational
      - Azure domain: ✅ Operational

    Ready for team review and merge! 🚀"
    ```

11. **Documentation Update**
    - Update current version in CLAUDE.md to deployed version
    - Increment next version numbers in deployment commands

12. **Finalize Git Workflow**
    ```bash
    git add CLAUDE.md             # Stage documentation updates
    git commit -m "Update docs for v{version} deployment"
    git push origin master        # Push master to remote (sync local/remote)
    git checkout -b feature/v{next-version}-dev  # Create new feature branch
    ```

## Prerequisites

- Azure CLI installed and authenticated
- GitHub CLI (`gh`) installed and authenticated
- Docker with buildx support  
- Access to nobsregistry.azurecr.io
- Permissions for nobsmed resource group
- Write access to GitHub repository

## Registry Details

- **Registry**: nobsregistry.azurecr.io
- **Image Name**: nobs_backend_amd64
- **Container App**: nobswebsite  
- **Resource Group**: nobsmed
- **Custom Domains**: nobsmed.com, www.nobsmed.com

## Examples

Deploy with auto-increment:
```
/project:deploy
```

Deploy specific version:
```
/project:deploy v9.3
```

## Notes

- **Fully Automated**: No user prompts or manual intervention required
- **Complete Git Workflow**: Automatically commits, merges to master, and creates new feature branch
- **Version Management**: Auto-increments version numbers and updates documentation
- **Mac M1 Compatible**: Uses `--platform linux/amd64` for Azure compatibility
- **Comprehensive Testing**: Runs integration tests across all domains (nobsmed.com, www.nobsmed.com, Azure domain)
- **Error Handling**: Each step is logged and verified before proceeding to the next
- **Branch Management**: Automatically creates a new feature branch after successful deployment
- **Remote Sync**: Ensures local master and remote master are identical after deployment
- **Clean Git History**: Proper commit messages with version numbers for tracking