"""
Swagger Coverage для Python
Аналог Java-библиотеки swagger-coverage-rest-assured
"""
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

import requests

_REAL_SESSION_REQUEST = requests.Session.request


class SwaggerCoverage:
    """Сборщик покрытия API на основе Swagger/OpenAPI"""

    def __init__(self, output_dir: str = "target/swagger-coverage-output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.calls: List[Dict] = []
        self._patched = False
        self._patch_requests()

    def _patch_requests(self):
        """Перехватывает все HTTP запросы через requests library"""
        if self._patched:
            return

        original_request = _REAL_SESSION_REQUEST

        def patched_request(session, method, url, *args, **kwargs):
            request_body = kwargs.get('json') or kwargs.get('data')
            params = kwargs.get('params', {})

            response = original_request(session, method, url, *args, **kwargs)

            self.add_call(
                method=method,
                url=url,
                status_code=response.status_code,
                request_body=request_body,
                response_body=self._safe_parse_json(response.text),
                query_params=params,
                headers=kwargs.get('headers', {})
            )

            return response

        requests.Session.request = patched_request
        self._patched = True

    def _safe_parse_json(self, text: str) -> Optional[Dict]:
        """Безопасно парсит JSON из ответа"""
        try:
            return json.loads(text) if text else None
        except:
            return None

    def add_call(self, method: str, url: str, status_code: int = None,
                 request_body: Dict = None, response_body: Dict = None,
                 query_params: Dict = None, path_params: Dict = None,
                 headers: Dict = None):
        """Логирует вызов API"""
        clean_url = self._clean_url(url)
        clean_path = self._normalize_path(clean_url)

        call_data = {
            "method": method.upper(),
            "path": clean_path,
            "originalUrl": url,
            "timestamp": datetime.now().isoformat(),
            "statusCode": status_code,
            "requestBody": request_body,
            "responseBody": response_body,
            "queryParams": query_params or {},
            "pathParams": path_params or {},
            "headers": headers or {}
        }
        self.calls.append(call_data)
        self._save_call(call_data)

    def _clean_url(self, url: str) -> str:
        """Очищает URL от базового хоста и порта; отрезает query (в OpenAPI путь без ?…)."""
        url = re.sub(r'^https?://[^/]+', '', url)
        q = url.find("?")
        if q >= 0:
            url = url[:q]
        return url if url else "/"

    def _normalize_path(self, path: str) -> str:
        """Нормализует путь, заменяя динамические ID на шаблоны"""
        # Заменяем числовые ID на {id}
        path = re.sub(r'/\d+', '/{id}', path)
        # Заменяем UUID на {uuid}
        path = re.sub(
            r'/[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}',
            '/{uuid}',
            path,
        )
        # Заменяем хэши на {hash}
        path = re.sub(r'/[a-f0-9]{32,}', '/{hash}', path)
        return path

    def _save_call(self, call_data: Dict):
        """Сохраняет вызов в файл"""
        safe_path = re.sub(r'[^\w\-_]', '_', call_data['path'])
        file_path = self.output_dir / f"call_{call_data['timestamp'].replace(':', '-')}_{call_data['method']}_{safe_path}.json"
        with open(file_path, 'w') as f:
            json.dump(call_data, f, indent=2)

    def generate_report(self, swagger_url: str) -> Dict:
        """Генерирует отчет о покрытии"""
        try:
            req = urllib.request.Request(swagger_url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                swagger_spec = json.loads(resp.read().decode())
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as e:
            print(f"⚠️ Failed to load swagger spec from {swagger_url}: {e}")
            cov = self._empty_coverage()
            cov["error_detail"] = str(e)
            self._generate_html_report(cov, {})
            self._write_metrics_json(cov, swagger_url)
            return cov

        expected_endpoints = self._extract_endpoints_from_swagger(swagger_spec)
        actual_endpoints = self._extract_actual_endpoints()
        coverage = self._analyze_coverage(expected_endpoints, actual_endpoints)
        self._generate_html_report(coverage, swagger_spec)
        self._write_metrics_json(coverage, swagger_url)

        return coverage

    def _empty_coverage(self) -> Dict:
        """Возвращает пустой отчет при ошибке"""
        try:
            actual_from_disk = sum(
                1 for _ in self.output_dir.glob("call_*.json")
            )
        except OSError:
            actual_from_disk = len(self.calls)
        return {
            'total': 0,
            'covered': 0,
            'uncovered': 0,
            'coverage_percent': 0,
            'uncovered_endpoints': {},
            'covered_endpoints': {},
            'actual_calls': actual_from_disk,
            'error': True
        }

    def _extract_endpoints_from_swagger(self, swagger_spec: Dict) -> Dict:
        """Извлекает все эндпоинты из Swagger спецификации"""
        endpoints = {}
        paths = swagger_spec.get('paths', {})

        for path, methods in paths.items():
            for method, details in methods.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                    key = f"{method.upper()} {path}"
                    endpoints[key] = {
                        'method': method.upper(),
                        'path': path,
                        'summary': details.get('summary', ''),
                        'description': details.get('description', ''),
                        'parameters': details.get('parameters', []),
                        'requestBody': details.get('requestBody', {}),
                        'responses': details.get('responses', {})
                    }
        return endpoints

    def _extract_actual_endpoints(self) -> Dict[str, List[Dict]]:
        """Извлекает реально вызванные эндпоинты из сохраненных данных"""
        endpoints = {}
        for file_path in self.output_dir.glob("call_*.json"):
            try:
                with open(file_path, 'r') as f:
                    call = json.load(f)
                    key = f"{call['method']} {call['path']}"
                    if key not in endpoints:
                        endpoints[key] = []
                    endpoints[key].append(call)
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")
        return endpoints

    def _analyze_coverage(self, expected: Dict, actual: Dict[str, List[Dict]]) -> Dict:
        """Анализирует покрытие API"""
        total = len(expected)
        strictly_covered = set(expected.keys()) & set(actual.keys())

        partially_covered = set()
        for exp_key in expected.keys():
            exp_method, exp_path = exp_key.split(' ', 1)
            for act_key in actual.keys():
                act_method, act_path = act_key.split(' ', 1)
                if exp_method == act_method and self._paths_match(exp_path, act_path):
                    partially_covered.add(exp_key)
                    break

        covered = strictly_covered | partially_covered
        covered_count = len(covered)
        coverage_percent = (covered_count / total * 100) if total > 0 else 0

        uncovered = {k: v for k, v in expected.items() if k not in covered}
        covered_details = {k: expected[k] for k in expected.keys() if k in covered}

        for key in covered_details:
            if key in actual:
                covered_details[key]['call_count'] = len(actual[key])
                covered_details[key]['status_codes'] = list(
                    set(c.get('statusCode') for c in actual[key] if c.get('statusCode')))

        return {
            'total': total,
            'covered': covered_count,
            'uncovered': total - covered_count,
            'coverage_percent': coverage_percent,
            'uncovered_endpoints': uncovered,
            'covered_endpoints': covered_details,
            'actual_calls': sum(len(calls) for calls in actual.values())
        }

    def _paths_match(self, swagger_path: str, actual_path: str) -> bool:
        """Проверяет соответствие пути из swagger с реальным вызовом"""
        pattern = re.sub(r'\{[^}]+\}', r'[^/]+', swagger_path)
        pattern = f"^{pattern}$"
        return bool(re.match(pattern, actual_path))

    def _generate_html_report(self, coverage: Dict, swagger_spec: Dict):
        """Генерирует HTML отчет"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        err_detail = coverage.get("error_detail") or ""
        error_block = ""
        if coverage.get("error") and err_detail:
            safe = err_detail.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            error_block = f'<div style="background:#ffebee;border-left:4px solid #f44336;padding:12px 16px;margin-bottom:16px;border-radius:8px;color:#333;"><strong>Не удалось загрузить OpenAPI</strong><br/><span style="font-size:13px;">{safe}</span></div>'

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Swagger API Coverage Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .card {{ 
            background: white; 
            border-radius: 12px; 
            padding: 24px; 
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #333; margin-bottom: 8px; font-size: 28px; }}
        .timestamp {{ color: #666; margin-bottom: 20px; font-size: 14px; }}
        .summary {{ 
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }}
        .stat-number {{ font-size: 36px; font-weight: bold; }}
        .stat-label {{ font-size: 14px; opacity: 0.9; margin-top: 8px; }}
        .coverage-bar {{ 
            background: #e0e0e0; 
            height: 40px; 
            border-radius: 20px; 
            overflow: hidden; 
            margin: 20px 0;
        }}
        .coverage-fill {{ 
            background: linear-gradient(90deg, #4CAF50, #8BC34A);
            height: 100%; 
            color: white; 
            text-align: center; 
            line-height: 40px;
            font-weight: bold;
            transition: width 0.5s ease;
        }}
        .section-title {{
            font-size: 20px;
            margin: 20px 0 15px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #e0e0e0;
        }}
        .endpoint {{ 
            margin: 10px 0; 
            padding: 15px; 
            border-left: 4px solid;
            border-radius: 8px;
            transition: transform 0.2s;
        }}
        .endpoint:hover {{ transform: translateX(5px); }}
        .covered {{ 
            border-left-color: #4CAF50; 
            background: #f0fff0;
        }}
        .uncovered {{ 
            border-left-color: #f44336; 
            background: #fff0f0;
        }}
        .method {{ 
            display: inline-block; 
            padding: 4px 10px; 
            border-radius: 6px; 
            font-weight: bold; 
            margin-right: 12px;
            font-size: 12px;
        }}
        .GET {{ background: #61affe; color: white; }}
        .POST {{ background: #49cc90; color: white; }}
        .PUT {{ background: #fca130; color: white; }}
        .DELETE {{ background: #f93e3e; color: white; }}
        .PATCH {{ background: #50e3c2; color: white; }}
        .path {{ font-family: 'Courier New', monospace; font-size: 14px; }}
        .summary-text {{ color: #666; margin-left: 12px; font-size: 13px; }}
        .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            margin-left: 10px;
        }}
        .badge-success {{ background: #4CAF50; color: white; }}
        .badge-danger {{ background: #f44336; color: white; }}
        .filter-buttons {{
            margin: 20px 0;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .filter-btn {{
            padding: 8px 16px;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            background: #f0f0f0;
            transition: all 0.3s;
        }}
        .filter-btn.active {{
            background: #667eea;
            color: white;
        }}
        .hidden {{ display: none; }}
        .call-stats {{
            font-size: 12px;
            color: #666;
            margin-top: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>📊 Swagger API Coverage Report</h1>
            <div class="timestamp">Generated: {timestamp}</div>
            {error_block}
            
            <div class="summary">
                <div class="stat-card">
                    <div class="stat-number">{coverage['total']}</div>
                    <div class="stat-label">Total Endpoints</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{coverage['covered']}</div>
                    <div class="stat-label">Covered</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{coverage['uncovered']}</div>
                    <div class="stat-label">Uncovered</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{coverage['actual_calls']}</div>
                    <div class="stat-label">Actual API Calls</div>
                </div>
            </div>
            
            <div class="coverage-bar">
                <div class="coverage-fill" style="width: {coverage['coverage_percent']}%">
                    {coverage['coverage_percent']:.1f}% Coverage
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="filter-buttons">
                <button class="filter-btn active" data-filter="all">All ({coverage['total']})</button>
                <button class="filter-btn" data-filter="covered">✅ Covered ({coverage['covered']})</button>
                <button class="filter-btn" data-filter="uncovered">❌ Uncovered ({coverage['uncovered']})</button>
            </div>
            
            <div id="endpoints-container">
                <div class="section-title">✅ Covered Endpoints</div>
                <div id="covered-endpoints">
"""

        for endpoint, details in coverage['covered_endpoints'].items():
            method, path = endpoint.split(' ', 1)
            call_info = f"<div class='call-stats'>📞 Called {details.get('call_count', 1)} time(s) | Status codes: {', '.join(str(c) for c in details.get('status_codes', []))}</div>" if details.get(
                'call_count') else ""
            html += f"""
                    <div class="endpoint covered" data-type="covered">
                        <span class="method {method}">{method}</span>
                        <code class="path">{path}</code>
                        <span class="summary-text">{details.get('summary', '')}</span>
                        {call_info}
                    </div>
"""

        html += f"""
                </div>
                
                <div class="section-title">❌ Uncovered Endpoints</div>
                <div id="uncovered-endpoints">
"""

        for endpoint, details in coverage['uncovered_endpoints'].items():
            method, path = endpoint.split(' ', 1)
            html += f"""
                    <div class="endpoint uncovered" data-type="uncovered">
                        <span class="method {method}">{method}</span>
                        <code class="path">{path}</code>
                        <span class="summary-text">{details.get('summary', '')}</span>
                    </div>
"""

        html += """
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const filterBtns = document.querySelectorAll('.filter-btn');
        const allEndpoints = document.querySelectorAll('.endpoint');
        
        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const filter = btn.dataset.filter;
                
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                allEndpoints.forEach(endpoint => {
                    if (filter === 'all') {
                        endpoint.classList.remove('hidden');
                    } else if (filter === 'covered' && endpoint.classList.contains('covered')) {
                        endpoint.classList.remove('hidden');
                    } else if (filter === 'uncovered' && endpoint.classList.contains('uncovered')) {
                        endpoint.classList.remove('hidden');
                    } else {
                        endpoint.classList.add('hidden');
                    }
                });
            });
        });
    </script>
</body>
</html>
"""

        report_path = self.output_dir.parent / "swagger-coverage-report.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ Swagger Coverage отчет сохранен: {report_path}")
        return report_path

    def _write_metrics_json(self, coverage: Dict, swagger_url: str) -> Path:
        """Метрики для CI / jq (target/swagger-coverage-metrics.json)."""
        metrics_path = self.output_dir.parent / "swagger-coverage-metrics.json"
        pct = float(coverage.get("coverage_percent") or 0)
        payload = {
            "coverage_percent": round(pct, 2),
            "total_endpoints": int(coverage.get("total") or 0),
            "covered_endpoints": int(coverage.get("covered") or 0),
            "uncovered_endpoints": int(coverage.get("uncovered") or 0),
            "actual_calls": int(coverage.get("actual_calls") or 0),
            "error": bool(coverage.get("error", False)),
            "swagger_url": swagger_url,
        }
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
            f.write("\n")
        print(f"✅ Swagger Coverage metrics: {metrics_path}")
        return metrics_path


_swagger_coverage_instance = None


def get_swagger_coverage():
    """Возвращает глобальный экземпляр SwaggerCoverage"""
    global _swagger_coverage_instance
    if _swagger_coverage_instance is None:
        _swagger_coverage_instance = SwaggerCoverage()
    return _swagger_coverage_instance


def reset_swagger_coverage():
    """Сбрасывает глобальный экземпляр (для использования между тестами)"""
    global _swagger_coverage_instance
    _swagger_coverage_instance = None
