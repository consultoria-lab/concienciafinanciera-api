# ConCiencia Financiera - Desarrollo Local

## Levantar ambos servicios

### 1. API (FastAPI) - Terminal 1

```bash
cd concienciafinanciera-api
uv run main.py
```

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/health

### 2. Frontend (Lovable) - Terminal 2

```bash
cd conciencia-financiera-hub
npm install
npm run dev
```

- App: http://localhost:5173

## Probar la API

### Swagger UI (navegador)

1. Abrir http://localhost:8000/docs
2. Click en POST /extract/presupuesto (o /inversiones)
3. Click en "Try it out"
4. En campo file, click "Choose File" y seleccionar PDF/imagen/audio/txt
5. Click "Execute"

### curl

```bash
# Texto plano
curl -X POST http://localhost:8000/extract/presupuesto \
  -F "file=@archivo.txt;type=text/plain"

# PDF
curl -X POST http://localhost:8000/extract/presupuesto \
  -F "file=@presupuesto.pdf"

# Imagen
curl -X POST http://localhost:8000/extract/inversiones \
  -F "file=@foto.jpg"

# Audio
curl -X POST http://localhost:8000/extract/inversiones \
  -F "file=@nota.m4a"
```

## Variables de entorno (.env)

```
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SECRET_KEY=sb_secret_...
OPENAI_MODEL=gpt-4o-mini
WHISPER_MODEL=whisper-1
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=lsv2_pt_...
LANGSMITH_PROJECT=conciencia financiera api
```
