# TodayAtSG Development Makefile

.PHONY: help setup dev prod down clean logs test lint format migrate seed

# Default target
help:
	@echo "Available commands:"
	@echo "  setup     - Initial project setup"
	@echo "  dev       - Start development environment"
	@echo "  prod      - Start production environment"
	@echo "  down      - Stop all services"
	@echo "  clean     - Clean up containers and volumes"
	@echo "  logs      - View logs from all services"
	@echo "  test      - Run tests"
	@echo "  lint      - Run linting"
	@echo "  format    - Format code"
	@echo "  migrate   - Run database migrations"
	@echo "  seed      - Seed database with sample data"

# Initial setup
setup:
	@echo "Setting up TodayAtSG development environment..."
	cp .env.example backend/.env
	cp .env.example frontend/.env
	docker-compose build
	@echo "Setup complete! Run 'make dev' to start development."

# Development environment
dev:
	@echo "Starting development environment..."
	docker-compose up -d postgres redis
	@echo "Waiting for database to be ready..."
	sleep 10
	docker-compose up backend frontend celery_worker

# Production environment
prod:
	@echo "Starting production environment..."
	docker-compose -f docker-compose.prod.yml up -d

# Stop all services
down:
	@echo "Stopping all services..."
	docker-compose down

# Clean up
clean:
	@echo "Cleaning up containers and volumes..."
	docker-compose down -v
	docker system prune -f

# View logs
logs:
	docker-compose logs -f

# Run backend tests
test:
	@echo "Running backend tests..."
	cd backend && python -m pytest tests/ -v
	@echo "Running frontend tests..."
	cd frontend && npm run test

# Lint code
lint:
	@echo "Linting backend code..."
	cd backend && flake8 app/
	cd backend && mypy app/
	@echo "Linting frontend code..."
	cd frontend && npm run lint

# Format code
format:
	@echo "Formatting backend code..."
	cd backend && black app/
	cd backend && isort app/
	@echo "Formatting frontend code..."
	cd frontend && npm run format

# Run database migrations
migrate:
	@echo "Running database migrations..."
	docker-compose exec backend alembic upgrade head

# Seed database
seed:
	@echo "Seeding database with sample data..."
	docker-compose exec backend python -m app.db.seed

# Backend only (for faster development)
backend:
	@echo "Starting backend services only..."
	docker-compose up -d postgres redis
	sleep 5
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend only (for faster development)
frontend:
	@echo "Starting frontend development server..."
	cd frontend && npm run dev

# Install dependencies
install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Database shell
db-shell:
	docker-compose exec postgres psql -U postgres -d todayatsg

# Backend shell
backend-shell:
	docker-compose exec backend python

# Check services status
status:
	docker-compose ps

# View specific service logs
backend-logs:
	docker-compose logs -f backend

frontend-logs:
	docker-compose logs -f frontend

db-logs:
	docker-compose logs -f postgres