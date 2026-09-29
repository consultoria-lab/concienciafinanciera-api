import pytest
from pydantic import ValidationError

from app.models.schemas import ConceptoExtraido, InversionExtraida


class TestConceptoExtraido:
    def test_valid_entrada(self):
        c = ConceptoExtraido(
            nombre="salario",
            valor=3_000_000,
            tipo="entrada",
            periodicidad="mensual",
        )
        assert c.nombre == "salario"
        assert c.valor == 3_000_000
        assert c.tipo == "entrada"

    def test_valid_salida_with_categoria(self):
        c = ConceptoExtraido(
            nombre="arriendo",
            valor=1_500_000,
            tipo="salida",
            periodicidad="mensual",
            categoria_nombre="vivienda",
        )
        assert c.categoria_nombre == "vivienda"

    def test_valor_must_be_positive(self):
        with pytest.raises(ValidationError, match="greater than 0"):
            ConceptoExtraido(
                nombre="test", valor=0, tipo="entrada", periodicidad="mensual"
            )

    def test_negative_valor_rejected(self):
        with pytest.raises(ValidationError, match="greater than 0"):
            ConceptoExtraido(
                nombre="test", valor=-100, tipo="salida", periodicidad="anual"
            )

    def test_invalid_tipo_rejected(self):
        with pytest.raises(ValidationError):
            ConceptoExtraido(
                nombre="test", valor=1000, tipo="otro", periodicidad="mensual"
            )

    def test_invalid_periodicidad_rejected(self):
        with pytest.raises(ValidationError):
            ConceptoExtraido(
                nombre="test", valor=1000, tipo="entrada", periodicidad="semanal"
            )


class TestInversionExtraida:
    def test_valid_inversion(self):
        i = InversionExtraida(
            nombre="cdt bancolombia",
            valor=10_000_000,
            categoria_nombre="cdt",
        )
        assert i.nombre == "cdt bancolombia"
        assert i.nota is None

    def test_nota_within_limit(self):
        i = InversionExtraida(
            nombre="cdt",
            valor=5_000_000,
            categoria_nombre="cdt",
            nota="vence en 6 meses",
        )
        assert i.nota == "vence en 6 meses"

    def test_nota_exceeds_30_chars(self):
        with pytest.raises(ValidationError, match="string_too_long"):
            InversionExtraida(
                nombre="cdt",
                valor=5_000_000,
                categoria_nombre="cdt",
                nota="esta nota tiene mas de treinta caracteres y debe fallar",
            )

    def test_valor_must_be_positive(self):
        with pytest.raises(ValidationError, match="greater than 0"):
            InversionExtraida(
                nombre="test", valor=0, categoria_nombre="cdt"
            )
