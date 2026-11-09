# CC Mock API

Simulador de l’API REST de Creative Commons v1.5 per a proves amb DSpace. Port `5000`.

## Prova local amb uv

Instal·leu [uv](https://docs.astral.sh/uv/getting-started/installation/) si us cal. Obriu un terminal nou després d’instal·lar-lo.

```sh
curl -fsSL https://astral.sh/uv/install.sh | sh
```

Des de l’arrel del projecte:

```sh
uv sync --locked
uv run --no-sync uvicorn cc_mock_server:app --host 0.0.0.0 --port 5000
```

## Servei systemd

Linux amb `sudo` i usuari i grup `www-data`. El projecte ha de ser llegible per aquest usuari.

**1. Instal·leu uv a la ruta de la unitat.** Si ja teniu un binari accessible per a `www-data`, podeu fer servir aquella ruta a `ExecStart` i a l’ordre de sincronització.

```sh
curl -fsSL https://astral.sh/uv/install.sh | sudo env UV_UNMANAGED_INSTALL=/usr/local/bin sh
```

**2. Prepareu l’entorn.** Si canvieu la ruta del projecte, ajusteu `WorkingDirectory`. Si ja hi ha una `.venv` d’un altre usuari, moveu-la abans.

```sh
cd /dades/creative-commons/cc-mock-api
sudo install -d -o www-data -g www-data -m 0755 \
  .venv /var/cache/cc-mock-api /var/lib/cc-mock-api/python
sudo -u www-data env UV_CACHE_DIR=/var/cache/cc-mock-api \
  UV_PYTHON_INSTALL_DIR=/var/lib/cc-mock-api/python \
  /usr/local/bin/uv sync --locked
```

**3. Instal·leu i activeu la unitat.** Deixeu lliure el port 5000 abans d’arrencar.

```sh
sudo install -m 0644 cc-mock-api.service /etc/systemd/system/cc-mock-api.service
sudo systemctl daemon-reload
sudo systemctl enable --now cc-mock-api.service
sudo systemctl status cc-mock-api.service
```

Registres amb `sudo journalctl -u cc-mock-api.service -n 50`. En actualitzar el projecte, repetiu la sincronització del pas 2 i feu `sudo systemctl restart cc-mock-api.service`. Si canvieu la unitat, torneu-la a copiar i feu `daemon-reload` abans de reiniciar.

## Docker

Per executar només el mock, des de l’arrel del projecte:

```sh
docker build -t cc-mock-api .
docker run --rm -p 5000:5000 cc-mock-api
```

## DSpace

A `[dspace]/config/local.cfg`, poseu-hi l’URL accessible des del backend de DSpace.

```properties
cc.api.rooturl = http://nom-del-servidor:5000
```

## Comprovació

```sh
curl -fsS http://127.0.0.1:5000/health
```
