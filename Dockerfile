# --- build stage -------------------------------------------------------------
FROM python:3.14-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- runtime stage -----------------------------------------------------------
FROM python:3.14-slim

# Non-root user; no shell, no home-dir clutter
RUN groupadd --gid 10001 skyhook \
    && useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin skyhook

COPY --from=builder /install /usr/local
WORKDIR /srv
COPY app/ app/

USER skyhook:skyhook
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz')"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
