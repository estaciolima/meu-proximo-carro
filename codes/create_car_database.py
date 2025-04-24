import pandas as pd

df = pd.DataFrame()

for url in car_pages:
    car_info = car_crawler(base_url+url)
    car_info = pd.DataFrame(car_info)
    df = pd.concat([df,car_info], ignore_index=True)

df['Valor'] = [int(x[3:].replace('.','')) for x in df['Valor']] # convert number from string to int and remove 'R$'
df.to_csv('example.csv')