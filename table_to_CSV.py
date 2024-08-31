import mysql.connector
import os
import csv
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

# To implement
# machine_password = os.getenv("MACHINE_PASSWORD")
# machine_address = os.getenv("MACHINE_ADDRESS")
# machine_ssh_port = os.getenv("MACHINE_SSH_PORT")
# machine_user = os.getenv("MACHINE_USER")

SQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
SQL_USER = os.getenv("SQL_USER")
SQL_HOST = os.getenv("SQL_HOST")
SQL_PORT = os.getenv("SQL_PORT")
DATABASE_NAME = os.getenv("DATABASE_NAME")

DATA_LIMIT = 10000000
LINES_PER_REQUEST = 10

cnx = mysql.connector.connect(user=SQL_USER, password=SQL_PASSWORD,
                              host=SQL_HOST, port=SQL_PORT,
                              database=DATABASE_NAME, connect_timeout=2)
cursor = cnx.cursor()

query = f"SELECT * FROM market_quotes LIMIT {DATA_LIMIT};"
cursor.execute(query)

column_names = [i[0] for i in cursor.description]
rows = cursor.fetchmany(LINES_PER_REQUEST)
with open('local_copy.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(column_names)

    while rows:
        for row in rows:
            writer.writerow(row)
        rows = cursor.fetchmany(LINES_PER_REQUEST)

cursor.close()
cnx.close()
