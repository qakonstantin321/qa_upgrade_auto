#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts 2>/dev/null || true
helm repo update

helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace \
  -f "${SCRIPT_DIR}/monitoring-values.yaml" \
  --wait --timeout 15m

kubectl apply -f "${SCRIPT_DIR}/backend-basic-auth-secret.yaml"
kubectl apply -f "${SCRIPT_DIR}/spring-monitoring.yaml"

echo "==> ServiceMonitors"
kubectl get servicemonitor -n monitoring

echo "==> Grafana: kubectl port-forward -n monitoring svc/monitoring-grafana 3030:80"
echo "    login: admin / admin"
