# Prospect

dbt project for Transfermarkt football data in DuckDB, orchestrated with [Apache Airflow 3](https://airflow.apache.org/) and [Astronomer Cosmos](https://astronomer.github.io/astronomer-cosmos/).

## Prerequisites

- [uv](https://docs.astral.sh/uv/) for local Python/dbt
- Python 3.12 (pinned via `.python-version`)
- [Docker Compose](https://docs.docker.com/compose/install/) v2.14+
- DuckDB database at `database/transfermarkt-datasets.duckdb` (gitignored; place your copy there)

## Project layout

```
├── prospect/              # dbt project
├── database/              # DuckDB file (not in git)
├── airflow/dags/          # Cosmos DAGs
├── docker-compose.yaml    # Airflow 3.2 cluster
├── Dockerfile             # Custom image with Cosmos + dbt-duckdb
└── pyproject.toml         # uv-managed local dbt deps
```

## Local dbt development

```bash
uv sync
export DUCKDB_PATH="$(pwd)/database/transfermarkt-datasets.duckdb"

uv run dbt debug --project-dir prospect --profiles-dir prospect
uv run dbt parse --project-dir prospect --profiles-dir prospect
uv run dbt list --project-dir prospect --profiles-dir prospect --resource-type source
```

The project defines sources from `transfermarkt-datasets` DuckDB database file, `main` schema. Staging and mart folders are scaffolded.

## Airflow + Cosmos

### Setup

```bash
cp .env.example .env
# Set FERNET_KEY in .env (see .env.example comment)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Ensure `database/transfermarkt-datasets.duckdb` exists before starting Airflow.

**Note:** Unset any host `DUCKDB_PATH` before `docker compose up` if you used it for local dbt (compose sets container paths internally). The database volume is read-write so dbt can materialize models into the same DuckDB file.

### Build and run

```bash
docker compose build
docker compose up airflow-init
docker compose up -d
```

Open the UI at [http://localhost:8080](http://localhost:8080) (default user/password: `airflow` / `airflow`).

Enable the **`prospect_dbt`** DAG. With no dbt models yet, the DAG may render with minimal tasks until you add SQL under `prospect/models/`.

### Verify dbt inside the worker

```bash
docker compose exec airflow-worker dbt debug \
  --project-dir /opt/airflow/dbt/prospect \
  --profiles-dir /opt/airflow/dbt/prospect
```

### Stop

```bash
docker compose down
```

## Versions

| Package | Version |
|---------|---------|
| dbt-core | 1.11.11 |
| dbt-duckdb | 1.10.1 |
| astronomer-cosmos | 1.14.1 |
| Apache Airflow | 3.2.1 |

## Environment variables

| Variable | Purpose |
|----------|---------|
| `DUCKDB_PATH` | Path to DuckDB file (local and container) |
| `DBT_PROJECT_PATH` | dbt project path in Airflow containers |
| `AIRFLOW_CONN_DUCKDB_DEFAULT` | Airflow connection for Cosmos DuckDB profile mapping |

Cosmos maps the connection `host` field to the dbt profile `path`.
