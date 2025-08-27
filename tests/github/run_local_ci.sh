#!/bin/bash
# Simple wrapper script for running local CI
# Usage: ./tests/github/run_local_ci.sh [options]

set -e

# Get the project root directory (two levels up from this script)
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Local GitHub Actions Emulator${NC}"
echo "Project Root: $PROJECT_ROOT"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi

# Check if we're in a virtual environment or have dependencies
if ! python3 -c "import pytest" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Installing dependencies...${NC}"
    pip install -e ".[dev]" || {
        echo -e "${RED}❌ Failed to install dependencies${NC}"
        exit 1
    }
fi

# Run the local CI emulator
echo -e "${GREEN}🔍 Running local CI validation...${NC}"
python3 tests/github/local_ci.py "$@"