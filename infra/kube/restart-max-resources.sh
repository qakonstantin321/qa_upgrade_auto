#!/usr/bin/env bash
# Max resources for ~16 GB RAM PC:
#   Docker Desktop Memory: 10240 MB (10 GB) — set manually first, then restart Docker
#   Minikube: 8192 MB, 4 CPUs
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Step 0: Docker Desktop -> Settings -> Resources -> Memory: 10240 MB -> Apply & Restart"
read -r -p "Press Enter when Docker is restarted..."

echo "==> Recreate Minikube with 8 GB RAM"
minikube stop 2>/dev/null || true
minikube delete
minikube config set memory 8192
minikube config set cpus 4
minikube start --memory=8192 --cpus=4

echo "==> Deploy nbank"
helm upgrade --install nbank "${SCRIPT_DIR}/nbank-chart" --wait --timeout 20m

echo "==> Deploy logging"
bash "${SCRIPT_DIR}/install-logging.sh"

echo "==> Deploy monitoring"
bash "${SCRIPT_DIR}/install-monitoring.sh"

echo "==> Status"
kubectl get pods -A
helm list -A
