# Max resources for ~16 GB RAM PC:
#   Docker Desktop Memory: 10240 MB (10 GB) — set manually first, then restart Docker
#   Minikube: 8192 MB, 4 CPUs
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..\..")

Write-Host "==> Step 0: Ensure Docker Desktop Memory >= 10 GB (Settings -> Resources -> Apply & Restart)"
Write-Host "    Press Enter when Docker is restarted..."
Read-Host

Write-Host "==> Recreate Minikube with 8 GB RAM"
minikube stop 2>$null
minikube delete
minikube config set memory 8192
minikube config set cpus 4
minikube start --memory=8192 --cpus=4

Write-Host "==> Deploy nbank"
helm upgrade --install nbank (Join-Path $ScriptDir "nbank-chart") --wait --timeout 20m

Write-Host "==> Deploy logging"
bash (Join-Path $ScriptDir "install-logging.sh")

Write-Host "==> Deploy monitoring"
bash (Join-Path $ScriptDir "install-monitoring.sh")

Write-Host "==> Status"
kubectl get pods -A
helm list -A

Write-Host ""
Write-Host "Port-forwards:"
Write-Host "  kubectl port-forward svc/backend 4111:4111"
Write-Host "  kubectl port-forward svc/frontend 3000:80"
Write-Host "  kubectl port-forward -n monitoring svc/monitoring-grafana 3030:80"
Write-Host "  kubectl port-forward -n logging svc/kibana-kibana 5601:5601"
