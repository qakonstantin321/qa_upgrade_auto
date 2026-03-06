#!/bin/bash
set -e # Прервать выполнение скрипта при ошибке

USERNAME="konstantinqa"
IMAGE="autotests"
TAG="${TAG:-v1.0.0}"

# Логин в Docker Hub (из переменных окружния, либо через командную строку: export DOCKERHUB_TOKEN="token")
echo "$DOCKERHUB_TOKEN" | docker login -u "$USERNAME" --password-stdin

docker tag "$IMAGE:$TAG" "$USERNAME/$IMAGE:$TAG"
docker push "$USERNAME/$IMAGE:$TAG"
echo "Для скачивания образа: docker pull $USERNAME/$IMAGE:$TAG"
