.PHONY: dev test eval dataset lint build infra-up infra-down clean

# Run local development stack (Postgres, Redis, MinIO via Docker Compose + FastAPI locally)
dev:
	@echo "Starting Sketch2STEP infrastructure services..."
	docker compose up -d postgres redis minio
	@echo "Starting FastAPI backend development server on http://localhost:8000..."
	python -m uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

# Run all test suites: API unit & integration tests, RLS isolation tests, CAD spec tests
test:
	@echo "Running full Sketch2STEP enterprise test suite..."
	python -m pytest apps/api/tests packages/spec/tests packages/cad/tests -v

# Run the 30-part accuracy evaluation harness and regression gating
eval:
	@echo "Running accuracy benchmark harness with regression gating..."
	python eval/runner.py --fail-on-regression

# Generate or update the 30 synthetic CAD benchmark datasets
dataset:
	@echo "Generating 30 synthetic benchmark datasets (STEP + DXF + spec)..."
	python eval/generate_dataset.py

# Run code formatters and static type linters
lint:
	@echo "Running Ruff linter..."
	python -m ruff check .
	@echo "Running type checking..."
	python -m mypy apps/api packages/spec

# Start full multi-container production stack
infra-up:
	docker compose up -d --build

infra-down:
	docker compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
