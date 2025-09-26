FROM python:3.11-slim

WORKDIR /app

# Системные зависимости (если потребуется)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем мета-файлы
COPY pyproject.toml README.md ./

# Устанавливаем пакет (включая зависимости)
RUN pip install --no-cache-dir .

# Копируем весь исходный код
COPY . .

# Запускаем MCP-сервер
CMD ["daniel-lightrag-mcp"]
