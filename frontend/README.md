# Casa Atardecer — Concierge (Frontend)

Interfaz web en Next.js para conversar con el agente de Casa Atardecer (backend FastAPI + ADK).

## Desarrollo local

1. Arranca el backend desde la raíz del proyecto (puerto 8000):

   ```bash
   uv run uvicorn app.fast_api_app:app --port 8000
   ```

   El `.env` de la raíz ya incluye `ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:3000` para CORS.

2. Arranca el frontend:

   ```bash
   npm install
   npm run dev
   ```

3. Abre [http://localhost:3000](http://localhost:3000).

## Variables de entorno

Definidas en `.env.local` (ver `.env.example`):

| Variable | Descripción | Default |
| --- | --- | --- |
| `NEXT_PUBLIC_API_URL` | URL del backend FastAPI | `http://127.0.0.1:8000` |
| `NEXT_PUBLIC_AGENT_APP_NAME` | Nombre de la app del agente en ADK | `app` |

## Cómo se conecta con el agente

- `POST {API_URL}/apps/{app}/users/{userId}/sessions` crea la sesión (el `userId` se genera una vez y se guarda en `localStorage`).
- `POST {API_URL}/run_sse` envía cada mensaje y recibe la respuesta como stream SSE; los eventos parciales se van pintando en tiempo real ([lib/agent-client.ts](lib/agent-client.ts)).
- "Nueva conversación" descarta la sesión y crea una nueva en el siguiente mensaje.

## Despliegue en Vercel

1. Importa este directorio (`frontend/`) como proyecto en Vercel (framework: Next.js, sin configuración extra).
2. En **Settings → Environment Variables** define `NEXT_PUBLIC_API_URL` con la URL pública de tu backend (por ejemplo, el servicio de Cloud Run).
3. En el backend, agrega el dominio de Vercel a `ALLOW_ORIGINS`, por ejemplo:

   ```env
   ALLOW_ORIGINS=https://tu-proyecto.vercel.app,http://localhost:3000
   ```
