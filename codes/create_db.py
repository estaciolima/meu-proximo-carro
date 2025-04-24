import pandas as pd
from sqlalchemy import create_engine, inspect, text
import mysql.connector

df = pd.read_csv('datasets/database-1701392111.8423762.csv')
df.columns = [c.strip() for c in df.columns]

engine = create_engine("{dialect}+{driver}://{username}:{password}@{host}/{database}".format(
    dialect='mysql',
    driver='mysqlconnector',
    username='root',
    password='password',
    host='localhost',
    database='mysql'))

with engine.connect() as connection:
    connection.execute(text('CREATE DATABASE IF NOT EXISTS carros_usados;'))
    connection.execute(text('USE carros_usados;'))
    connection.commit()
                                                                                                                                                                                                                
df.to_sql('carros', engine, index=False)
    
inspector = inspect(engine)

print(inspector.get_table_names('carros_usados'))