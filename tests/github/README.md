# Local GitHub Actions Emulator

This directory contains tools for running GitHub Actions validation locally without relying on remote CI.

## Files

- `local_ci.py` - Main Python script that emulates GitHub Actions validation
- `run_local_ci.sh` - Simple shell wrapper for running local CI 
- `run_docker_ci.sh` - Docker-based CI runner for isolated environment
- `Dockerfile` - Docker environment that mimics GitHub Actions Ubuntu runner
- `docker-compose.yml` - Docker Compose configuration for multi-service testing

## Quick Start

### Option 1: Direct Python Execution
```bash
# From project root
python tests/github/local_ci.py
```

### Option 2: Shell Script (Recommended)
```bash
# From project root  
./tests/github/run_local_ci.sh
```

### Option 3: Docker (Most Accurate)
```bash
# From project root
./tests/github/run_docker_ci.sh
```

### Option 4: Docker Compose
```bash
# From project root
cd tests/github
docker-compose up local-ci
```

## What It Validates

The local CI emulator runs the same checks as GitHub Actions:

1. **Python Setup** - Verifies Python version and dependencies
2. **Linting** - Runs ruff linting checks
3. **Testing** - Executes all tests with 100% coverage requirement  
4. **Agreement** - Checks src-test agreement if script exists

## Output

- Console output shows real-time progress
- Final report with pass/fail status for each step
- Coverage percentage display
- JSON report saved as `local_ci_report.json`
- Docker mode saves reports in `tests/github/reports/`

## Benefits

- **Fast feedback** - No waiting for remote CI queues
- **Debugging** - Full control over execution environment
- **Offline capable** - Works without internet connection
- **Cost effective** - No CI minutes consumed
- **Reproducible** - Same environment as GitHub Actions

## Integration

You can integrate this into your development workflow:

```bash
# Add to Makefile
local-ci:
	./tests/github/run_local_ci.sh

# Or create an alias
alias lci="./tests/github/run_local_ci.sh"
```

## Docker Environment

The Docker setup replicates GitHub Actions Ubuntu 24.04 environment:

- Ubuntu 24.04 base image
- Python 3.11
- All system dependencies
- Project mounted as volume for live updates

This ensures maximum compatibility with actual GitHub Actions.