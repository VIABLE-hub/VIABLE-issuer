#!/bin/bash
# Start all tenants on different ports

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_DIR/backend"
VENV_DIR="$PROJECT_DIR/test_env"
LOGS_DIR="$PROJECT_DIR/logs"

# Create logs directory
mkdir -p "$LOGS_DIR"

# Kill existing servers - MORE AGGRESSIVE
echo "🔄 Stopping any existing servers..."
echo "   Killing processes on port 8080..."
lsof -ti:8080 2>/dev/null | xargs kill -9 2>/dev/null || true
sleep 0.5
echo "   Killing processes on port 8081..."
lsof -ti:8081 2>/dev/null | xargs kill -9 2>/dev/null || true
sleep 0.5
echo "   Killing processes on port 8082..."
lsof -ti:8082 2>/dev/null | xargs kill -9 2>/dev/null || true
sleep 0.5
echo "   Killing processes on port 8083..."
lsof -ti:8083 2>/dev/null | xargs kill -9 2>/dev/null || true
sleep 1

# Also kill any Python processes running main.py
echo "   Killing any remaining Python main.py processes..."
pkill -9 -f "python.*main.py" 2>/dev/null || true
sleep 2

# Verify ports are free
echo "   Verifying ports are free..."
if lsof -i:8080 >/dev/null 2>&1; then
    echo "   ⚠️  WARNING: Port 8080 still in use!"
fi
if lsof -i:8081 >/dev/null 2>&1; then
    echo "   ⚠️  WARNING: Port 8081 still in use!"
fi
if lsof -i:8082 >/dev/null 2>&1; then
    echo "   ⚠️  WARNING: Port 8082 still in use!"
fi
if lsof -i:8083 >/dev/null 2>&1; then
    echo "   ⚠️  WARNING: Port 8083 still in use!"
fi
echo "   ✓ Port cleanup complete"

echo ""
echo "🚀 Starting tenants..."
echo ""

# Start Veritas on 8080
cd "$BACKEND_DIR"
TENANT_ID=veritas SERVER_PORT=8080 nohup "$VENV_DIR/bin/python" main.py > "$LOGS_DIR/veritas.log" 2>&1 &
VERITAS_PID=$!
echo "✅ VERITAS starting on port 8080 (PID: $VERITAS_PID)"
sleep 5

# Verify Veritas started
if lsof -i:8080 >/dev/null 2>&1; then
    echo "   ✓ Veritas is listening on 8080"
else
    echo "   ⚠️  Veritas may not have started - check logs/veritas.log"
fi

# Start TUB on 8081
cd "$BACKEND_DIR"
TENANT_ID=tub SERVER_PORT=8081 nohup "$VENV_DIR/bin/python" main.py > "$LOGS_DIR/tub.log" 2>&1 &
TUB_PID=$!
echo "✅ TUB     starting on port 8081 (PID: $TUB_PID)"
sleep 5

# Verify TUB started
if lsof -i:8081 >/dev/null 2>&1; then
    echo "   ✓ TUB is listening on 8081"
else
    echo "   ⚠️  TUB may not have started - check logs/tub.log"
fi

# Start FUB on 8082
cd "$BACKEND_DIR"
TENANT_ID=fub SERVER_PORT=8082 nohup "$VENV_DIR/bin/python" main.py > "$LOGS_DIR/fub.log" 2>&1 &
FUB_PID=$!
echo "✅ FUB     starting on port 8082 (PID: $FUB_PID)"
sleep 5

# Verify FUB started
if lsof -i:8082 >/dev/null 2>&1; then
    echo "   ✓ FUB is listening on 8082"
else
    echo "   ⚠️  FUB may not have started - check logs/fub.log"
fi

# Start ROOT on 8083
cd "$BACKEND_DIR"
TENANT_ID=root SERVER_PORT=8083 nohup "$VENV_DIR/bin/python" main.py > "$LOGS_DIR/root.log" 2>&1 &
ROOT_PID=$!
echo "✅ ROOT    starting on port 8083 (PID: $ROOT_PID)"
sleep 5

# Verify ROOT started
if lsof -i:8083 >/dev/null 2>&1; then
    echo "   ✓ ROOT is listening on 8083"
else
    echo "   ⚠️  ROOT may not have started - check logs/root.log"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                  ✅ ALL TENANTS RUNNING ✅                    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Access URLs:"
echo ""
echo "  🔵 VERITAS : https://localhost:8080/login  (Blue theme)"
echo "  🔴 TUB     : https://localhost:8081/login  (Red theme)"
echo "  🟢 FUB     : https://localhost:8082/login  (Green theme)"
echo "  ⚪ ROOT    : https://localhost:8083/login  (Default theme)"
echo ""
echo "📋 View Logs:"
echo ""
echo "  tail -f logs/veritas.log  # Veritas logs"
echo "  tail -f logs/tub.log      # TUB logs"
echo "  tail -f logs/fub.log      # FUB logs"
echo "  tail -f logs/root.log     # Root logs"
echo ""
echo "🛑 To stop all servers:"
echo ""
echo "  make stop-all"
echo ""
echo "📊 Check running servers:"
echo ""
echo "  lsof -i:8080  # Veritas"
echo "  lsof -i:8081  # TUB"
echo "  lsof -i:8082  # FUB"
echo "  lsof -i:8083  # ROOT"
echo ""

# Save PIDs for later
echo "$VERITAS_PID" > "$LOGS_DIR/veritas.pid"
echo "$TUB_PID" > "$LOGS_DIR/tub.pid"
echo "$FUB_PID" > "$LOGS_DIR/fub.pid"
echo "$ROOT_PID" > "$LOGS_DIR/root.pid"

echo "💡 Servers are running in the background. Check logs for any errors."
echo ""

