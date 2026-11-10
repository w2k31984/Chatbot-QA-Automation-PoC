# tests/test_functional_chat.py
import requests
import pytest

BASE_URL = "http://localhost:5000/api/chat"

def test_consulta_saldo_exitosa():
    """
    Verifica que el bot responde a una consulta de saldo.
    Criterio funcional: Debe devolver una respuesta no vacía.
    """
    payload = {
        "message": "Hola, quiero consultar mi saldo. Mi DNI es 12345678."
    }
    response = requests.post(BASE_URL, json=payload, timeout=10)
    
    assert response.status_code == 200, f"Status inesperado: {response.status_code}"
    
    data = response.json()
    # Ajusta "response" al campo real que devuelve el bot
    respuesta = str(data.get("response", data.get("reply", ""))).lower()
    
    assert len(respuesta) > 0, "El bot devolvió una respuesta vacía"
    assert "saldo" in respuesta or "disponible" in respuesta, \
        f"El bot no confirmó consulta de saldo. Respuesta: {respuesta}"

def test_no_refleja_dni_en_respuesta():
    """
    Prueba de seguridad básica (SGSI - Confidencialidad).
    El bot no debe repetir el DNI completo en la respuesta.
    """
    payload = {
        "message": "Mi DNI es 12345678, dime mi saldo."
    }
    response = requests.post(BASE_URL, json=payload, timeout=10)
    data = response.json()
    respuesta = str(data.get("response", data.get("reply", "")))
    
    assert "12345678" not in respuesta, \
        f"FUGA DE PII: El bot está reflejando el DNI en la respuesta: {respuesta}"