#!/usr/bin/env bash
set -euo pipefail

TAG="${1:-latest}"
DOCKER_USER="${DOCKER_USER:-prathamshah}"
IMAGE_NAME="aegis-api"
FULL_TAG="${DOCKER_USER}/${IMAGE_NAME}:${TAG}"

echo "=== Building ${FULL_TAG} ==="
docker build -t "${FULL_TAG}" .

echo ""
echo "=== Pushing to Docker Hub ==="
docker push "${FULL_TAG}"

echo ""
echo "=== Done ==="
echo "Pull with:  docker pull ${FULL_TAG}"
echo "Run with:   docker run -p 8000:8000 ${FULL_TAG}"
