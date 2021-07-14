import pandas as pd
import sqlalchemy as sq
import datetime as dt
import os
import sys

def cat_state(my_string):
    '''
    Label each USA state as one of the 4 Census defined regions
    '''
    # source for usa regions: https://en.wikipedia.org/wiki/List_of_regions_of_the_United_States
    regions = {
        'Northeast':['Connecticut', 'Maine', 'Massachusetts', 'New Hampshire', 
                     'Rhode Island', 'Vermont', 'New Jersey', 'New York', 'Pennsylvania'],
        'Midwest':['Illinois', 'Indiana', 'Michigan', 'Ohio', 
                   'Wisconsin', 'Iowa', 'Kansas', 'Minnesota', 'Missouri', 
                   'Nebraska', 'North Dakota','South Dakota'],
        'South':['Delaware', 'Florida', 'Georgia', 'Maryland',
                 'North Carolina', 'South Carolina', 'Virginia', 
                 'District of Columbia', 'West Virginia', 'Alabama', 
                 'Kentucky', 'Mississippi', 'Tennessee', 'Arkansas', 
                 'Louisiana', 'Oklahoma', 'Texas'],
        'West':['Arizona', 'Colorado', 'Idaho', 'Montana', 'Nevada',
                'New Mexico', 'Utah', 'Wyoming', 'Alaska', 
                'California', 'Hawaii', 'Oregon', 'Washington']
    }

    for r in regions.keys():
        if my_string in regions[r]:
            return r
        
def get_usa():
    """
    Download new data, merge with pop, calculate new variables
    """
    usa_df = pd.read_csv(
        "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv"
    )
    usa_vax = pd.read_csv('https://github.com/owid/covid-19-data/raw/master/public/data/vaccinations/us_state_vaccinations.csv').rename({'location':'state'}, axis=1)
    usa_vax['state'] = usa_vax['state'].str.replace('New York State', 'New York')
    usa_df = usa_df.merge(usa_vax, on=['date','state'], how='outer')
    usa_df["date"] = usa_df["date"].apply(lambda x: dt.datetime.strptime(x, "%Y-%m-%d"))
    
    statepop = (
        pd.read_csv("data/statepop.csv")[["NAME", "STATE", "POPESTIMATE2019"]]
        .iloc[5:, :]
        .reset_index(drop=True)
    )
    statepop.columns = ["state", "fips", "pop"]

    usa_df = usa_df.merge(statepop, on=["state", "fips"])
    new_df = pd.DataFrame(columns=usa_df.columns)

    for state in usa_df["state"].unique():
        temp_df = usa_df[usa_df["state"] == state].copy()
        temp_df["new_cases"] = temp_df["cases"].diff()
        temp_df["weekly_rolling_new_cases"] = (
            temp_df["new_cases"].rolling(window=7).mean()
        )

        temp_df["new_deaths"] = temp_df["deaths"].diff()
        temp_df["weekly_rolling_new_deaths"] = (
            temp_df["new_deaths"].rolling(window=7).mean()
        )

        new_df = new_df.append(temp_df)

    new_df["cases_per_100k"] = (new_df["cases"] / new_df["pop"]) * 100000
    new_df["deaths_per_100k"] = (new_df["deaths"] / new_df["pop"]) * 100000
    new_df["weekly_rolling_new_cases_per_100k"] = (
        new_df["weekly_rolling_new_cases"] / new_df["pop"]
    ) * 100000
    new_df["weekly_rolling_new_deaths_per_100k"] = (
        new_df["weekly_rolling_new_deaths"] / new_df["pop"]
    ) * 100000

    new_col_names = {
         'people_vaccinated':'one_dose_vaccinated',
         'people_fully_vaccinated':'all_doses_vaccinated',
         'new_vaccinations':'new_doses_administered',
         'new_vaccinations_smoothed':'new_doses_administered_smoothed',
         'people_vaccinated_per_hundred':'one_dose_vaccinated_per_hundred',
         'people_fully_vaccinated_per_hundred':'all_doses_vaccinated_per_hundred',
         'new_vaccinations_smoothed_per_million':'new_doses_administered_smoothed_per_million'
    }
    new_df = new_df.rename(new_col_names, axis=1)
    new_df['region'] = new_df['state'].apply(cat_state)
    return new_df.reset_index(drop=True)


def get_world():
    world_df = pd.read_csv("https://covid.ourworldindata.org/data/owid-covid-data.csv")
    world_df["deaths_per_pos"] = world_df["new_deaths"] / world_df["new_cases"]
    world_df["pos_per_tests"] = world_df["new_cases"] / world_df["new_tests"]
    
    new_world = pd.DataFrame()
    for ctry in world_df['location'].unique():
        temp = world_df[world_df['location']==ctry]
        temp["rolling_pos_per_tests"] = temp["pos_per_tests"].rolling(7).mean()
        new_world = new_world.append(temp)
    # rename columns
    new_col_names = {
         'people_vaccinated':'one_dose_vaccinated',
         'people_fully_vaccinated':'all_doses_vaccinated',
         'new_vaccinations':'new_doses_administered',
         'new_vaccinations_smoothed':'new_doses_administered_smoothed',
         'people_vaccinated_per_hundred':'one_dose_vaccinated_per_hundred',
         'people_fully_vaccinated_per_hundred':'all_doses_vaccinated_per_hundred',
         'new_vaccinations_smoothed_per_million':'new_doses_administered_smoothed_per_million'
    }
    world_df = new_world.rename(new_col_names, axis=1)
    
    return world_df


def app():
    print("downloading usa")
    usa_df = get_usa()

    print("downloading world")
    world_df = get_world()

    engine = sq.create_engine(f"sqlite:///data/covid_db.sqlite")
    print("connecting")
    cnx = engine.connect()
    print("connected!")
    usa_df.to_sql("covid_states", con=cnx, if_exists="replace", index=False)
    print("states saved")
    world_df.to_sql("covid_world", con=cnx, if_exists="replace", index=False)

    print("everything saved!")
    return f"New data saved to the database today ({dt.datetime.now()}!)"


if __name__ == "__main__":
    app()
