# Hermes Agent on Railway

Deploy [Hermes Agent](https://hermes-agent.nousresearch.com/) to Railway with one click. Hermes is an open-source AI agent by Nous Research with tool use, memory, messaging platform integrations, and a web dashboard.

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/template/TEMPLATE_ID?referralCode=REFERRAL_CODE)

## What you get

- **Web Dashboard** at your Railway-provided URL — manage config, API keys, sessions, logs, analytics, cron jobs, and skills from your browser
- **REST API** for automation (`/api/status`, `/api/sessions`, `/api/config`, etc.)
- **Persistent storage** via Railway volumes (sessions, memories, logs)

## Setup

1. Click the **Deploy on Railway** button above
2. Set `DASHBOARD_PASSWORD` (required — protects your dashboard with basic auth)
3. Deploy — log in at your Railway URL and configure API keys, model, and settings from the dashboard

## Environment Variables

| Variable | Description |
|---|---|
| `DASHBOARD_USER` | Login username (default: `admin`) |
| `DASHBOARD_PASSWORD` | Login password (**required** — deploy will fail without it) |
| `AUTO_UPDATE` | Pull latest Hermes on every restart (default: `true`, set to `false` to pin to build version) |

All other configuration — LLM provider keys, tool API keys, messaging platform tokens, model selection, and agent settings — is done through the dashboard's **API Keys** and **Config** pages after deploy.

## Adding a Volume (recommended)

To persist sessions, memories, and logs across deploys, attach a Railway volume mounted at `/root/.hermes`.

## Resources

- [Hermes Agent Documentation](https://hermes-agent.nousresearch.com/docs)
- [GitHub Repository](https://github.com/NousResearch/hermes-agent)
- [Web Dashboard Guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard)
