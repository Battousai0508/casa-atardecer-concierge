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

This project includes a standard [Dockerfile](file:///Users/anaaragon/Desktop/capstone/casa-atardecer-concierge/Dockerfile) at the root, allowing you to deploy the FastAPI backend to any container-supporting cloud provider (such as Render, Railway, Fly.io, AWS, or DigitalOcean) without requiring the Google Cloud SDK (`gcloud` or `agents-cli deploy`).

### How to Deploy (Render, Railway, etc.)

1.  **Build and test the container locally** (optional):
    ```bash
    docker build -t casa-atardecer-concierge .
    docker run -p 8080:8080 --env-file .env casa-atardecer-concierge
    ```
2.  **Deploy to your hosting provider**:
    - Connect your GitHub repository to your hosting provider (e.g., Render, Railway).
    - Configure the service to build from the root [Dockerfile](file:///Users/anaaragon/Desktop/capstone/casa-atardecer-concierge/Dockerfile).
    - Expose port `8080` (or your provider's default port).
    - Define your environment variables (like `GEMINI_API_KEY`) in the provider's Dashboard settings.

## Observability

Built-in telemetry exports to Cloud Trace, BigQuery, and Cloud Logging.

## A2A Inspector

This agent supports the [A2A Protocol](https://a2a-protocol.org/). Use the [A2A Inspector](https://github.com/a2aproject/a2a-inspector) to test interoperability.
See the [A2A Inspector docs](https://github.com/a2aproject/a2a-inspector) for details.
