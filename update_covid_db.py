import pandas as pd
import sqlalchemy as sq
import datetime as dt
import os 
import sys

def app():
    print("downloading")
    usa_df = pd.read_csv('https://covidtracking.com/api/v1/states/daily.csv')
    usa_df['total_tests'] = usa_df['positive'] + usa_df['negative']
    usa_df['pos_per_tests'] = usa_df['positive']/usa_df['total_tests']
    usa_df['date'] = usa_df['date'].astype(str)
    usa_df['date'] = usa_df['date'].apply(lambda x: dt.datetime.strptime(x,'%Y%m%d'))
    print("downloading second")
    world_df = pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv')
    world_df['deaths_per_pos'] = world_df['new_deaths']/world_df['new_cases']
    world_df['pos_per_tests'] = world_df['new_cases']/world_df['new_tests']
    
    engine = sq.create_engine(f'sqlite:///data/covid_db.sqlite')
    print("connecting")
    cnx = engine.connect()
    print("connected!")
    usa_df.to_sql('covid_states',con=cnx,if_exists='replace',index=False)
    print("states saved")
    world_df.to_sql('covid_world',con=cnx,if_exists='replace',index=False)

    print("everything saved!")
    return f'New data saved to the database today ({dt.datetime.now()}!)'

