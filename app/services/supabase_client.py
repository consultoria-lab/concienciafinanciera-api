from functools import lru_cache

from supabase import Client, create_client

from app.config import get_settings


def _get_client() -> Client:
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_secret_key)


@lru_cache
def get_categorias_salida() -> dict[str, str]:
    """Fetch categorias_salida. Retorna {nombre: id}."""
    client = _get_client()
    response = client.table("categorias_salida").select("id, nombre").execute()
    return {row["nombre"]: row["id"] for row in response.data}


@lru_cache
def get_categorias_inversion() -> dict[str, str]:
    """Fetch categorias_inversion. Retorna {nombre: id}."""
    client = _get_client()
    response = client.table("categorias_inversion").select("id, nombre").execute()
    return {row["nombre"]: row["id"] for row in response.data}


@lru_cache
def get_categorias_inversion_con_ayuda() -> list[dict]:
    """Fetch categorias_inversion con campo ayuda para el prompt."""
    client = _get_client()
    response = (
        client.table("categorias_inversion").select("id, nombre, ayuda").execute()
    )
    return response.data


def resolve_categoria(nombre: str, categorias: dict[str, str]) -> str | None:
    """Resuelve nombre de categoria a UUID. Busca coincidencia exacta o parcial."""
    nombre_lower = nombre.lower().strip()
    # Coincidencia exacta (case-insensitive)
    for cat_nombre, cat_id in categorias.items():
        if cat_nombre.lower() == nombre_lower:
            return cat_id
    # Coincidencia parcial
    for cat_nombre, cat_id in categorias.items():
        if nombre_lower in cat_nombre.lower() or cat_nombre.lower() in nombre_lower:
            return cat_id
    return None
