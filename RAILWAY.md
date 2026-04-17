# Deploy and Host Hermes Agent (with Official Dashboard) on Railway

Hermes Agent is an open-source AI agent by Nous Research with tool use, persistent memory, scheduled tasks, and multi-platform messaging. This template deploys the full agent with its official web dashboard, messaging gateway for Telegram/Discord/Slack, cookie-based authentication, and automatic updates on every restart.

## About Hosting Hermes Agent (with Official Dashboard)

Hosting Hermes Agent requires running three components: the web dashboard (a FastAPI server serving a React SPA), the messaging gateway (a long-running process that connects to Telegram, Discord, and Slack), and an authentication proxy that protects both behind a login page. This template bundles all three into a single container with a Python-based auth proxy that handles session cookies, gateway lifecycle management, and health checks. Configuration is done entirely through the dashboard UI after deploy — no SSH or CLI access needed. A Railway volume is recommended to persist sessions, memories, API keys, and config across redeploys.

## Common Use Cases

- Run a personal AI assistant accessible via Telegram, Discord, or Slack with persistent memory and tool use
- Host a web-based dashboard to manage agent configuration, API keys, sessions, and analytics from any browser
- Schedule recurring AI agent tasks with cron jobs and monitor usage and costs through built-in analytics

## Dependencies for Hermes Agent (with Official Dashboard) Hosting

- Python 3.11 runtime with uv package manager
- Node.js 22 (for browser automation tools and frontend builds)

### Deployment Dependencies

- [Hermes Agent GitHub Repository](https://github.com/NousResearch/hermes-agent)
- [Hermes Agent Documentation](https://hermes-agent.nousresearch.com/docs)
- [Web Dashboard Guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard)
- At least one LLM provider API key ([OpenRouter](https://openrouter.ai/), [Anthropic](https://console.anthropic.com/), [OpenAI](https://platform.openai.com/), or [DeepSeek](https://platform.deepseek.com/))

### Implementation Details

The template runs an aiohttp reverse proxy (`auth_proxy.py`) as the main process, which handles:

- **Cookie-based authentication** — login page with HMAC-signed session cookies (7-day expiry), no repeated browser auth prompts
- **Gateway lifecycle** — starts the messaging gateway on boot, auto-restarts it when API keys or config are changed through the dashboard
- **HTML injection** — injects a floating status widget into the dashboard showing gateway state and volume mount status
- **Health check** — unauthenticated `/api/health` endpoint for Railway's health monitoring

```
Internet -> Railway -> Auth Proxy (cookie login) -> Hermes Dashboard (port 9119)
                           |
                           +-> Messaging Gateway (Telegram/Discord/Slack)
                           +-> /api/health (Railway health check)
                           +-> /api/gateway/restart (restart bot)
                           +-> /api/gateway/status (check bot + volume status)
```

Auto-updates pull the latest Hermes release on every container restart via `git pull` — no template repo changes needed.

## Why Deploy Hermes Agent (with Official Dashboard) on Railway?

Railway is a singular platform to deploy your infrastructure stack. Railway will host your infrastructure so you don't have to deal with configuration, while allowing you to vertically and horizontally scale it.

By deploying Hermes Agent (with Official Dashboard) on Railway, you are one step closer to supporting a complete full-stack application with minimal burden. Host your servers, databases, AI agents, and more on Railway.
