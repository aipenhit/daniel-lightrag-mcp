FROM python:3.11-slim

WORKDIR /app

# системные зав-ти (если потребуются)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# КОПИРУЕМ ВСЁ (включая src/)
COPY . .

# устанавливаем пакет + зависимости
RUN pip install --no-cache-dir .

# точка входа уже прописана в pyproject.toml
CMD ["daniel-lightrag-mcp"]
