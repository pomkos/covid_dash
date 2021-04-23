######################
## Import Libraries ##
######################
import streamlit as st  # webgui

import pandas as pd  # data
import numpy as np  # check if datetime
import datetime as dt  # date
import plotly.express as px  # plots

import sqlalchemy as sq  # sql
import sqlalchemy.orm as sqo  # dynamically select columns
import os  # current directory

import base64
import sys  # for script args

from apps import helpers as h  # helper functions

###################
## Load metadata ##
###################

# connect to db
# engine = sq.create_engine(f'postgres://{us_pw}@{db_ip}:{port}')
engine = sq.create_engine("sqlite:///data/covid_db.sqlite")
cnx = engine.connect()
meta = sq.MetaData()
# get all schemas
meta.reflect(bind=engine)
# select schema
table = meta.tables["covid_world"]
# retreive columns
all_columns = table.columns.keys()
all_columns.sort()

# create session
Session = sqo.sessionmaker(bind=engine)
session = Session()

def app():
    options = [
        "New cases",
        "New deaths",
        "Total cases",
        "Total deaths",
        "Hosp patients per mill",
        "Positivity rate",
    ]
    plot_selected = st.sidebar.selectbox("Select a plot", options, index=0)
    date_selected = st.sidebar.date_input(
        "Change the dates?", value=(dt.datetime(2020, 3, 1), dt.datetime.now())
    )
    if len(date_selected) != 2:
        st.info("Select a beginning and end date")
        st.stop()
    ##### Retrieve #####

    columns = [
        "location",
        "continent",
        "date",
        "hosp_patients_per_million",
        "new_cases_smoothed_per_million",
        "new_deaths_smoothed_per_million",
        "total_cases_per_million",
        "total_deaths_per_million",
        "rolling_pos_per_tests",
    ]

    my_df = pd.DataFrame(h.sql_orm_requester(columns, table, session))
    my_df["date"] = pd.to_datetime(my_df["date"])