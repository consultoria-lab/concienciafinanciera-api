from langchain_openai import ChatOpenAI

from app.config import get_settings
from app.models.schemas import ExtraccionInversiones, ExtraccionPresupuesto
from app.prompts.system_prompts import (
    build_inversiones_prompt,
    build_presupuesto_prompt,
)
from app.services.preprocessors import (
    encode_image_to_base64,
    extract_text_from_excel,
    pdf_pages_to_base64_images,
    transcribe_audio,
)
from app.services.supabase_client import (
    get_categorias_inversion_con_ayuda,
    get_categorias_salida,
)

SUPPORTED_PDF = {"application/pdf"}
SUPPORTED_IMAGES = {"image/png", "image/jpeg", "image/webp", "image/gif"}
SUPPORTED_AUDIO = {
    "audio/mpeg",
    "audio/mp4",
    "audio/wav",
    "audio/webm",
    "audio/ogg",
    "audio/flac",
    "audio/m4a",
    "audio/x-m4a",
}
SUPPORTED_TEXT = {"text/plain", "text/markdown"}
SUPPORTED_EXCEL = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
}
SUPPORTED_TYPES = SUPPORTED_PDF | SUPPORTED_IMAGES | SUPPORTED_AUDIO | SUPPORTED_TEXT | SUPPORTED_EXCEL


def _get_llm() -> ChatOpenAI:
    settings = get_settings()
    return ChatOpenAI(
        model=settings.openai_model,
        temperature=0,
        api_key=settings.openai_api_key,
    )


def _build_user_message(
    file_bytes: bytes, filename: str, content_type: str
) -> list[dict]:
    """Construye el mensaje de usuario segun el tipo de archivo."""
    if content_type in SUPPORTED_PDF:
        # PDF → convertir paginas a imagenes → enviar como vision al LLM
        page_images = pdf_pages_to_base64_images(file_bytes)
        if not page_images:
            raise ValueError("El PDF no contiene paginas.")
        content: list[dict] = [
            {
                "type": "text",
                "text": "Extrae la informacion financiera de este documento:",
            }
        ]
        for img_uri in page_images:
            content.append({"type": "image_url", "image_url": {"url": img_uri}})
        return content

    if content_type in SUPPORTED_IMAGES:
        data_uri = encode_image_to_base64(file_bytes, content_type)
        return [
            {
                "type": "text",
                "text": "Extrae la informacion financiera de esta imagen:",
            },
            {"type": "image_url", "image_url": {"url": data_uri}},
        ]

    if content_type in SUPPORTED_AUDIO:
        text = transcribe_audio(file_bytes, filename)
        if not text.strip():
            raise ValueError("No se pudo transcribir el audio.")
        return [
            {
                "type": "text",
                "text": f"Transcripcion de audio del usuario:\n\n{text}",
            }
        ]

    if content_type in SUPPORTED_EXCEL:
        text = extract_text_from_excel(file_bytes)
        if not text:
            raise ValueError("El archivo Excel esta vacio.")
        return [{"type": "text", "text": text}]

    if content_type in SUPPORTED_TEXT:
        text = file_bytes.decode("utf-8", errors="replace").strip()
        if not text:
            raise ValueError("El archivo de texto esta vacio.")
        return [{"type": "text", "text": text}]

    raise ValueError(f"Tipo de archivo no soportado: {content_type}")


def get_source_type(content_type: str) -> str:
    """Retorna el tipo de fuente para la respuesta."""
    if content_type in SUPPORTED_PDF:
        return "documento"
    if content_type in SUPPORTED_IMAGES:
        return "imagen"
    if content_type in SUPPORTED_AUDIO:
        return "audio"
    if content_type in SUPPORTED_TEXT:
        return "documento"
    if content_type in SUPPORTED_EXCEL:
        return "documento"
    return "desconocido"


def get_medio_cargue(content_type: str) -> str:
    """Retorna el medio_cargue segun el tipo de archivo."""
    if content_type in SUPPORTED_PDF or content_type in SUPPORTED_TEXT or content_type in SUPPORTED_EXCEL:
        return "documento"
    if content_type in SUPPORTED_IMAGES:
        return "imagen"
    if content_type in SUPPORTED_AUDIO:
        return "audio"
    return "documento"


async def extract_presupuesto(
    file_bytes: bytes, filename: str, content_type: str
) -> ExtraccionPresupuesto:
    """Extrae conceptos de presupuesto de un archivo."""
    categorias = get_categorias_salida()
    system_prompt = build_presupuesto_prompt(list(categorias.keys()))

    llm = _get_llm()
    structured_llm = llm.with_structured_output(ExtraccionPresupuesto)

    user_content = _build_user_message(file_bytes, filename, content_type)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

    result = await structured_llm.ainvoke(messages)
    return result


async def extract_inversiones(
    file_bytes: bytes, filename: str, content_type: str
) -> ExtraccionInversiones:
    """Extrae inversiones de un archivo."""
    categorias_info = get_categorias_inversion_con_ayuda()
    system_prompt = build_inversiones_prompt(categorias_info)

    llm = _get_llm()
    structured_llm = llm.with_structured_output(ExtraccionInversiones)

    user_content = _build_user_message(file_bytes, filename, content_type)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

    result = await structured_llm.ainvoke(messages)
    return result
