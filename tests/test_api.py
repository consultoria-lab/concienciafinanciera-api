from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.models.schemas import ExtraccionPresupuesto, ConceptoExtraido, ExtraccionInversiones, InversionExtraida


class TestHealthEndpoint:
    def test_health_no_auth_required(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestAuthenticationRequired:
    def test_presupuesto_missing_api_key(self, client: TestClient):
        response = client.post(
            "/extract/presupuesto",
            files={"file": ("test.txt", b"salario 3000000", "text/plain")},
        )
        assert response.status_code == 422  # Missing required header

    def test_presupuesto_invalid_api_key(self, client: TestClient):
        response = client.post(
            "/extract/presupuesto",
            files={"file": ("test.txt", b"salario 3000000", "text/plain")},
            headers={"X-API-Key": "wrong-key"},
        )
        assert response.status_code == 401

    def test_inversiones_missing_api_key(self, client: TestClient):
        response = client.post(
            "/extract/inversiones",
            files={"file": ("test.txt", b"cdt 10000000", "text/plain")},
        )
        assert response.status_code == 422

    def test_inversiones_invalid_api_key(self, client: TestClient):
        response = client.post(
            "/extract/inversiones",
            files={"file": ("test.txt", b"cdt 10000000", "text/plain")},
            headers={"X-API-Key": "wrong-key"},
        )
        assert response.status_code == 401


class TestPresupuestoEndpoint:
    @patch("app.routers.extraction.get_categorias_salida")
    @patch("app.routers.extraction.extract_presupuesto")
    def test_successful_extraction(
        self, mock_extract, mock_categorias, client: TestClient, api_key: str
    ):
        mock_extract.return_value = ExtraccionPresupuesto(
            items=[
                ConceptoExtraido(
                    nombre="salario",
                    valor=3_000_000,
                    tipo="entrada",
                    periodicidad="mensual",
                ),
                ConceptoExtraido(
                    nombre="arriendo",
                    valor=1_500_000,
                    tipo="salida",
                    periodicidad="mensual",
                    categoria_nombre="vivienda",
                ),
            ]
        )
        mock_categorias.return_value = {"vivienda": "uuid-vivienda"}

        response = client.post(
            "/extract/presupuesto",
            files={"file": ("test.txt", b"salario 3000000\narriendo 1500000", "text/plain")},
            headers={"X-API-Key": api_key},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["module"] == "presupuesto"
        assert data["source_type"] == "documento"
        assert data["item_count"] == 2
        assert len(data["items"]) == 2

    def test_unsupported_file_type(self, client: TestClient, api_key: str):
        response = client.post(
            "/extract/presupuesto",
            files={"file": ("test.zip", b"data", "application/zip")},
            headers={"X-API-Key": api_key},
        )
        assert response.status_code == 400
        assert "no soportado" in response.json()["detail"]


class TestInversionesEndpoint:
    @patch("app.routers.extraction.get_categorias_inversion")
    @patch("app.routers.extraction.extract_inversiones")
    def test_successful_extraction(
        self, mock_extract, mock_categorias, client: TestClient, api_key: str
    ):
        mock_extract.return_value = ExtraccionInversiones(
            items=[
                InversionExtraida(
                    nombre="cdt bancolombia",
                    valor=10_000_000,
                    categoria_nombre="cdt",
                ),
            ]
        )
        mock_categorias.return_value = {"cdt": "uuid-cdt"}

        response = client.post(
            "/extract/inversiones",
            files={"file": ("test.txt", b"cdt bancolombia 10000000", "text/plain")},
            headers={"X-API-Key": api_key},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["module"] == "inversiones"
        assert data["item_count"] == 1
        assert data["items"][0]["categoria_id"] == "uuid-cdt"

    def test_unsupported_file_type(self, client: TestClient, api_key: str):
        response = client.post(
            "/extract/inversiones",
            files={"file": ("test.zip", b"data", "application/zip")},
            headers={"X-API-Key": api_key},
        )
        assert response.status_code == 400

    @patch("app.routers.extraction.get_categorias_inversion")
    @patch("app.routers.extraction.extract_inversiones")
    def test_file_too_large(
        self, mock_extract, mock_categorias, client: TestClient, api_key: str
    ):
        large_content = b"x" * (11 * 1024 * 1024)  # 11 MB
        response = client.post(
            "/extract/inversiones",
            files={"file": ("big.txt", large_content, "text/plain")},
            headers={"X-API-Key": api_key},
        )
        assert response.status_code == 400
        assert "10 MB" in response.json()["detail"]
