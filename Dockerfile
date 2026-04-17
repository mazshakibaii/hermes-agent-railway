FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates ripgrep ffmpeg debian-keyring debian-archive-keyring apt-transport-https \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg \
    && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends nodejs caddy \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

RUN git clone --recurse-submodules https://github.com/NousResearch/hermes-agent.git /opt/hermes-agent

WORKDIR /opt/hermes-agent
RUN uv venv venv --python 3.11 \
    && VIRTUAL_ENV=/opt/hermes-agent/venv uv pip install -e ".[all]"

ENV PATH="/opt/hermes-agent/venv/bin:$PATH"

RUN mkdir -p /root/.hermes/{cron,sessions,logs,memories,skills,pairing,hooks,image_cache,audio_cache} \
    && cp cli-config.yaml.example /root/.hermes/config.yaml \
    && touch /root/.hermes/.env

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
