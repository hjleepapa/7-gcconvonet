# Hanok Table — 5th Cloud Run microservice (Convonet GCP).
# Build context: repository ROOT. Requires ./hanok_table/ (vendored FastAPI package).
# Copy from local checkout: cp -R kfood/hanok_table ./hanok_table   (then commit hanok_table/)
FROM python:3.11-slim
WORKDIR /app
COPY docker/hanok-table-requirements.txt /tmp/hanok-requirements.txt
RUN pip install --no-cache-dir -r /tmp/hanok-requirements.txt
COPY hanok_table /app/hanok_table
ENV PYTHONPATH=/app
ENV PORT=8080
EXPOSE 8080
CMD ["/bin/sh", "-c", "exec uvicorn hanok_table.app:app --host 0.0.0.0 --port ${PORT:-8080}"]
