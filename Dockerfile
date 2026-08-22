FROM python:3.13-slim AS builder

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/takdora-venv

RUN pip install --no-cache-dir "uv==0.9.21"
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

FROM python:3.13-slim AS runtime

ENV UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/takdora-venv \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    REFLEX_DIR=/tmp/reflex

RUN apt-get update \
    && apt-get install --no-install-recommends -y curl gettext-base nginx unzip \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir "uv==0.9.21" \
    && useradd --create-home --uid 10001 appuser \
    && mkdir -p /tmp/reflex /var/lib/nginx /var/cache/nginx \
    && chown -R appuser:appuser /tmp/reflex /var/lib/nginx /var/cache/nginx

WORKDIR /app
COPY --from=builder /opt/takdora-venv /opt/takdora-venv
COPY --chown=appuser:appuser . .
RUN chown appuser:appuser /app \
    && chmod 0555 /app/docker/start-production.sh

USER appuser
EXPOSE 10000
CMD ["/app/docker/start-production.sh"]
