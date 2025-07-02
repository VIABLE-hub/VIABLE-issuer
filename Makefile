# Makefile for StudentVC Backend Application
# Uses test_env in root directory and starts app on port 8080 with HTTPS

BACKEND_DIR = backend
VENV_DIR = test_env
PYTHON = python3
PIP = pip3
PORT = 8080
HOST = 0.0.0.0
BASE_URL = https://localhost:$(PORT)

.PHONY: dev setup install clean kill-port activate info test setup-test dev-root dev-tub dev-fub

# Zeigt Informationen über die Umgebung
info:
	@echo "📋 BBS Core Backend Informationen:"
	@echo "📁 Backend-Verzeichnis: $(BACKEND_DIR)"
	@echo "🐍 Virtuelle Umgebung: $(VENV_DIR) (Root-Level)"
	@echo "🔧 Python: $(PYTHON)"
	@echo "📦 Pip: $(PIP)"
	@echo "🌐 Port: $(PORT)"
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "✅ Virtuelle Umgebung existiert"; \
		echo "🐍 Python-Version: $$($(PYTHON) --version 2>/dev/null || echo 'Nicht verfügbar')"; \
	else \
		echo "❌ Virtuelle Umgebung nicht gefunden"; \
		echo "💡 Führe 'make setup' aus"; \
	fi

# Test target - runs tests using test_env
test:
	@echo "🧪 Running tests in test_env environment..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "❌ Virtuelle Umgebung nicht gefunden: $(VENV_DIR)"; \
		echo "💡 Führe 'make setup' aus"; \
		exit 1; \
	fi
	@$(PYTHON) $(VENV_DIR)/run_all_tests.py --url $(BASE_URL)
	@echo "✅ All tests completed."

# Setup test environment - installs required testing packages in test_env
setup-test:
	@echo "🧪 Setting up test_env environment..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "❌ Virtuelle Umgebung nicht gefunden: $(VENV_DIR)"; \
		echo "💡 Führe 'make setup' aus"; \
		exit 1; \
	fi
	@$(PYTHON) $(VENV_DIR)/install_requirements.py
	@echo "✅ Test environment setup completed."

# Zeigt Aktivierungsbefehl für manuelle Nutzung
activate:
	@echo "🔧 Um die virtuelle Umgebung manuell zu aktivieren:"
	@echo "   source $(VENV_DIR)/bin/activate"
	@echo ""
	@echo "🚀 Oder verwende einfach 'make dev' um direkt zu starten"

# 🏛️ TENANT-SPECIFIC TARGETS - ISOLATED DATABASES PER TENANT

# Root tenant (default StudentVC branding)
dev-root:
	@echo "🔷 Starte StudentVC (Root/Default Tenant)..."
	@echo "🏛️  Tenant: Root (Default StudentVC)"
	@echo "💾 Database: Isolated Root Tenant Database"
	@pkill -f "python.*main.py" 2>/dev/null || true
	@make kill-port
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "❌ Virtuelle Umgebung nicht gefunden: $(VENV_DIR)"; \
		echo "💡 Führe 'make setup' aus"; \
		exit 1; \
	fi
	@cd $(BACKEND_DIR) && TENANT_ID=root ../$(VENV_DIR)/bin/python main.py

# TUB tenant (TU Berlin red branding)  
dev-tub:
	@echo "🔴 Starte StudentVC (TU Berlin Tenant)..."
	@echo "🏛️  Tenant: TUB (TU Berlin Red)"
	@echo "💾 Database: Isolated TUB Tenant Database"
	@pkill -f "python.*main.py" 2>/dev/null || true
	@make kill-port
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "❌ Virtuelle Umgebung nicht gefunden: $(VENV_DIR)"; \
		echo "💡 Führe 'make setup' aus"; \
		exit 1; \
	fi
	@cd $(BACKEND_DIR) && TENANT_ID=tub ../$(VENV_DIR)/bin/python main.py

# FUB tenant (FU Berlin green branding)
dev-fub:
	@echo "🟢 Starte StudentVC (FU Berlin Tenant)..."
	@echo "🏛️  Tenant: FUB (FU Berlin Green)"
	@echo "💾 Database: Isolated FUB Tenant Database"
	@pkill -f "python.*main.py" 2>/dev/null || true
	@make kill-port
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "❌ Virtuelle Umgebung nicht gefunden: $(VENV_DIR)"; \
		echo "💡 Führe 'make setup' aus"; \
		exit 1; \
	fi
	@cd $(BACKEND_DIR) && TENANT_ID=fub ../$(VENV_DIR)/bin/python main.py

# Hauptziel - startet die Entwicklungsumgebung mit test_env (defaults to root tenant)
dev:
	@echo "🔍 Vergewissere mich, dass port 8080 frei ist..."
	@pkill -f "python.*main.py" 2>/dev/null || true
	@make kill-port
	@echo "🚀 Starte die BBS Core Backend Anwendung..."
	@echo "📍 Arbeitsverzeichnis: $(BACKEND_DIR)"
	@echo "🐍 Python-Umgebung: test_env"
	@echo "🔒 HTTPS-Port: $(PORT) auf Host $(HOST)"
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "❌ Virtuelle Umgebung nicht gefunden: $(VENV_DIR)"; \
		echo "💡 Führe 'make setup' aus"; \
		exit 1; \
	fi
	@# Aktiviere die test_env Umgebung
	@source $(VENV_DIR)/bin/activate || echo "⚠️ Konnte test_env nicht aktivieren, aber das ist nicht schlimm"
	@echo "🐝 Verwende Python von: $(VENV_DIR)/bin/python"
	@cd $(BACKEND_DIR) && ../$(VENV_DIR)/bin/python main.py

# Tötet Prozesse auf Port 8080 falls belegt
kill-port:
	@echo "🔍 Prüfe Port $(PORT)..."
	@if lsof -ti :$(PORT) > /dev/null 2>&1 || pgrep -f "[p]ython.*main.py" > /dev/null 2>&1; then \
		echo "⚠️  Port $(PORT) ist belegt. Beende laufende Prozesse..."; \
		lsof -ti :$(PORT) | xargs kill -9 2>/dev/null || true; \
		pkill -f "python.*main.py" 2>/dev/null || true; \
		sleep 1; \
		echo "✅ Port $(PORT) ist jetzt frei."; \
	else \
		echo "✅ Port $(PORT) ist bereits frei."; \
	fi

# Installiert Dependencies in der test_env virtuellen Umgebung
install:
	@echo "📦 Installiere Dependencies in der virtuellen Umgebung $(VENV_DIR)..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "❌ Virtuelle Umgebung nicht gefunden: $(VENV_DIR)"; \
		echo "💡 Führe 'make setup' aus"; \
		exit 1; \
	fi
	@$(PIP) install -r $(BACKEND_DIR)/requirements.txt

# Setup: Benutze oder erstelle die test_env virtuelle Umgebung und installiere Dependencies
setup:
	@echo "📦 Setup der virtuellen Umgebung..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "🔧 Erstelle virtuelle Umgebung: $(VENV_DIR)"; \
		python3 -m venv $(VENV_DIR); \
	fi
	@echo "⬆️  Upgrade pip in virtueller Umgebung..."
	@$(PIP) install --upgrade pip
	@echo "📦 Installiere Backend Dependencies..."
	@$(PIP) install -r $(BACKEND_DIR)/requirements.txt

# Bereinigt die Umgebung
clean:
	@echo "🧹 Bereinige Umgebung..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@if [ -f "$(BACKEND_DIR)/instance/database.db" ]; then \
		rm "$(BACKEND_DIR)/instance/database.db"; \
		echo "🗑️  Database gelöscht"; \
	fi

# Zeigt Hilfe an
help:
	@echo "🛠️  Verfügbare Befehle:"
	@echo "  make dev      - Startet die Anwendung auf Port 8080 (HTTPS) mit test_env"
	@echo "  make dev-root - Startet ROOT tenant (Default StudentVC branding)"
	@echo "  make dev-tub  - Startet TUB tenant (TU Berlin red branding)"
	@echo "  make dev-fub  - Startet FUB tenant (FU Berlin green branding)"
	@echo "  make setup    - Aktualisiert pip und installiert Dependencies in test_env"
	@echo "  make install  - Installiert Dependencies in der test_env Umgebung"
	@echo "  make clean    - Bereinigt Cache und Database"
	@echo "  make kill-port- Beendet Prozesse auf Port 8080"
	@echo "  make test     - Führt alle Tests in der test_env Umgebung aus"
	@echo "  make setup-test- Installiert zusätzliche Pakete für Tests in test_env"
	@echo "  make help     - Zeigt diese Hilfe an"
