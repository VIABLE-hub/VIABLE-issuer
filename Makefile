# Makefile for StudentVC Backend Application

BACKEND_DIR = backend
VENV_DIR = .venv
PYTHON = python3
PIP = pip3
PORT = 8080
HOST = 0.0.0.0
BASE_URL = https://localhost:$(PORT)

.PHONY: dev setup install clean kill-port activate info test setup-test dev-root dev-tub dev-fub dev-veritas dev-all start-all stop-all dev-ngrok docker-build docker-bbs docker-run docker-down test-bbs-linux test-docker-api debug-bbs-docker hot-patch-bbs monitor-bbs predeploy test-bbs-docker setup-bbs use-macos-bbs use-linux-bbs test-startup

# Zeigt Informationen über die Umgebung
info:
	@echo "BBS Core Backend Information:"
	@echo "Backend-Folder: $(BACKEND_DIR)"
	@echo "Virtual Environment: $(VENV_DIR)"
	@echo "Python: $(PYTHON)"
	@echo "Pip: $(PIP)"
	@echo "Port: $(PORT)"
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "Virtual Environment exists"; \
		echo "Python-Version: $$($(PYTHON) --version 2>&1)"; \
	else \
		echo "Virtual Environment does not exist"; \
	fi

# Startet die Anwendung mit root tenant on port 8083
dev-root:
ifeq ($(OS),Windows_NT)
	@echo "Starting StudentVC with ROOT tenant on port 8083"
	cd backend && set TENANT_ID=root&& set SERVER_PORT=8083&& ..\.venv\Scripts\python.exe main.py
else
	@echo "Starte StudentVC mit Root Tenant auf Port 8083"
	cd $(BACKEND_DIR) && TENANT_ID=root SERVER_PORT=8083 ../$(VENV_DIR)/bin/python main.py
endif

# Startet die Anwendung mit TU Berlin tenant on port 8081
dev-tub:
ifeq ($(OS),Windows_NT)
	@echo "Starting StudentVC with TUB tenant on port 8081"
	cd backend && set TENANT_ID=tub&& set SERVER_PORT=8081&& ..\.venv\Scripts\python.exe main.py
else
	@echo "Starting StudentVC with TUB tenant on port 8081"
	cd backend && TENANT_ID=tub SERVER_PORT=8081 ../.venv/bin/python main.py
endif

# Startet die Anwendung mit FU Berlin tenant on port 8082
dev-fub:
ifeq ($(OS),Windows_NT)
	@echo "Starting StudentVC with FUB tenant on port 8082"
	cd backend && set TENANT_ID=fub&& set SERVER_PORT=8082&& ..\.venv\Scripts\python.exe main.py
else
	@echo "Starte StudentVC mit FUB Tenant auf Port 8082"
	cd $(BACKEND_DIR) && TENANT_ID=fub SERVER_PORT=8082 ../$(VENV_DIR)/bin/python main.py
endif

# Startet die Anwendung mit Veritas tenant on port 8080
dev-veritas:
ifeq ($(OS),Windows_NT)
	@echo "Starting StudentVC with VERITAS tenant on port 8080"
	cd backend && set TENANT_ID=veritas&& set SERVER_PORT=8080&& ..\.venv\Scripts\python.exe main.py
else
	@echo "Starte StudentVC mit Veritas Tenant auf Port 8080"
	cd $(BACKEND_DIR) && TENANT_ID=veritas SERVER_PORT=8080 ../$(VENV_DIR)/bin/python main.py
endif


# Starts ALL tenants on different ports simultaneously
dev-all:
	@echo "╔════════════════════════════════════════════════════════════════╗"
	@echo "║                                                                ║"
	@echo "║          Starting ALL Tenants Simultaneously                   ║"
	@echo "║                                                                ║"
	@echo "╚════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "Stopping any existing servers..."
	@./scripts/start-all-tenants.sh

# Stop all tenant servers
stop-all:
	@echo "Stopping all tenant servers..."
	@bash -c 'lsof -ti:8080 | xargs kill -9 2>/dev/null && echo "  Stopped Veritas (port 8080)" || echo "  ⚠️  No server on port 8080"'
	@bash -c 'lsof -ti:8081 | xargs kill -9 2>/dev/null && echo "  Stopped TUB (port 8081)" || echo "  ⚠️  No server on port 8081"'
	@bash -c 'lsof -ti:8082 | xargs kill -9 2>/dev/null && echo "  Stopped FUB (port 8082)" || echo "  ⚠️  No server on port 8082"'
	@bash -c 'lsof -ti:8083 | xargs kill -9 2>/dev/null && echo "  Stopped ROOT (port 8083)" || echo "  ⚠️  No server on port 8083"'
	@rm -f logs/*.pid 2>/dev/null || true
	@echo ""
	@echo "All tenants stopped"

# Alias for dev-all
start-all: dev-all

# Default development mode mit Root Tenant
dev:
	@echo "Starte StudentVC (Default Tenant: Root)"
	cd $(BACKEND_DIR) && ../$(VENV_DIR)/bin/python main.py --host $(HOST) --port $(PORT)

# Erstellt die virtuelle Umgebung und installiert Abhängigkeiten
setup:
ifeq ($(OS),Windows_NT)
	@echo "Creating virtual environment: .venv"
	python -m venv .venv
	@echo "Installing dependencies"
	.venv\Scripts\python.exe -m pip install --upgrade pip
	.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
else
	@echo "Creating virtual environment: .venv"
	python3 -m venv .venv
	@echo "Installing dependencies"
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r backend/requirements.txt
endif

# Installiert nur Abhängigkeiten (ohne venv zu erstellen)
install:
	@echo "Installing Dependencies in existing enviornment"
	$(VENV_DIR)/bin/pip install -r $(BACKEND_DIR)/requirements.txt

# Bereinigt temporäre Dateien
clean:
	@echo "Cleaning up temporary files"
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +

# Tötet Prozesse auf dem angegebenen Port
kill-port:
	@echo "Kill Processes on Port $(PORT)"
	-lsof -ti:$(PORT) | xargs kill -9

# Führt Tests aus
test:
	@echo "Starting tests"
	cd $(BACKEND_DIR) && ../$(VENV_DIR)/bin/pytest

# Richtet die Testumgebung ein
setup-test:
	@echo "Setting up testing environment"
	$(VENV_DIR)/bin/pip install -r $(BACKEND_DIR)/test/requirements.txt

# Docker targets

# Build Docker images for all tenants
docker-build:
	@echo "Building Docker images for all tenants"
	cd deploy && docker-compose -f configs/docker-compose.yml build

# Run BBS+ test in Docker to verify Linux compatibility
docker-bbs:
	@echo "Running BBS+ test in Docker to verify Linux compatibility"
	cd backend && docker build --target bbs-test -t bbs-test .
	@echo "Starting BBS+ test container..."
	docker run --rm bbs-test

# Test BBS+ Linux compatibility using our test script
test-bbs-linux:
	@echo "Testing BBS+ Linux compatibility"
	./test_bbs_linux_docker.sh

# Start Docker containers for all tenants
docker-run:
	@echo "Starting Docker containers for all tenants"
	cd deploy && docker-compose -f configs/docker-compose.yml up

# Stop Docker containers
docker-down:
	@echo "Stopping Docker containers"
	cd deploy && docker-compose -f configs/docker-compose.yml down

# Test BBS+ Core in Docker Containers
test-bbs-docker:
	@echo "Testing BBS+ core functionality in Docker containers..."
	@chmod +x scripts/testing/test_docker_bbs_core.sh
	@./scripts/testing/test_docker_bbs_core.sh

# BBS+ Build Management
setup-bbs:
	@echo "Setting up BBS+ build management..."
	@chmod +x scripts/testing/setup_bbs_builds.sh
	@./scripts/testing/setup_bbs_builds.sh

# Apply macOS BBS+ build for local development
use-macos-bbs:
	@echo "Applying macOS BBS+ build for local development..."
	@cp backend/bbs-core/macos-build/bbs_core.py backend/bbs_core.py 2>/dev/null || echo "⚠️  macOS build not found, run 'make setup-bbs' first"
	@cp backend/bbs-core/macos-build/libuniffi_bbs_core.dylib backend/libuniffi_bbs_core.dylib 2>/dev/null || echo "⚠️  macOS dylib not found"
	@echo "Ready for local development"

# Apply Linux BBS+ build for Docker deployment
use-linux-bbs:
	@echo "Applying Linux BBS+ build for Docker deployment..."
	@cp backend/bbs-core/linux-build/bbs_core.py backend/bbs_core.py 2>/dev/null || echo "⚠️  Linux build not found"
	@cp backend/bbs-core/linux-build/libuniffi_bbs_core.so backend/libuniffi_bbs_core.dylib 2>/dev/null || echo "⚠️  Linux .so not found"
	@echo "Ready for Docker deployment"

# Pre-deployment testing
predeploy:
	@echo "Running pre-deployment tests..."
	@mkdir -p logs
	@chmod +x scripts/testing/predeploy_test.sh
	@./scripts/testing/predeploy_test.sh

# Comprehensive startup testing
test-startup:
	@echo "Running comprehensive startup tests..."
	@$(VENV_DIR)/bin/python test_startup.py

# User Management
create-veritas-admin:
	@echo "Creating Veritas admin user..."
	@cd backend && python3 scripts/create_veritas_admin.py

show-veritas-credentials:
	@echo ""
	@echo "============================================================"
	@echo "  VERITAS ADMIN CREDENTIALS"
	@echo "============================================================"
	@echo "  Tenant:   Veritas University"
	@echo "  URL:      http://localhost:5005/veritas"
	@echo "  Username: admin@veritas.edu"
	@echo "  Password: VeritasAdmin2024!"
	@echo "============================================================"
	@echo "  Login:    http://localhost:5005/veritas/login"
	@echo "============================================================"
	@echo ""

# Diagnostic Tools
check-disclosure-veritas:
	@echo "Checking Veritas selective disclosure settings..."
	@python3 backend/scripts/check_disclosure_settings.py veritas

check-disclosure-tuberlin:
	@echo "Checking TU Berlin selective disclosure settings..."
	@python3 backend/scripts/check_disclosure_settings.py tuberlin

check-disclosure-fuberlin:
	@echo "Checking FU Berlin selective disclosure settings..."
	@python3 backend/scripts/check_disclosure_settings.py fuberlin

check-disclosure-root:
	@echo "Checking Root tenant selective disclosure settings..."
	@python3 backend/scripts/check_disclosure_settings.py root

check-disclosure-all:
	@echo "Checking ALL tenants selective disclosure settings..."
	@echo ""
	@make check-disclosure-root
	@echo ""
	@make check-disclosure-tuberlin
	@echo ""
	@make check-disclosure-fuberlin
	@echo ""
	@make check-disclosure-veritas

# Debug selective disclosure with live server
test-disclosure-debug:
	@echo "Testing selective disclosure debug endpoint..."
	@echo "⚠️  Make sure server is running (make dev in another terminal)"
	@echo ""
	@curl -s http://localhost:5005/veritas/verifier/debug/selective-disclosure | python3 -m json.tool || echo "Error: Is the server running? Run 'make dev' first."
