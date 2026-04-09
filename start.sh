#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$ROOT/Backend"
FRONTEND="$ROOT/frontend"

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

if [[ "${1:-}" == "stop" ]]; then
    echo -e "${RED}Stopping AEGIS V3...${NC}"
    lsof -ti :8000 | xargs kill 2>/dev/null && echo "  Backend stopped" || echo "  Backend not running"
    lsof -ti :3000 | xargs kill 2>/dev/null && echo "  Frontend stopped" || echo "  Frontend not running"
    echo -e "${GREEN}Done.${NC}"
    exit 0
fi

lsof -ti :8000 | xargs kill 2>/dev/null || true
lsof -ti :3000 | xargs kill 2>/dev/null || true
sleep 1

echo -e "${CYAN}"
echo "  ╔═══════════════════════════════════════╗"
echo "  ║         AEGIS V3 — Starting           ║"
echo "  ╚═══════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${GREEN}[1/2] Starting Backend (port 8000)...${NC}"
cd "$BACKEND"
source .venv/bin/activate
uvicorn api.main:app --host 0.0.0.0 --port 8000 --log-level warning &
BACKEND_PID=$!
sleep 2

if curl -sf http://localhost:8000/api/health > /dev/null; then
    echo -e "  ${GREEN}✓ Backend healthy${NC}"
else
    echo -e "  ${RED}✗ Backend failed to start${NC}"
    exit 1
fi

echo -e "${GREEN}[2/2] Starting Frontend (port 3000)...${NC}"
cd "$FRONTEND"
npm run dev -- --port 3000 > /dev/null 2>&1 &
FRONTEND_PID=$!
sleep 3
echo -e "  ${GREEN}✓ Frontend ready${NC}"

echo ""
echo -e "${CYAN}  ╔═══════════════════════════════════════╗"
echo -e "  ║           AEGIS V3 — LIVE              ║"
echo -e "  ║                                         ║"
echo -e "  ║  Dashboard:  http://localhost:3000       ║"
echo -e "  ║  API Docs:   http://localhost:8000/docs  ║"
echo -e "  ║                                         ║"
echo -e "  ║  Stop:  ./start.sh stop                 ║"
echo -e "  ╚═══════════════════════════════════════╝${NC}"
echo ""

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
