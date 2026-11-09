FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md cc_mock_server.py ./
RUN uv sync --locked

EXPOSE 5000

CMD [".venv/bin/uvicorn", "cc_mock_server:app", "--host", "0.0.0.0", "--port", "5000"]
