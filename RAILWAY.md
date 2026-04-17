![Hermes Agent](https://raw.githubusercontent.com/NousResearch/hermes-agent/main/assets/banner.png)

# Deploy Your Own Hermes Agent

Your own AI agent, running 24/7, talking to you on Telegram. Think OpenClaw, but **better**. Hermes Agent by Nous Research comes with tool use, persistent memory, scheduled tasks, and multi-platform messaging — and this template gives you the whole thing with one click.

## About

No YAML files. No SSH. No "just clone the repo and figure it out." This template gives you a fully managed Hermes Agent accessible from your browser. Add API keys, connect messaging platforms, manage sessions, view analytics, and schedule cron jobs — all from the dashboard. The messaging gateway runs alongside it and automatically restarts when you change settings. Attach a Railway volume and your data sticks around forever.

## Getting Started

### 1. Deploy to Railway

Click the **Deploy on Railway** button, set a `DASHBOARD_PASSWORD`, and deploy. Once it's live, open your Railway-provided URL and log in.

### 2. Add an LLM Provider

Your agent needs an AI model to work. [OpenRouter](https://openrouter.ai/) is the easiest option since it gives access to all major models with a single key.

1. Create an account at [openrouter.ai](https://openrouter.ai/) and generate an API key
2. In the Hermes dashboard, go to the **API Keys** page
3. Paste your key into the `OPENROUTER_API_KEY` field and save

### 3. Set Up a Telegram Bot

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts to name your bot
3. BotFather will give you a bot token — copy it
4. In the Hermes dashboard, go to the **API Keys** page
5. Paste the token into the `TELEGRAM_BOT_TOKEN` field and save
6. Also set `GATEWAY_ALLOW_ALL_USERS=true` (or set `TELEGRAM_ALLOWED_USERS` to your Telegram user ID for restricted access)
7. The gateway will restart automatically — check the status widget in the bottom-right corner

### 4. Test It

Open your new bot in Telegram and send a message. Hermes will respond using the model you configured. You can check the **Sessions** page in the dashboard to see the conversation, token usage, and tool calls.

### 5. Persist Your Data (Recommended)

Attach a Railway volume so your config, sessions, and memories survive redeploys:

1. Right-click the service in your Railway project
2. Select **Attach Volume**
3. Set mount path to `/root/.hermes`

## Common Use Cases

- Run a personal AI assistant on Telegram, Discord, or Slack with persistent memory and tool use
- Manage your agent from any browser — configure models, API keys, sessions, and analytics through the dashboard
- Schedule recurring AI tasks with cron jobs and monitor usage and costs

## Dependencies

- At least one LLM provider API key ([OpenRouter](https://openrouter.ai/), [Anthropic](https://console.anthropic.com/), [OpenAI](https://platform.openai.com/), or [DeepSeek](https://platform.deepseek.com/))
- A Telegram, Discord, or Slack bot token (if using messaging platforms)

### Deployment Dependencies

- [Hermes Agent Documentation](https://hermes-agent.nousresearch.com/docs)
- [Web Dashboard Guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard)
- [Telegram BotFather](https://t.me/BotFather) (for Telegram setup)
- [OpenRouter](https://openrouter.ai/) (recommended LLM provider)

## Why Use Railway?

Railway is a singular platform to deploy your infrastructure stack. Railway will host your infrastructure so you don't have to deal with configuration, while allowing you to vertically and horizontally scale it.
