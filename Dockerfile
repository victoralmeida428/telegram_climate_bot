FROM python:3.10

WORKDIR /airflow

COPY . /airflow/

RUN pip install --upgrade pip &&  \
    pip install -r requirements.txt && \
    export AIRFLOW_HOME=$(pwd)

EXPOSE 8080



