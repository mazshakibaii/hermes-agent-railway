# Hermes Agent on Railway

Deploy [Hermes Agent](https://hermes-agent.nousresearch.com/) to Railway with one click. Hermes is an open-source AI agent by Nous Research with tool use, memory, messaging platform integrations, and a web dashboard.

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/template/TEMPLATE_ID?referralCode=REFERRAL_CODE)

## Features

This template goes beyond a basic Hermes deploy:

- **Full dashboard access** — manage config, API keys, sessions, logs, analytics, cron jobs, and skills from your browser. No SSH or CLI needed.
- **Messaging gateway included** — Telegram, Discord, and Slack bots run alongside the dashboard. Configure platform tokens in the UI, hit restart, and your bot is live.
- **Gateway management widget** — a floating status indicator and restart button injected into the dashboard. See at a glance if the gateway is running, restart it after config changes without redeploying.
- **Cookie-based auth** — password-protected login page with session cookies. No repeated browser auth prompts like basic auth templates.
- **Auto-updates** — pulls the latest Hermes release on every container restart. Always up to date, no manual intervention. Disable with `AUTO_UPDATE=false` to pin a version.
- **Zero config to start** — deploy with just a password, then set up everything else (LLM provider, API keys, messaging platforms) from the dashboard UI.
- **Persistent storage** — attach a Railway volume to keep sessions, memories, config, and logs across redeploys.

## Setup

1. Click the **Deploy on Railway** button above
2. Set `DASHBOARD_PASSWORD` (required)
3. Deploy — log in at your Railway URL
4. Add your LLM provider key (e.g. OpenRouter) on the **API Keys** page
5. Optionally configure Telegram/Discord/Slack tokens and hit **Restart** on the gateway widget

## Environment Variables

| Variable | Description |
|---|---|
| `DASHBOARD_USER` | Login username (default: `admin`) |
| `DASHBOARD_PASSWORD` | Login password (**required** — deploy will fail without it) |
| `AUTO_UPDATE` | Pull latest Hermes on every restart (default: `true`, set to `false` to pin version) |

All other configuration is done through the dashboard after deploy.

## Persistent Storage

To keep your data across redeploys, attach a Railway volume:

1. Right-click the service in your Railway project
2. Select **Attach Volume**
3. Set mount path to `/root/.hermes`

This persists sessions, memories, API keys, config, logs, and cron jobs.

## Architecture

```
Internet -> Railway -> Auth Proxy (cookie login) -> Hermes Dashboard (port 9119)
                           |
                           +-> Messaging Gateway (Telegram/Discord/Slack)
                           +-> /api/health (unauthenticated, for Railway health checks)
                           +-> /api/gateway/restart (authenticated, restart bot)
                           +-> /api/gateway/status (authenticated, check bot status)
```

## Resources

- [Hermes Agent Documentation](https://hermes-agent.nousresearch.com/docs)
- [GitHub Repository](https://github.com/NousResearch/hermes-agent)
- [Web Dashboard Guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard)
