#!/bin/bash
set -e

# Deploy script for GCP Compute Engine
# Usage: ./deploy.sh [version]
# Examples:
#   ./deploy.sh v1.0.0   # Deploy specific version
#   ./deploy.sh latest   # Deploy latest from main branch

VERSION=${1:-latest}
APP_DIR="/home/deploy/api-server"
COMPOSE_FILE="guanfu_backend/docker-compose.yaml"

echo "=========================================="
echo "Starting deployment of GuanFu Backend v${VERSION}"
echo "=========================================="

# Navigate to app directory
cd "${APP_DIR}"

# Pull latest code from GitHub
echo "Fetching latest code from GitHub..."
git fetch --all --tags
if [ "${VERSION}" != "latest" ]; then
    echo "Checking out version: ${VERSION}"
    git checkout "${VERSION}"
else
    echo "Checking out main branch"
    git checkout main
    git pull origin main
fi

# Navigate to backend directory
cd guanfu_backend

# Check if .env file exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy .env.example to .env and configure it"
    exit 1
fi

# Stop only backend container (keep DB and nginx running)
echo "Stopping old backend container..."
docker compose stop backend

# Clean up unused images (optional, saves space)
echo "Cleaning up unused Docker images..."
docker image prune -f

# Rebuild only backend service
echo "Building new backend image..."
docker compose build --no-cache backend

echo "Starting new backend container..."
docker compose up -d --force-recreate backend

# Wait for service to start
echo "Waiting for backend service to start..."
sleep 10

# Check service status
echo "Checking service status..."
docker compose ps

# Check backend health
echo "Checking backend health..."
for i in {1..30}; do
    if curl -f http://localhost:8000/docs >/dev/null 2>&1; then
        echo "✓ Backend service is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "✗ Backend service startup timeout"
        docker compose logs backend
        exit 1
    fi
    echo "Waiting for backend service... ($i/30)"
    sleep 2
done

# Show recent logs (last 20 lines)
echo "=========================================="
echo "Recent logs:"
echo "=========================================="
docker compose logs --tail=20 backend

echo "=========================================="
echo "Deployment completed! Version: ${VERSION}"
echo "Backend: http://localhost:8000"
echo "=========================================="
