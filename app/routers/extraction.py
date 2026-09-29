import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.dependencies import verify_api_key
from app.models.schemas import ExtractionResponse
from app.services.extraction import (
    SUPPORTED_TYPES,
    extract_inversiones,
    extract_presupuesto,
    get_medio_cargue,
    get_source_type,
)
from app.services.supabase_client import (
    get_categorias_inversion,
    get_categorias_salida,
    resolve_categoria,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/extract", tags=["extraction"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/presupuesto", response_model=ExtractionResponse)
async def extract_presupuesto_endpoint(file: UploadFile, _key: str = Depends(verify_api_key)):
    """Extrae conceptos de presupuesto (entradas/salidas) de un archivo."""
    content_type = file.content_type or ""
    logger.info("POST /extract/presupuesto - archivo: %s, tipo: %s", file.filename, content_type)

    if content_type not in SUPPORTED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no soportado: {content_type}. "
            f"Tipos soportados: PDF, imagenes (PNG/JPEG/WebP/GIF), audio (MP3/WAV/OGG/M4A/WebM/FLAC).",
        )

    file_bytes = await file.read()
    logger.info("Archivo leido: %.1f KB", len(file_bytes) / 1024)

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="El archivo excede el limite de 10 MB.")

    try:
        logger.info("Enviando a LLM para extraccion...")
        result = await extract_presupuesto(file_bytes, file.filename or "archivo", content_type)
        logger.info("LLM retorno %d items", len(result.items))
    except ValueError as e:
        logger.error("Error en extraccion: %s", e)
        raise HTTPException(status_code=422, detail=str(e))

    categorias = get_categorias_salida()
    logger.info("Categorias salida cargadas: %d", len(categorias))

    medio = get_medio_cargue(content_type)
    items = []
    for item in result.items:
        item_dict = item.model_dump()
        if item.tipo == "salida" and item.categoria_nombre:
            categoria_id = resolve_categoria(item.categoria_nombre, categorias)
            if categoria_id is None:
                logger.warning("Categoria no encontrada: '%s'", item.categoria_nombre)
            item_dict["categoria_id"] = categoria_id
        else:
            item_dict["categoria_id"] = None
        item_dict["medio_cargue"] = medio
        items.append(item_dict)

    logger.info("Respuesta: %d items, medio_cargue=%s", len(items), medio)
    return ExtractionResponse(
        items=items,
        module="presupuesto",
        source_type=get_source_type(content_type),
        item_count=len(items),
    )


@router.post("/inversiones", response_model=ExtractionResponse)
async def extract_inversiones_endpoint(file: UploadFile, _key: str = Depends(verify_api_key)):
    """Extrae inversiones de un archivo."""
    content_type = file.content_type or ""
    logger.info("POST /extract/inversiones - archivo: %s, tipo: %s", file.filename, content_type)

    if content_type not in SUPPORTED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no soportado: {content_type}. "
            f"Tipos soportados: PDF, imagenes (PNG/JPEG/WebP/GIF), audio (MP3/WAV/OGG/M4A/WebM/FLAC).",
        )

    file_bytes = await file.read()
    logger.info("Archivo leido: %.1f KB", len(file_bytes) / 1024)

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="El archivo excede el limite de 10 MB.")

    try:
        logger.info("Enviando a LLM para extraccion...")
        result = await extract_inversiones(file_bytes, file.filename or "archivo", content_type)
        logger.info("LLM retorno %d items", len(result.items))
    except ValueError as e:
        logger.error("Error en extraccion: %s", e)
        raise HTTPException(status_code=422, detail=str(e))

    categorias = get_categorias_inversion()
    logger.info("Categorias inversion cargadas: %d", len(categorias))

    medio = get_medio_cargue(content_type)
    items = []
    for item in result.items:
        categoria_id = resolve_categoria(item.categoria_nombre, categorias)
        if categoria_id is None:
            logger.warning("Categoria no encontrada: '%s'", item.categoria_nombre)
        item_dict = item.model_dump()
        item_dict["categoria_id"] = categoria_id
        item_dict["medio_cargue"] = medio
        items.append(item_dict)

    logger.info("Respuesta: %d items, medio_cargue=%s", len(items), medio)
    return ExtractionResponse(
        items=items,
        module="inversiones",
        source_type=get_source_type(content_type),
        item_count=len(items),
    )
