#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAMESPACE="${LOGGING_NAMESPACE:-logging}"
# Kibana 8.x pre-install hook needs HTTPS + ES security; 7.17.3 works with HTTP on Minikube.
STACK_VERSION="${ELASTIC_STACK_VERSION:-7.17.3}"

helm repo add elastic https://helm.elastic.co 2>/dev/null || true
helm repo update

kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

# Clean failed Kibana 8.x install (pre-install job loop).
helm uninstall kibana -n "${NAMESPACE}" 2>/dev/null || true
kubectl delete job -n "${NAMESPACE}" -l job-name=pre-install-kibana-kibana --ignore-not-found 2>/dev/null || true

# After a failed 8.x attempt, reset once: RESET_LOGGING=1 bash install-logging.sh
if [ "${RESET_LOGGING:-}" = "1" ]; then
  helm uninstall filebeat kibana elasticsearch -n "${NAMESPACE}" 2>/dev/null || true
  kubectl delete job -n "${NAMESPACE}" --all --ignore-not-found 2>/dev/null || true
  kubectl wait --for=delete pod -n "${NAMESPACE}" -l app=elasticsearch-master --timeout=120s 2>/dev/null || true
  kubectl delete pod -n "${NAMESPACE}" -l app=elasticsearch-master --force --grace-period=0 2>/dev/null || true
  kubectl delete pvc -n "${NAMESPACE}" -l app=elasticsearch-master --ignore-not-found 2>/dev/null || true
  sleep 10
fi

helm upgrade --install elasticsearch elastic/elasticsearch \
  --version "${STACK_VERSION}" \
  -n "${NAMESPACE}" \
  -f "${SCRIPT_DIR}/elasticsearch-values.yaml" \
  --wait --timeout 15m

helm upgrade --install kibana elastic/kibana \
  --version "${STACK_VERSION}" \
  -n "${NAMESPACE}" \
  -f "${SCRIPT_DIR}/kibana-values.yaml" \
  --wait --timeout 15m

helm upgrade --install filebeat elastic/filebeat \
  --version "${STACK_VERSION}" \
  -n "${NAMESPACE}" \
  -f "${SCRIPT_DIR}/filebeat-values.yaml" \
  --wait --timeout 15m

echo "==> Pods in ${NAMESPACE}"
kubectl get pods -n "${NAMESPACE}"

echo "==> Kibana: kubectl port-forward -n ${NAMESPACE} svc/kibana-kibana 5601:5601"
echo "    Index pattern: filebeat-*"
