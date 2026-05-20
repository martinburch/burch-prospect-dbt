FROM apache/airflow:3.2.1-python3.12

USER airflow
COPY --chown=airflow:root airflow/requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
