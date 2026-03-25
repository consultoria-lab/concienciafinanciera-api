from typing import Literal

from pydantic import BaseModel, Field


class ConceptoExtraido(BaseModel):
    """Un concepto financiero extraido de un documento (entrada o salida)."""

    nombre: str = Field(description="Nombre del concepto financiero, en minusculas")
    valor: float = Field(gt=0, description="Valor en COP, debe ser mayor a 0")
    tipo: Literal["entrada", "salida"] = Field(
        description="Tipo de concepto: 'entrada' para ingresos, 'salida' para gastos"
    )
    periodicidad: Literal["mensual", "anual"] = Field(
        description="Periodicidad del concepto: 'mensual' o 'anual'"
    )
    categoria_nombre: str | None = Field(
        default=None,
        description="Nombre de la categoria (solo para tipo 'salida'). Debe ser None para tipo 'entrada'.",
    )


class InversionExtraida(BaseModel):
    """Una inversion extraida de un documento."""

    nombre: str = Field(description="Nombre de la inversion, en minusculas")
    valor: float = Field(gt=0, description="Valor en COP, debe ser mayor a 0")
    categoria_nombre: str = Field(
        description="Nombre de la categoria de inversion que mejor corresponde"
    )
    nota: str | None = Field(
        default=None,
        max_length=30,
        description="Nota breve opcional (maximo 30 caracteres)",
    )


class ExtraccionPresupuesto(BaseModel):
    """Resultado de extraccion de conceptos de presupuesto."""

    items: list[ConceptoExtraido]


class ExtraccionInversiones(BaseModel):
    """Resultado de extraccion de inversiones."""

    items: list[InversionExtraida]


class ExtractionResponse(BaseModel):
    """Respuesta del endpoint de extraccion."""

    items: list[dict]
    module: str
    source_type: str
    item_count: int
