# burch-prospect-dbt

dbt project for transforming Transfermarkt football data in DuckDB, orchestrated with [Apache Airflow 3](https://airflow.apache.org/) and [Astronomer Cosmos](https://astronomer.github.io/astronomer-cosmos/).

**This project currently includes only _[source testing](dbt/models/staging/_transfermarkt__sources.yml)_ as a demonstration**, not silver and gold data modelling.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) for local Python/dbt
- Python 3.12 (pinned via `.python-version`)
- [Docker Compose](https://docs.docker.com/compose/install/) v2.14+
- DuckDB database at `database/transfermarkt-datasets.duckdb`

```
mkdir -p database/
cd database/
curl -LO https://pub-e682421888d945d684bcae8890b0ec20.r2.dev/data/transfermarkt-datasets.duckdb
```

## Project layout

```
├── dbt/                   # dbt project
├── database/              # DuckDB file (not in git)
├── airflow/dags/          # Cosmos DAGs
├── docker-compose.yaml    # Airflow 3.2 cluster
├── Dockerfile             # Custom image with Cosmos + dbt-duckdb
├── pyproject.toml         # uv-managed Python deps (dbt-core, dbt-duckdb)
└── dbt/packages.yml       # dbt Hub packages (e.g. dbt-utils)
```

## Local dbt development

`pyproject.toml` installs the Python dbt toolchain (`dbt-core`, `dbt-duckdb`). Hub packages such as [dbt-utils](https://hub.getdbt.com/dbt-labs/dbt_utils/latest/) are declared in `dbt/packages.yml` and installed with `dbt deps`.

```bash
cd dbt

uv run dbt deps
uv run dbt debug
uv run dbt parse
uv run dbt list --resource-type source
```

The project defines sources from `transfermarkt-datasets` DuckDB database file, `main` schema.

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

Enable the **`prospect_dbt`** DAG. Cosmos runs `dbt deps` before tasks (`install_deps: true`), so Hub packages are installed in the container without a separate step. With no dbt models yet, the DAG may render with minimal tasks until we add SQL under `dbt/models/`.

### Verify dbt inside the worker

```bash
docker compose exec airflow-worker dbt debug \
  --project-dir /opt/airflow/dbt \
  --profiles-dir /opt/airflow/dbt
```

### Stop

```bash
docker compose down
```

## Environment variables

| Variable | Purpose |
|----------|---------|
| `DUCKDB_PATH` | Path to DuckDB file (local and container) |
| `DBT_PROJECT_PATH` | dbt project path in Airflow containers |
| `AIRFLOW_CONN_DUCKDB_DEFAULT` | Airflow connection for Cosmos DuckDB profile mapping |

Cosmos maps the connection `host` field to the dbt profile `path`.
