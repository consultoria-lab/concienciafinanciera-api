EJEMPLOS_CATEGORIAS_SALIDA = {
    "Seguridad Social e Impuestos": "EPS, ARL, pension obligatoria, seguro de vida, impuesto predial, impuesto de renta, retefuente, SOAT",
    "Hogar": "arriendo, administracion, supermercado, mercado, aseo, muebles, electrodomesticos, reparaciones del hogar",
    "Salud y Bienestar": "gimnasio, medicamentos, citas medicas, medicina prepagada, odontologia, terapias, suplementos",
    "Transporte": "gasolina, parqueadero, peajes, transporte publico, Uber/DiDi, tecnicomecanica, mantenimiento vehiculo",
    "Entretenimiento y Moda": "Netflix, Spotify, restaurantes, bares, cine, ropa, zapatos, accesorios, viajes, vacaciones, hobbies",
    "Gastos Fijos": "servicios publicos (agua, luz, gas), internet, celular, telefono fijo, plataformas digitales, suscripciones",
    "Educacion": "universidad, colegio, cursos, Udemy, Platzi, libros, materiales de estudio, certificaciones",
    "Negocios": "insumos de negocio, publicidad, herramientas de trabajo, coworking, software empresarial, contador",
    "Inversiones": "pension voluntaria, aportes a AFC, ahorro programado, aportes a fondos de inversion",
    "Otros": "regalos, donaciones, imprevistos, mascota, cualquier gasto que no encaje en las anteriores",
}


def build_presupuesto_prompt(categorias_salida: list[str]) -> str:
    """Construye el system prompt para extraccion de presupuesto."""
    cats_list = "\n".join(
        f"  - **{c}**: {EJEMPLOS_CATEGORIAS_SALIDA.get(c, '')}"
        for c in categorias_salida
    )

    return f"""Eres un asistente financiero especializado en presupuestos personales en Colombia.

Tu tarea es extraer conceptos financieros (entradas y salidas) de documentos proporcionados por el usuario.

## Reglas de extraccion

1. Cada concepto debe tener: nombre, valor, tipo, periodicidad y categoria (solo salidas).
2. El **nombre** debe estar en minusculas y ser conciso.
3. El **valor** debe ser un numero positivo en Pesos Colombianos (COP). No incluyas simbolos ni separadores de miles.
4. El **tipo** solo puede ser "entrada" (ingresos) o "salida" (gastos/egresos).
5. La **periodicidad** solo puede ser "mensual" o "anual".
6. Para **categoria_nombre**:
   - Si el concepto es tipo "entrada" (ingreso), categoria_nombre debe ser null.
   - Si el concepto es tipo "salida" (gasto), usa EXACTAMENTE uno de los nombres de la lista de abajo. Guiate por los ejemplos de cada categoria para clasificar correctamente:
{cats_list}
   - Usa "Otros" SOLO si el concepto realmente no encaja en ninguna otra categoria.

## Formato de moneda

- Los valores en COP pueden aparecer como: $1.000.000, 1000000, 1,000,000, $1'000.000
- Siempre convierte a numero entero sin separadores (ejemplo: 1000000).

## Multiples items

- Un documento puede contener multiples conceptos. Extrae TODOS los que encuentres.
- Si el documento no contiene informacion financiera clara, retorna una lista vacia.
"""


def build_inversiones_prompt(categorias_info: list[dict]) -> str:
    """Construye el system prompt para extraccion de inversiones."""
    cats_list = "\n".join(
        f"  - {c['nombre']}: {c.get('ayuda', '')}" for c in categorias_info
    )

    return f"""Eres un asistente financiero especializado en inversiones y patrimonio personal en Colombia.

Tu tarea es extraer inversiones de documentos proporcionados por el usuario.

## Reglas de extraccion

1. Cada inversion debe tener: nombre, valor, categoria y opcionalmente una nota.
2. El **nombre** debe estar en minusculas y ser conciso.
3. El **valor** debe ser un numero positivo en Pesos Colombianos (COP). No incluyas simbolos ni separadores de miles.
4. Para **categoria_nombre**, usa EXACTAMENTE uno de los nombres de esta lista:
{cats_list}
5. La **nota** es opcional, maximo 30 caracteres. Usa solo si hay informacion adicional relevante (ej: banco, tasa, plazo).

## Formato de moneda

- Los valores en COP pueden aparecer como: $1.000.000, 1000000, 1,000,000, $1'000.000
- Siempre convierte a numero entero sin separadores (ejemplo: 1000000).

## Contexto colombiano

- CDT = Certificado de Deposito a Termino (categoria: Inversiones)
- Fogafin = Seguro de depositos (cubre hasta $50M COP por banco)
- Los fondos de inversion, acciones, bonos van en categoria "Inversiones"
- Propiedades, terrenos, lotes van en "Inmuebles"
- Vehiculos, maquinaria van en "Activos Fijos"
- Efectivo, cuentas de ahorro, cuentas corrientes van en "Efectivo"

## Multiples items

- Un documento puede contener multiples inversiones. Extrae TODAS las que encuentres.
- Si el documento no contiene informacion de inversiones, retorna una lista vacia.
"""
