FROM python:3.11-slim

WORKDIR /app

# Instal·la uv per gestió de dependències ràpida
RUN pip install --no-cache-dir uv

# Copia fitxers de configuració
COPY pyproject.toml ./

# Instal·la dependències
RUN uv pip install --system --no-cache -e .

# Copia el codi
COPY cc_mock_server.py ./

# Exposa el port
EXPOSE 5000

# Executa el servidor
CMD ["uvicorn", "cc_mock_server:app", "--host", "0.0.0.0", "--port", "5000"]