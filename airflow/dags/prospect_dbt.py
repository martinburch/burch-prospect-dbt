"""
Orchestrate the prospect dbt project with Astronomer Cosmos on Airflow 3.
"""

from datetime import datetime
import os
from pathlib import Path

from cosmos import DbtDag, ExecutionConfig, ProfileConfig, ProjectConfig
from cosmos.constants import ExecutionMode
from cosmos.profiles import DuckDBUserPasswordProfileMapping

DBT_PROJECT_PATH = Path(
    os.getenv("DBT_PROJECT_PATH", "/opt/airflow/dbt/prospect")
)

profile_config = ProfileConfig(
    profile_name="prospect",
    target_name="dev",
    profile_mapping=DuckDBUserPasswordProfileMapping(
        conn_id="duckdb_default",
        profile_args={"schema": "main"},
    ),
)

prospect_dbt_dag = DbtDag(
    project_config=ProjectConfig(DBT_PROJECT_PATH),
    profile_config=profile_config,
    execution_config=ExecutionConfig(execution_mode=ExecutionMode.LOCAL),
    schedule="@daily",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    dag_id="prospect_dbt",
    operator_args={"install_deps": True},
)
