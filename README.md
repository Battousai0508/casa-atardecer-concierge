# casa-atardecer-concierge

Simple ReAct agent
Agent generated with `agents-cli` version `1.0.0`

## Project Structure

```
casa-atardecer-concierge/
├── app/         # Core agent code
│   ├── agent.py               # Main agent logic
│   ├── fast_api_app.py        # FastAPI Backend server
│   └── app_utils/             # App utilities and helpers
├── tests/                     # Unit, integration, and load tests
├── GEMINI.md                  # AI-assisted development guide
└── pyproject.toml             # Project dependencies
```

> 💡 **Tip:** Use [Antigravity CLI](https://antigravity.google/) for AI-assisted development - project context is pre-configured in `GEMINI.md`.

## Requirements

Before you begin, ensure you have:
- **uv**: Python package manager (used for all dependency management in this project) - [Install](https://docs.astral.sh/uv/getting-started/installation/) ([add packages](https://docs.astral.sh/uv/concepts/dependencies/) with `uv add <package>`)
- **agents-cli**: Agents CLI - Install with `uv tool install google-agents-cli`
- **Google Cloud SDK**: For GCP services - [Install](https://cloud.google.com/sdk/docs/install)


## Quick Start

Install `agents-cli` and its skills if not already installed:

```bash
uvx google-agents-cli setup
```

Install required packages:

```bash
agents-cli install
```

Test the agent with a local web server:

```bash
agents-cli playground
```

You can also use features from the [ADK](https://adk.dev/) CLI with `uv run adk`.

## Commands

| Command              | Description                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------- |
| `agents-cli install` | Install dependencies using uv                                                         |
| `agents-cli playground` | Launch local development environment                                                  |
| `agents-cli lint`    | Run code quality checks                                                               |
| `agents-cli eval`    | Evaluate agent behavior (generate, grade, analyze, and more — see `agents-cli eval --help`) |
| `uv run pytest tests/unit tests/integration` | Run unit and integration tests                                                        || [A2A Inspector](https://github.com/a2aproject/a2a-inspector) | Launch A2A Protocol Inspector                                                        |

## 🛠️ Project Management

| Command | What It Does |
|---------|--------------|
| `agents-cli scaffold enhance` | Add CI/CD pipelines and Terraform infrastructure |
| `agents-cli infra cicd` | One-command setup of entire CI/CD pipeline + infrastructure |
| `agents-cli scaffold upgrade` | Auto-upgrade to latest version while preserving customizations |

---

## Local Development

### 1. Test Agent Logic Only (Playground)
To interact with the agent using the built-in ADK CLI dev UI, run:
```bash
agents-cli playground
```

### 2. Run Complete Application (FastAPI Backend + Next.js Frontend)
To run the full stack locally:

*   **Start the backend server** (runs on port `8000`):
    ```bash
    uv run uvicorn app.fast_api_app:app --port 8000
    ```
    *Note: The `.env` file at the root handles CORS configuration automatically.*

*   **Start the frontend server** (runs on port `3000`):
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

*   **Open** [http://localhost:3000](http://localhost:3000) in your browser.

---

## Deployment

### Option A: Deploy to Google Cloud (Cloud Run)
If you want to host the backend on Google Cloud, use the default ADK deployment commands (requires the Google Cloud SDK):
```bash
gcloud config set project <your-project-id>
agents-cli deploy
```
- To add CI/CD and Terraform infrastructure, run `agents-cli scaffold enhance`.
- To set up your complete production infrastructure pipeline, run `agents-cli infra cicd`.

### Option B: Deploy to Any Cloud Provider (Render, Railway, Fly.io, etc.)
Because this project includes a standard [Dockerfile](file:///Users/anaaragon/Desktop/capstone/casa-atardecer-concierge/Dockerfile), you can deploy it to any provider that supports Docker container deployments:

1.  **Build and run the container locally** to test:
    ```bash
    docker build -t casa-atardecer-concierge .
    docker run -p 8080:8080 --env-file .env casa-atardecer-concierge
    ```
2.  **Deploy**: Connect this repository to your preferred platform (e.g. Render, Railway) and point it to the root [Dockerfile](file:///Users/anaaragon/Desktop/capstone/casa-atardecer-concierge/Dockerfile) to build and run the backend. Make sure to configure the `GEMINI_API_KEY` and other variables in your provider's environment settings.

## Observability

Built-in telemetry exports to Cloud Trace, BigQuery, and Cloud Logging.

## A2A Inspector

This agent supports the [A2A Protocol](https://a2a-protocol.org/). Use the [A2A Inspector](https://github.com/a2aproject/a2a-inspector) to test interoperability.
See the [A2A Inspector docs](https://github.com/a2aproject/a2a-inspector) for details.
