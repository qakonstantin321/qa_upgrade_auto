#!/usr/bin/env bash

COMPOSE_FILE_PATH="infra/docker-compose/docker-compose.yaml"
IMAGE_NAME="autotests"
TAG="v1.0.0"
IMAGE_FULL="${IMAGE_NAME}:${TAG}"
HOST_BASE_URL="http://localhost:4111"
HOST_UI_BASE_URL="http://localhost:3000"
DOCKER_BASE_URL="http://backend:4111"
DOCKER_UI_BASE_URL="http://frontend"

# Цвет шрифта
RED='\033[31m' # красный
NC='\033[0m'   # сброс цвета

cleanup() {
  echo -e "${RED}Останавливаю окружение (docker-compose down)...${NC}"
  docker compose -f "${COMPOSE_FILE_PATH}" down || true
}

 trap cleanup EXIT # вызовется cleanup даже если тесты завершились с ошибкой

echo -e "${RED}Поднимаю окружение через docker-compose...${NC}"
docker compose -f "${COMPOSE_FILE_PATH}" up -d

echo -e "${RED}Жду готовности backend...${NC}"
SECONDS=0
until curl -sf "${HOST_BASE_URL}/actuator/health" >/dev/null 2>&1; do
  sleep 20
  if [ "$SECONDS" -ge 400 ]; then
    echo -e "${RED}Backend не поднялся за 400 секунд. Прерываю запуск тестов.${NC}"
    exit 1
  fi
  echo -e "${RED}Backend ещё не готов, healthcheck недоступен...${NC}"
done

echo -e "${RED}Собираю docker-образ ${IMAGE_FULL} с тестами...${NC}"
docker build -t "${IMAGE_FULL}" .

echo -e "${RED}Запускаю тесты в контейнере...${NC}"
echo -e "${RED}BASE_URL=${HOST_BASE_URL}${NC}"
echo -e "${RED}UI_BASE_URL=${HOST_UI_BASE_URL}${NC}"
docker run --rm \
  -p 8080:8080 \
  --network docker-compose_nbank-network \
  -e BASE_URL="${DOCKER_BASE_URL}" \
  -e UI_BASE_URL="${DOCKER_UI_BASE_URL}" \
  "${IMAGE_FULL}"
