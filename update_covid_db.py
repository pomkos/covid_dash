import pandas as pd
import sqlalchemy as sq
import datetime as dt
import os 
import sys

us_pw = sys.argv[1]  # user input: "my_user:password"
db_ip = sys.argv[2]  # user input: 192.168.1.11
port = sys.argv[3]   # user input: 5432

def app():
    usa_df = pd.read_csv('https://covidtracking.com/api/v1/states/daily.csv')
    usa_df['total_tests'] = usa_df['positive'] + usa_df['negative']
    usa_df['pos_per_tests'] = usa_df['positive']/usa_df['total_tests']
    usa_df['date'] = usa_df['date'].astype(str)
    usa_df['date'] = usa_df['date'].apply(lambda x: dt.datetime.strptime(x,'%Y%m%d'))

    world_df = pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv')
    world_df['deaths_per_pos'] = world_df['new_deaths']/world_df['new_cases']
    world_df['pos_per_tests'] = world_df['new_cases']/world_df['new_tests']

    parent = os.path.dirname(os.getcwd()) # get parent of current directory
    engine = sq.create_engine(f'postgres://{us_pw}@{db_ip}:{port}')
    cnx = engine.connect()

    usa_df.to_sql('covid_states',con=cnx,if_exists='replace',index=False)
    world_df.to_sql('covid_world',con=cnx,if_exists='replace',index=False)

    return f'New data saved to the database today ({dt.datetime.now()}!)'