"""Airflow DAG for dbt parse/build, requiring a provisioned analytics connection."""
from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
with DAG("august_dbt_daily",start_date=datetime(2026,1,1),schedule="@daily",
         catchup=False,max_active_runs=1,tags=["august","dbt"]) as dag:
    parse=BashOperator(task_id="parse",bash_command="cd \"$AUGUST_REPO_ROOT\" && dbt parse")
    build=BashOperator(task_id="build",bash_command="cd \"$AUGUST_REPO_ROOT\" && dbt build")
    parse >> build
