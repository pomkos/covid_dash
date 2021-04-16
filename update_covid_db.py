import pandas as pd
import sqlalchemy as sq
import datetime as dt
import os 
import sys

def get_usa():
    usa_df = pd.read_csv("https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv")
    usa_df['fips'] = usa_df['fips'].astype('category')
    usa_df['date'] = usa_df['date'].apply(lambda x: dt.datetime.strptime(x,'%Y-%m-%d'))

    new_df = pd.DataFrame(columns=usa_df.columns)

    for state in usa_df['state'].unique():
        temp_df = usa_df[usa_df['state'] == state].copy()
        temp_df['new_cases'] = temp_df['cases'].diff()
        temp_df['weekly_rolling_new_cases'] = temp_df['new_cases'].rolling(window = 7).mean()
        temp_df['monthly_rolling_new_cases'] = temp_df['new_cases'].rolling(window = 30).mean()
        
        temp_df['new_deaths'] = temp_df['deaths'].diff()
        temp_df['weekly_rolling_new_deaths'] = temp_df['new_deaths'].rolling(window = 7).mean()
        temp_df['monthly_rolling_new_deaths'] = temp_df['new_deaths'].rolling(window = 30).mean()
        
        new_df = new_df.append(temp_df)
    return new_df.reset_index(drop=True)

def get_world():
    world_df = pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv')
    world_df['deaths_per_pos'] = world_df['new_deaths']/world_df['new_cases']
    world_df['pos_per_tests'] = world_df['new_cases']/world_df['new_tests']
    world_df['rolling_pos_per_tests'] = world_df['pos_per_tests'].rolling(7).mean()
    return world_df

def app():
    print("downloading usa")
    usa_df = get_usa()

    print("downloading world")
    world_df = get_world()
    
    engine = sq.create_engine(f'sqlite:///data/covid_db.sqlite')
    print("connecting")
    cnx = engine.connect()
    print("connected!")
    usa_df.to_sql('covid_states',con=cnx,if_exists='replace',index=False)
    print("states saved")
    world_df.to_sql('covid_world',con=cnx,if_exists='replace',index=False)

    print("everything saved!")
    return f'New data saved to the database today ({dt.datetime.now()}!)'

if __name__ == '__main__':
    app()
