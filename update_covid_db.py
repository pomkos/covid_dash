import pandas as pd
import sqlalchemy as sq
import datetime as dt
import os
import sys


def get_usa():
    """
    Download new data, merge with pop, calculate new variables
    """
    usa_df = pd.read_csv(
        "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv"
    )
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

    return new_df.reset_index(drop=True)


def get_world():
    world_df = pd.read_csv("https://covid.ourworldindata.org/data/owid-covid-data.csv")
    world_df["deaths_per_pos"] = world_df["new_deaths"] / world_df["new_cases"]
    world_df["pos_per_tests"] = world_df["new_cases"] / world_df["new_tests"]
    world_df["rolling_pos_per_tests"] = world_df["pos_per_tests"].rolling(7).mean()
    
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
    world_df = world_df.rename(new_col_names, axis=1)
    
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
