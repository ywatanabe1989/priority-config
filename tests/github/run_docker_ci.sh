#!/bin/bash
# Docker-based local CI runner
# Usage: ./tests/github/run_docker_ci.sh

set -e

# Get the project root directory (two levels up from this script)
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
GITHUB_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🐳 Docker-based Local CI Emulator${NC}"
echo "Project Root: $PROJECT_ROOT"
echo

# Check if docker is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker.${NC}"
    exit 1
fi

# Create reports directory if it doesn't exist
mkdir -p "$GITHUB_DIR/reports"

echo -e "${BLUE}🏗️  Building Docker image...${NC}"
docker build -f tests/github/Dockerfile -t minimal-pip-project-ci . || {
    echo -e "${RED}❌ Failed to build Docker image${NC}"
    exit 1
}

echo -e "${GREEN}🚀 Running CI in Docker container...${NC}"
docker run --rm \
    -v "$PROJECT_ROOT:/workspace" \
    -v "$GITHUB_DIR/reports:/workspace/reports" \
    -w /workspace \
    minimal-pip-project-ci "$@"

echo -e "${GREEN}✅ Docker CI completed${NC}"
echo -e "Reports saved in: ${YELLOW}tests/github/reports/${NC}"