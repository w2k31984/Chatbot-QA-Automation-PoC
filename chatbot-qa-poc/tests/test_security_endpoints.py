# tests/test_security_endpoints.py
"""
Pruebas de seguridad de endpoints expuestos.
Cada test fallido representa un hallazgo de seguridad documentable en el SGSI.
"""
import requests
import pytest

BASE_URL = "http://localhost:5000"

def test_health_endpoint_disponible():
    """Control SGSI: A.8.1 - Disponibilidad del servicio. Debe responder."""
    r = requests.get(f"{BASE_URL}/health", timeout=10)
    assert r.status_code == 200, f"Health check falló: {r.status_code}"

def test_endpoint_database_no_expuesto():
    """
    HALLAZGO CRÍTICO (SGSI A.8.2 - Confidencialidad).
    El endpoint /api/database NO debe ser accesible sin autenticación.
    Si este test falla, expone PII, SSNs, tarjetas y credenciales.
    """
    r = requests.get(f"{BASE_URL}/api/database", timeout=10)
    assert r.status_code in (401, 403, 404), (
        f"VULNERABILIDAD CRÍTICA: /api/database accesible sin auth "
        f"(status={r.status_code}). Expone PII completa."
    )

def test_database_no_contiene_ssn_en_respuesta():
    """
    HALLAZGO CRÍTICO (SGSI A.8.2 - Minimización de datos).
    Si el endpoint responde, NO debe contener SSNs en formato válido.
    """
    r = requests.get(f"{BASE_URL}/api/database", timeout=10)
    if r.status_code == 200:
        body = r.text
        import re
        ssns = re.findall(r"\b\d{3}-\d{2}-\d{4}\b", body)
        assert not ssns, (
            f"FUGA DE PII: Se encontraron {len(ssns)} SSNs en /api/database: {ssns[:3]}"
        )

def test_database_no_contiene_credenciales():
    """
    HALLAZGO CRÍTICO (SGSI A.5.17 - Credenciales de autenticación).
    El endpoint no debe exponer contraseñas o tokens.
    """
    r = requests.get(f"{BASE_URL}/api/database", timeout=10)
    if r.status_code == 200:
        body = r.text.lower()
        patrones_prohibidos = ["password", "p@ssw0rd", "bearer eyj", "api_token"]
        encontrados = [p for p in patrones_prohibidos if p in body]
        assert not encontrados, (
            f"FUGA DE CREDENCIALES: se detectaron patrones {encontrados} en la respuesta"
        )