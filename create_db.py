import pandas as pd
from sqlalchemy import create_engine, inspect, text
#import mysql.connector

df = pd.read_csv('example.csv')

engine = create_engine("{dialect}+{driver}://{username}:{password}@{host}/{database}".format(
    dialect='mysql',
    driver='mysqlconnector',
    username='root',
    password='admin',
    host='localhost',
    database='carros_usados'))

df.to_sql('carros', engine, index=False)

with engine.connect() as connection:
    connection.execute(text('CREATE DATABASE IF NOT EXISTS carros_usados;'))
    connection.execute(text('USE carros_usados;'))
    connection.commit()

    

inspector = inspect(engine)

print(inspector.get_table_names('carros_usados'))