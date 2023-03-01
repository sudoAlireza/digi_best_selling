from flask import Flask, jsonify, render_template
from dotenv import load_dotenv
import os

import mysql.connector

from flask_swagger_ui import get_swaggerui_blueprint


app = Flask(__name__)

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.yml'
swagger_ui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "My API"})
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


load_dotenv()

mysql_host = os.getenv('MYSQL_HOST')
mysql_port = int(os.getenv('MYSQL_PORT'))
mysql_user = os.getenv('MYSQL_USER')
mysql_password = os.getenv('MYSQL_PASSWORD')
mysql_database = 'best_selling_db'

cnx = mysql.connector.connect(user=mysql_user,
                              password=mysql_password,
                              host='localhost',
                              database=mysql_database)

cursor = cnx.cursor()


@app.route('/')
def index():
    return render_template('index.html')

@app.route("/analysis/main_category")
def main_category_analysis():
    query = """
        SELECT main_category, COUNT(*) as num_products, AVG(rate) as avg_rating, AVG(rate_count) as avg_rate_count, AVG(comment_count) as avg_comment_count
        FROM best_selling_table
        GROUP BY main_category
        ORDER BY num_products DESC
    """
    cursor.execute(query)
    result = []
    for row in cursor.fetchall():
        result.append(dict(zip(cursor.column_names, row)))

    json_result = jsonify(result)
    return json_result


@app.route("/analysis/sub_category")
def sub_category_analysis():
    query = """
        SELECT sub_category, COUNT(*) as num_products, AVG(rate) as avg_rating, AVG(rate_count) as avg_rate_count, AVG(comment_count) as avg_comment_count
        FROM best_selling_table
        GROUP BY sub_category
        ORDER BY num_products DESC
    """
    cursor.execute(query)
    result = []
    for row in cursor.fetchall():
        result.append(dict(zip(cursor.column_names, row)))

    json_result = jsonify(result)
    return json_result


@app.route("/analysis/price")
def price_analysis():
    query = """
        SELECT first_price, last_price, COUNT(*) as num_products, AVG(rate) as avg_rating, AVG(rate_count) as avg_rate_count, AVG(comment_count) as avg_comment_count
        FROM best_selling_table
        GROUP BY first_price, last_price
        ORDER BY first_price, last_price
    """
    cursor.execute(query)
    result = []
    for row in cursor.fetchall():
        result.append(dict(zip(cursor.column_names, row)))

    json_result = jsonify(result)
    return json_result




@app.route("/analysis/rating")
def rating_analysis():
    query = """
    SELECT rate, COUNT(*) as num_products, AVG(first_price) as avg_first_price, AVG(last_price) as avg_last_price, AVG(rate_count) as avg_rate_count, AVG(comment_count) as avg_comment_count
    FROM best_selling_table
    GROUP BY rate
    ORDER BY rate DESC
    """
    cursor.execute(query)
    result = []
    for row in cursor.fetchall():
        result.append(dict(zip(cursor.column_names, row)))

    json_result = jsonify(result)
    return json_result




@app.route("/analysis/rate_count")
def rate_count_analysis():
    query = """
        SELECT rate_count, COUNT(*) as num_products, AVG(first_price) as avg_first_price, AVG(last_price) as avg_last_price, AVG(rate) as avg_rating, AVG(comment_count) as avg_comment_count
        FROM best_selling_table
        GROUP BY rate_count
        ORDER BY rate_count DESC
    """
    cursor.execute(query)
    result = []
    for row in cursor.fetchall():
        result.append(dict(zip(cursor.column_names, row)))

    json_result = jsonify(result)
    return json_result



if __name__ == '__main__':
    app.run()
