# conftest.py
import pytest
from pytest_metadata.plugin import metadata_key

# Clasificación de severidad por test (para el reporte SGSI)
SEVERIDAD = {
    "test_endpoint_database_no_expuesto":           "CRÍTICA",
    "test_database_no_contiene_ssn_en_respuesta":   "CRÍTICA",
    "test_database_no_contiene_credenciales":       "CRÍTICA",
    "test_ningun_prompt_filtra_ssn":                "ALTA",
    "test_ningun_prompt_revela_password":           "ALTA",
    "test_ningun_prompt_revela_system_prompt":      "MEDIA",
    "test_ningun_prompt_revela_tarjetas":           "ALTA",
    "test_consulta_saldo_exitosa":                  "FUNCIONAL",
    "test_no_refleja_dni_en_respuesta":             "ALTA",
}

def pytest_html_report_title(report):
    report.title = "PoC QA & Seguridad — Chatbot vulnerable (SGSI)"

@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session, exitstatus):
    session.config.stash[metadata_key]["Entorno"]         = "Local (Docker)"
    session.config.stash[metadata_key]["Objetivo"]        = "scthornton/vulnerable-chat (PoC)"
    session.config.stash[metadata_key]["Marco SGSI"]      = "ISO/IEC 27001:2022"
    session.config.stash[metadata_key]["Controles"]       = "A.8.2, A.8.3, A.5.17, A.8.1"
    session.config.stash[metadata_key]["Criterio"]        = "0 fugas de PII/credenciales"

def pytest_html_results_table_header(cells):
    cells.insert(2, "<th>Severidad SGSI</th>")

def pytest_html_results_table_row(report, cells):
    sev = SEVERIDAD.get(report.nodeid.split("::")[-1], "—")
    color = {"CRÍTICA": "#c62828", "ALTA": "#ef6c00", "MEDIA": "#f9a825"}.get(sev, "#333")
    cells.insert(2, f'<td style="color:{color};font-weight:bold">{sev}</td>')