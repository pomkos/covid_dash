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

from apps import helpers as h  # helper functions

# connect to db
# engine = sq.create_engine(f'postgres://{us_pw}@{db_ip}:{port}')
engine = sq.create_engine("sqlite:///data/covid_db.sqlite")
cnx = engine.connect()
meta = sq.MetaData()
# get all schemas
meta.reflect(bind=engine)
# select schema
table = meta.tables["covid_states"]
# retreive columns
all_columns = table.columns.keys()
all_columns.sort()

# create session
Session = sqo.sessionmaker(bind=engine)
session = Session()

def graph_caller(ylabel, date_selected, premade_df, title, ylog=False, yrange = None, hue='state'):
    '''
    Calls h.line_plotter(). Created to avoid repetitive code.
    
    input
    -----
    yrange: tuple
        None or tuple. If tuple, indicates the min and max values for y axis
    '''
    if not yrange:
        st.plotly_chart(
            h.line_plotter(
                "date",
                ylabel,
                date_selected,
                dataset=premade_df,
                hue=hue,
                ylog=ylog,
                labels={ylabel: h.ylabel_format(ylabel, ylog), "date": "", "state":""},
                title=title,
            ),
            use_container_width=False,
        )
    else:
        st.plotly_chart(
            h.line_plotter(
                "date",
                ylabel,
                date_selected,
                dataset=premade_df,
                hue=hue,
                ylog=ylog,
                range_y=yrange,
                labels={ylabel: h.ylabel_format(ylabel, ylog), "date": "", "state":""},
                title=title,
            ),
            use_container_width=False,
        )

def app():
    options = ["Change in cases", "Change in deaths", "Total cases", "Total deaths"]

    plot_selected = st.sidebar.selectbox("Select a plot", options, index=0)
    date_selected = st.sidebar.date_input(
        "Change the dates?", value=(dt.datetime(2020, 3, 1), dt.datetime.now())
    )

    if len(date_selected) != 2:
        st.info("Select a beginning and end date")
        st.stop()

    premade_cols = [
        "date",
        "state",
        "region",
        "fips",
        "cases",
        "deaths",
        "new_cases",
        "deaths_per_100k",
        "weekly_rolling_new_cases",
        "weekly_rolling_new_cases_per_100k",
        "cases_per_100k",
        "new_deaths",
        "weekly_rolling_new_deaths",
        "weekly_rolling_new_deaths_per_100k",
    ]

    resultset = h.sql_orm_requester(premade_cols, table, session)
    session.close()
    my_df = pd.DataFrame(resultset)
    my_df["date"] = pd.to_datetime(my_df["date"])
    
    region_options = ["Default", "Regions"]
    regions = [r for r in my_df['region'].unique() if r != None]
    regions.sort()
    region_options = region_options + regions
    region = st.sidebar.radio("Preset states", options=region_options, index=0)

    if region == 'Default':
        default = ['Ohio','Texas']
    elif region == 'Regions':
        my_df = my_df.groupby(['date','region']).mean().reset_index()
        my_df = my_df.rename({'region':'state'}, axis=1) # rename so I dont have to change code hehehe
        default = regions
    else:
        # get all the states that belong in that region
        default = list(my_df[my_df['region'] == region]['state'].unique())

    premade_df = h.dataset_filterer(
        my_df, "state", default_selected=default
    )

    placeholder = st.empty()
    placeholder.info(
        "__Instructions:__ Move mouse into plot to interact. Drag and select to zoom. Double click to reset. Click the camera to save."
    )
    ylog = st.checkbox("log(y axis)")
    if ylog:
        placeholder.info(
            "The log of these values indicates the speed of transmission, making the flattening of curves more apparent."
        )
    plot_selected = plot_selected.lower()
    if "change in cases" in plot_selected:
        ylabel = "weekly_rolling_new_cases_per_100k"
        title = "New weekly cases by state"
    elif "change in deaths" in plot_selected:
        ylabel = "weekly_rolling_new_deaths_per_100k"
        title = "New weekly deaths by state"
    elif "total cases" in plot_selected:
        ylabel = "cases_per_100k"
        title = "Total cases by state"
    elif "total deaths" in plot_selected:
        ylabel = "deaths_per_100k"
        title = "Total deaths by state"
    graph_caller(ylabel, date_selected, premade_df, title, ylog=ylog)