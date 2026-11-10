# Chatbot QA Automation PoC

Framework de automatización QA y seguridad para un chatbot vulnerable (PoC SGSI / OWASP LLM). Combina:

- **pytest** — pruebas funcionales y de seguridad (endpoints + prompts)
- **crucible-ai** — escaneo red-team (LLM01, LLM07, etc.)
- **vulnerable-chat** — chatbot de prueba (GitHub o imagen Docker)

> **Advertencia:** el chatbot incluye vulnerabilidades intencionales. Úsalo solo en entornos locales de prueba. No lo expongas a internet ni a datos reales.

---

## Estructura del repositorio

```
qa-automation-chatbot/
├── chatbot-qa-poc/          # Framework de automatización
│   ├── tests/               # Pruebas pytest
│   ├── conftest.py          # Metadata y severidad SGSI en reporte HTML
│   ├── scan.yaml            # Configuración de Crucible
│   ├── docker-compose.yml   # Levanta el chatbot con imagen Docker
│   ├── pytest.ini
│   ├── requirements.txt
│   └── reports/             # Reportes generados (pytest + crucible)
└── vulnerable-chat/         # Código fuente del chatbot (opcional)
```

---

## Requisitos

- Python 3.10+ (recomendado 3.12)
- Docker y Docker Compose
- `git`
- macOS / Linux / WSL

---

## 1. Clonar el proyecto

Si este repositorio ya está en GitHub:

```bash
git clone <URL_DE_ESTE_REPO>
cd qa-automation-chatbot
```

Si solo tienes el PoC local, trabaja desde la raíz del proyecto.

---

## 2. Levantar el chatbot de pruebas

El framework apunta a `http://localhost:5000`. Elige **una** de las dos opciones.

### Opción A — Imagen Docker (recomendada)

Usa la imagen publicada y el `docker-compose` del PoC:

```bash
cd chatbot-qa-poc
docker compose up -d
```

Esto descarga y ejecuta:

```yaml
image: cagricihamza/vulnerable-chat:latest
ports:
  - "5000:5000"
```

Verifica:

```bash
curl http://localhost:5000/health
```

Detener:

```bash
docker compose down
```

### Opción B — Desde el repositorio de GitHub

Clona el chatbot vulnerable y levántalo con Docker Compose:

```bash
git clone https://github.com/scthornton/vulnerable-chat.git
cd vulnerable-chat
cp .env.example .env
docker compose up -d --build
```

Por defecto el servicio escucha en el puerto del `docker-compose.yml` del chatbot.  
Si el host queda en **5001** (mapeo `5001:5000`), actualiza las URLs en:

- `chatbot-qa-poc/tests/*.py` → `BASE_URL`
- `chatbot-qa-poc/scan.yaml` → `target.url`

para usar `http://localhost:5001` en lugar de `5000`.

Verifica:

```bash
curl http://localhost:5000/health
# o http://localhost:5001/health según el mapeo
```

---

## 3. Instalar el framework de automatización

Desde la raíz del proyecto (o dentro de `chatbot-qa-poc`):

```bash
cd chatbot-qa-poc
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install crucible-ai
```

Dependencias principales (`requirements.txt`):

- `pytest`
- `pytest-html`
- `requests`

`crucible-ai` se instala aparte (red-teaming CLI).

---

## 4. Correr los tests (pytest)

Con el chatbot arriba y el venv activo:

```bash
cd chatbot-qa-poc
source .venv/bin/activate
mkdir -p reports
pytest
```

El `pytest.ini` genera automáticamente:

```text
reports/pytest-report.html
```

### Ejecutar suites específicas

```bash
# Solo funcional
pytest tests/test_functional_chat.py

# Solo endpoints de seguridad
pytest tests/test_security_endpoints.py

# Solo prompts de ataque
pytest tests/test_security_prompts.py
```

### Qué valida cada suite

| Archivo | Enfoque |
|---------|---------|
| `test_functional_chat.py` | Respuesta a consulta de saldo / no reflejo de DNI |
| `test_security_endpoints.py` | `/health`, exposición de `/api/database`, PII y credenciales |
| `test_security_prompts.py` | Prompts de `/api/test-prompts` vs fuga de SSN, password, system prompt, tarjetas |

Los fallos esperados en este PoC documentan hallazgos de seguridad (el chatbot es vulnerable a propósito).

---

## 5. Correr el escaneo Crucible

Configuración en `chatbot-qa-poc/scan.yaml`:

```yaml
target:
  provider: webhook
  url: "http://localhost:5000/api/chat"
  response_field: "response"

probes:
  categories:
    - LLM01  # Prompt Injection
    - LLM07  # System prompt / tool misuse
```

Ejecutar:

```bash
cd chatbot-qa-poc
source .venv/bin/activate
crucible scan -c scan.yaml -o reports --i-agree-to-tos
```

Opciones útiles:

```bash
# Validar config sin enviar payloads
crucible scan -c scan.yaml --dry-run --i-agree-to-tos

# Listar probes disponibles
crucible list-probes

# Estimar costo (si aplica)
crucible scan -c scan.yaml --estimate-cost --i-agree-to-tos
```

Reportes típicos en `reports/`:

- `scan.md`
- `scan.json`
- `scan.jsonl`

---

## Flujo rápido (resumen)

```bash
# 1) Chatbot (imagen Docker)
cd chatbot-qa-poc
docker compose up -d

# 2) Entorno Python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install crucible-ai

# 3) Tests pytest
mkdir -p reports
pytest

# 4) Escaneo Crucible
crucible scan -c scan.yaml -o reports --i-agree-to-tos
```

Abre el reporte HTML:

```bash
open reports/pytest-report.html   # macOS
# o xdg-open reports/pytest-report.html en Linux
```

---

## Troubleshooting

| Problema | Qué revisar |
|----------|-------------|
| `Connection refused` en pytest | El contenedor no está arriba o el puerto no es 5000 |
| Puerto ocupado | Cambia el mapeo en `docker-compose.yml` y alinea URLs de tests/`scan.yaml` |
| `crucible: command not found` | Activa el venv e instala `crucible-ai` |
| Imagen no arranca en Apple Silicon | El compose del PoC usa `platform: linux/amd64` |
| Healthcheck fallido | `docker logs vulnerable-ai-chatbot` y `curl http://localhost:5000/health` |

```bash
docker ps
docker logs vulnerable-ai-chatbot
docker compose -f chatbot-qa-poc/docker-compose.yml down
docker compose -f chatbot-qa-poc/docker-compose.yml up -d
```

---

## Referencias

- Chatbot vulnerable (código): [scthornton/vulnerable-chat](https://github.com/scthornton/vulnerable-chat)
- Imagen Docker: `cagricihamza/vulnerable-chat:latest`
- Crucible AI: [vbelmonte/crucible-ai](https://github.com/vbelmonte/crucible-ai)
- Marco de controles del reporte: ISO/IEC 27001:2022 (A.8.2, A.8.3, A.5.17, A.8.1) + OWASP LLM Top 10
