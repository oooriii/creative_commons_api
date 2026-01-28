# creative_commons_api
api creative commons fake - mockup


Install dependencies
```
# Instal·la les dependències
uv pip install -e .

# O amb pip tradicional
pip install -e .

# Executa el servidor
python cc_mock_server.py

# O amb uvicorn directament
uvicorn cc_mock_server:app --reload --port 5000
```

Run the server
```
uv run cc_mock_server:app --host 0.0.0.0 --port 5000
```


Docker
```
# Build i run
docker-compose up --build cc-mock

# Només el servei mock
docker-compose up cc-mock

```

Tests
```
# Health check
curl http://localhost:5000/health

# Workflow 1: Llicències
curl http://localhost:5000/?locale=ca

# Workflow 2: Camps
curl http://localhost:5000/license/standard?locale=ca

# Workflow 3B: Detalls
curl "http://localhost:5000/details?license-uri=http://creativecommons.org/licenses/by-nc-sa/3.0/"

# Workflow 3A: Issue (POST)
curl -X POST http://localhost:5000/license/standard/issue \
  -d "answers=<answers><locale>ca</locale><license-standard><commercial>n</commercial><derivatives>sa</derivatives></license-standard></answers>"

```