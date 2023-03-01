import json
import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import mysql.connector
from dotenv import load_dotenv

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from kafka import KafkaConsumer

cwd = os.getcwd()
print(cwd)


load_dotenv()
mysql_host = os.getenv('MYSQL_HOST')
mysql_port = int(os.getenv('MYSQL_PORT'))
mysql_user = os.getenv('MYSQL_USER')
mysql_password = os.getenv('MYSQL_PASSWORD')


def create_database_and_table():
    cnx = mysql.connector.connect(
        user=mysql_user,
        password=mysql_password,
        host=mysql_host
    )

    cursor = cnx.cursor()

    cursor.execute("SHOW DATABASES")
    db_exists = False
    for db in cursor:
        if db[0] == 'best_selling_db':
            db_exists = True
    if not db_exists:
        cursor.execute(f"CREATE DATABASE best_selling_db")
        print("Database created!")
    else:
        print("Database already exists.")


    cursor.execute('USE best_selling_db')

    cursor.execute("SHOW TABLES LIKE 'best_selling_table'")
    table_exists = False
    if cursor.fetchone():
        table_exists = True
    if not table_exists:
        cursor.execute('''
        CREATE TABLE best_selling_table (
        id INT AUTO_INCREMENT PRIMARY KEY,
        main_category VARCHAR(255),
        sub_category VARCHAR(255),
        first_price FLOAT,
        last_price FLOAT,
        rate INTEGER,
        rate_count INTEGER,
        comment_count INTEGER,
        timestamp DATETIME
        );
        ''')
    else:
        print("Table already exists.")

    cursor.close()
    cnx.close()


create_database_and_table()

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 3, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'scraper_dag',
    default_args=default_args,
    description='Run scrapy hourly and save the data in MySQL',
    schedule_interval=timedelta(hours=1),
)


def scrape_data():
    process = CrawlerProcess(get_project_settings())
    process.crawl('best_selling_scraper')
    process.start()

scrape_task = PythonOperator(
    task_id='scrape_data',
    python_callable=scrape_data,
    dag=dag
)


def read_json_store_in_mysql():
    with open('output.json', 'r') as f:
        results = json.load(f)
    

    cnx = mysql.connector.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        database='best_selling_db'
    )
    cursor = cnx.cursor()
    
    for result in results:
        main_category = result.get('main_cat')
        sub_category = result.get('sub_cat')
        first_price = result.get('first_price')
        off_price = result.get('last_price')
        rate = result.get('rate')
        rate_count = result.get('rate_count')
        comment_count = result.get('comment_count')
        
        add_result = ("INSERT INTO best_selling_table "
                      "(main_category, sub_category, first_price, last_price, rate, rate_count, comment_count, timestamp) "
                      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
        
        data = (main_category, sub_category, first_price, off_price, rate, rate_count, comment_count, datetime.now())
        
        cursor.execute(add_result, data)

    
    cnx.commit()
    cursor.close()
    cnx.close()
    os.remove("output.json")



# def kafka_consumer():
#     consumer = KafkaConsumer(
#         'products_topic',
#         bootstrap_servers = ['127.0.0.1:9092'],
#         auto_offset_reset = 'earliest',
#         enable_auto_commit = True,
#         group_id = 'products_group',
#         value_deserializer = lambda x : json.loads(x.decode('utf-8')),
#         api_version=(0, 10, 1)
#         )

#     cnx = mysql.connector.connect(
#         host=mysql_host,
#         user=mysql_user,
#         password=mysql_password,
#         database='best_selling_db'
#         )
#     cursor = cnx.cursor()


#     for message in consumer:
#         message = message.value.decode()
#         main_category = message.get('main_cat')
#         sub_category = message.get('sub_cat')
#         first_price = message.get('first_price')
#         off_price = message.get('last_price')
#         rate = message.get('rate')
#         rate_count = message.get('rate_count')
#         comment_count = message.get('comment_count')
        
#         add_result = ("INSERT INTO best_selling_table "
#                       "(main_category, sub_category, first_price, last_price, rate, rate_count, comment_count, timestamp) "
#                       "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
        
#         data = (main_category, sub_category, first_price, off_price, rate, rate_count, comment_count, datetime.now())
        
#         cursor.execute(add_result, data)


#     cnx.commit()
#     cursor.close()
#     cnx.close()

    



store_in_mysql_task = PythonOperator(
    task_id='store_in_mysql',
    python_callable=read_json_store_in_mysql,
    dag=dag
)

scrape_task >> store_in_mysql_task

