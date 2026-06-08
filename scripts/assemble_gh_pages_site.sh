#!/usr/bin/env bash
# Собирает каталог для actions-gh-pages: test-report/<run>/allure-report и swagger-coverage.
# Запуск из корня репозитория:
#   scripts/assemble_gh_pages_site.sh <GITHUB_RUN_NUMBER> [output-dir]
# Пример:
#   scripts/assemble_gh_pages_site.sh 42 gh-pages-site
set -euo pipefail

RUN="${1:?GitHub run number (e.g. GITHUB_RUN_NUMBER)}"
SITE="${2:-gh-pages-site}"

mkdir -p "${SITE}/test-report/${RUN}/allure-report"
mkdir -p "${SITE}/test-report/${RUN}/swagger-coverage/widgets"

if [[ -d "allure-history/${RUN}" ]] && [[ -f "allure-history/${RUN}/index.html" ]]; then
  cp -r "allure-history/${RUN}/." "${SITE}/test-report/${RUN}/allure-report/"
elif [[ -f "allure-history/index.html" ]]; then
  cp -r allure-history/. "${SITE}/test-report/${RUN}/allure-report/"
else
  echo "Warning: Allure index not found; writing placeholder."
  echo '<!DOCTYPE html><html><body><p>Allure report unavailable for this run.</p></body></html>' \
    > "${SITE}/test-report/${RUN}/allure-report/index.html"
fi

if [[ -f target/swagger-coverage-report.html ]]; then
  cp target/swagger-coverage-report.html "${SITE}/test-report/${RUN}/swagger-coverage/index.html"
else
  echo '<!DOCTYPE html><html><body><p>Swagger coverage HTML missing.</p></body></html>' \
    > "${SITE}/test-report/${RUN}/swagger-coverage/index.html"
fi

if [[ -f target/swagger-coverage-metrics.json ]]; then
  cp target/swagger-coverage-metrics.json "${SITE}/test-report/${RUN}/swagger-coverage/widgets/coverage.json"
else
  echo '{"coverage_percent":0,"error":true}' > "${SITE}/test-report/${RUN}/swagger-coverage/widgets/coverage.json"
fi

if [[ -d target/swagger-coverage-output ]]; then
  mkdir -p "${SITE}/test-report/${RUN}/swagger-coverage/raw-calls"
  cp -r target/swagger-coverage-output/. "${SITE}/test-report/${RUN}/swagger-coverage/raw-calls/" 2>/dev/null || true
fi

cat > "${SITE}/index.html" << EOF
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta http-equiv="refresh" content="0; url=./test-report/${RUN}/allure-report/index.html" />
  <title>Test reports</title>
</head>
<body>
  <p><a href="./test-report/${RUN}/allure-report/index.html">Allure — run ${RUN}</a></p>
  <p><a href="./test-report/${RUN}/swagger-coverage/index.html">Swagger API coverage — run ${RUN}</a></p>
</body>
</html>
EOF

ALLURE_IDX="${SITE}/test-report/${RUN}/allure-report/index.html"
if [[ -f "$ALLURE_IDX" ]]; then
  sed -i 's|</body>|<div style="position:fixed;bottom:16px;right:16px;z-index:9999"><a href="../swagger-coverage/index.html" target="_blank" style="background:#4CAF50;color:#fff;padding:10px 16px;text-decoration:none;border-radius:6px;font-family:sans-serif">API coverage</a></div></body>|' "$ALLURE_IDX"
fi

echo "Assembled GitHub Pages bundle: ${SITE}/ (run ${RUN})"
