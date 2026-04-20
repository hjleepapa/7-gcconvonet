# Hanok Table reservation API (kfood submodule). Separate Cloud Run service (option 2).
# Build from repo root: docker build -f docker/hanok-table.Dockerfile .
# Requires kfood/hanok_table present (git submodule: git submodule update --init kfood).
FROM python:3.11-slim
WORKDIR /app

COPY docker/hanok-table-requirements.txt /tmp/hanok-requirements.txt
RUN pip install --no-cache-dir -r /tmp/hanok-requirements.txt

COPY kfood/ /app/kfood/

ENV PYTHONPATH=/app/kfood
WORKDIR /app/kfood

ENV PORT=8080
EXPOSE 8080

# Cloud Run sets PORT; hanok_table.app:app is the FastAPI entrypoint.
CMD ["/bin/sh", "-c", "exec uvicorn hanok_table.app:app --host 0.0.0.0 --port ${PORT:-8080}"]
