# Development cheatsheet

```bash
# Pre-requisites
$docker-compose --version
Docker Compose version v2.1.1
# Upgrade if needed to at least version 2.22.0 and later, part of Docker Desktop (mac)
brew install docker-compose
$docker-compose --version
Docker Compose version 2.36.2
docker compose -f docker-compose.yml -f docker-compose.override.yml watch
# docker compose watch
docker compose logs
docker compose logs backend
```

### Development URLs

Development URLs, for local development.

Frontend: http://localhost:5173

Backend: http://localhost:8000

Automatic Interactive Docs (Swagger UI): http://localhost:8000/docs

Automatic Alternative Docs (ReDoc): http://localhost:8000/redoc

Adminer: http://localhost:8080

Traefik UI: http://localhost:8090

MailCatcher: http://localhost:1080
