# Развёртывание NBank в Kubernetes (Minikube + Helm)

UI-тесты в проекте запускаются **локально через Playwright**; в кластере разворачиваются только приложение и БД.

## Быстрый старт

Bash:

```bash
cd infra/kube
bash restart_kube.sh
```

## Архитектура

Helm chart `nbank-chart` разворачивает три компонента:

| Компонент | Deployment | Service type | Назначение |
|-----------|------------|--------------|------------|
| PostgreSQL | `postgres` | ClusterIP | База данных для backend |
| Backend | `backend` | NodePort | REST API (Spring Boot) |
| Frontend | `frontend` | NodePort | UI (nginx) |

## Сервисы и порты

| Сервис | Внутренний порт (Service → Pod) | Внешний NodePort (Minikube IP) | `kubectl port-forward` (localhost) |
|--------|----------------------------------|--------------------------------|-------------------------------------|
| **Backend** | 4111 | 30411 | `4111:4111` → `http://localhost:4111` |
| **Frontend** | 80 | 30000 | `3000:80` → `http://localhost:3000` |
| **Postgres** | 5432 | — (только внутри кластера) | `5432:5432` (при необходимости) |

NodePort доступен по адресу `$(minikube ip):<nodePort>` (например, frontend: `http://<minikube-ip>:30000`).

## Установка через Helm

```bash
minikube start
helm upgrade --install nbank ./nbank-chart --wait --timeout 10m
kubectl get svc
kubectl get pods
```

## Список подов

```bash
kubectl get pods -o wide
```

Ожидаемые поды:

- `postgres-*` — Running
- `backend-*` — Running
- `frontend-*` — Running

## Логи сервисов

```bash
kubectl logs deployment/postgres --tail=50
kubectl logs deployment/backend --tail=50
kubectl logs deployment/frontend --tail=50
```

При ошибках: `kubectl describe pod <pod-name>`.

## Проброс портов (`kubectl port-forward`)

В **отдельных** терминалах:

```bash
kubectl port-forward svc/frontend 3000:80
kubectl port-forward svc/backend 4111:4111
```

Проверка:

- Frontend: http://localhost:3000
- Backend health: http://localhost:4111/actuator/health

## Secret `postgres-secret`

Хранит `POSTGRES_PASSWORD` (значение в `values.yaml` → `secrets.postgresPassword`).

Backend и Postgres используют `secretKeyRef`:

```bash
kubectl describe secret postgres-secret
```

## Проверка через kubectl

```bash
kubectl get svc
kubectl get pods
kubectl get deployments
kubectl logs deployment/backend
kubectl describe svc backend
```

## Масштабирование (реплики)

```bash
kubectl scale deployment/backend --replicas=2
kubectl get pods -l app=backend
kubectl scale deployment/frontend --replicas=2
kubectl get pods -l app=frontend
```


## Удаление

```bash
helm uninstall nbank
minikube stop
```
