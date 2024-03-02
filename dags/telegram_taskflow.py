from airflow.providers.telegram.operators.telegram import TelegramOperator
from airflow.utils.dates import days_ago
from datetime import datetime
from airflow.decorators import task, dag
import requests
import pandas as pd


@dag(dag_id='TelegramBot', start_date=days_ago(1), schedule_interval='@daily')
def telegram_dag():

    @task
    def get_text(df: pd.DataFrame) -> str:
        sep = '   -   ' 
        text = f'''data          -   Min (°C) -  Max (°C)
{df.iloc[0,0].strftime('%d/%m/%Y')}{sep}{df.iloc[0,1]}{sep}{df.iloc[0,2]}
{df.iloc[1,0].strftime('%d/%m/%Y')}{sep}{df.iloc[1,1]}{sep}{df.iloc[1,2]}
{df.iloc[2,0].strftime('%d/%m/%Y')}{sep}{df.iloc[2,1]}{sep}{df.iloc[2,2]}''' 
        return text

    @task
    def requisicao():
        TOKEN = '39e14d935ebfb93759b34380231ab4b2'
        cityID = 73779
        url = f"http://apiadvisor.climatempo.com.br/api/v1/forecast/locale/{cityID}/hours/72?token={TOKEN}"
        response = requests.get(url)
        return response.json()

    @task
    def preprocess(data: dict):
        df = pd.DataFrame(data['data'])
        df['temperature'] = pd.json_normalize(df['temperature'])
        df['date'] = pd.to_datetime(df['date'])
        df['data'] = df['date'].dt.date
        df_min_max = df.groupby('data')['temperature'].agg(['min','max']).reset_index()
        df_min_max['amplitude'] = df_min_max['max'] - df_min_max['min']
        return df_min_max


    
    dados = requisicao()
    df_json = preprocess(dados)
    message = get_text(df_json)
    msg_1 = TelegramOperator(
            task_id="send_msg_1",
            text='Previsão do tempo',
        )
    msg_2 = TelegramOperator(
            task_id="send_msg_2",
            text=message,
        )
    
    
    dados>>df_json>>msg_1>>msg_2

dag = telegram_dag()