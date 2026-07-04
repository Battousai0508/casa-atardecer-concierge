# Casa Atardecer — Concierge (Frontend)

Next.js web interface for chatting with the Casa Atardecer agent (FastAPI + ADK backend).

## Local development

1. Start the backend from the project root (port 8000):

   ```bash
   uv run uvicorn app.fast_api_app:app --port 8000
   ```

   The root `.env` already includes `ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:3000` for CORS.

2. Start the frontend:

   ```bash
   npm install
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000).

## Environment variables

Defined in `.env.local` (see `.env.example`):

| Variable | Description | Default |
| --- | --- | --- |
| `NEXT_PUBLIC_API_URL` | FastAPI backend URL | `http://127.0.0.1:8000` |
| `NEXT_PUBLIC_AGENT_APP_NAME` | ADK agent app name | `app` |

## How it connects to the agent

- `POST {API_URL}/apps/{app}/users/{userId}/sessions` creates the session (the `userId` is generated once and stored in `localStorage`).
- `POST {API_URL}/run_sse` sends each message and receives the response as an SSE stream; partial events are rendered in real time ([lib/agent-client.ts](lib/agent-client.ts)).
- "Nueva conversación" discards the session and creates a new one on the next message.

## Deploying to Vercel

1. Import this directory (`frontend/`) as a project in Vercel (framework: Next.js, no extra configuration).
2. In **Settings → Environment Variables**, set `NEXT_PUBLIC_API_URL` to your backend's public URL (for example, the Cloud Run service).
3. On the backend, add the Vercel domain to `ALLOW_ORIGINS`, for example:

   ```env
   ALLOW_ORIGINS=https://your-project.vercel.app,http://localhost:3000
   ```
