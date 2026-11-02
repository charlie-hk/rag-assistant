# The panel is built first, then copied in, so one image serves the API and the
# UI from the same origin and the browser never needs a second host.
FROM node:20-slim AS panel
WORKDIR /panel
COPY web/package.json web/package-lock.json* ./
RUN npm install --no-audit --no-fund
COPY web/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/ ./data/
COPY --from=panel /panel/dist ./web/dist

# 7860 is what Hugging Face Spaces expects; anything else can override PORT.
ENV PYTHONPATH=/app/src \
    PORT=7860

EXPOSE 7860
CMD ["sh", "-c", "uvicorn ragassistant.api:app --host 0.0.0.0 --port ${PORT:-7860}"]
