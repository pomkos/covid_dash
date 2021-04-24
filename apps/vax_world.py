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

def graph_caller(ylabel, date_selected, premade_df, title, ylog=False):
    '''
    Calls h.line_plotter(). Created to avoid repetitive code.
    '''
    st.plotly_chart(
        h.line_plotter(
            "date",
            ylabel,
            date_selected,
            dataset=premade_df,
            hue="location",
            ylog=ylog,
            labels={ylabel: h.ylabel_format(ylabel, ylog), "date": ""},
            title=title,
        ),
        use_container_width=False,
    )

def app():
    options = [
        "New doses administered",
        "Fully vaccinated",
        "Partially vaccinated",
        "All vaccinations",
    ]
    plot_selected = st.sidebar.selectbox("Select a plot", options, index=0)
    date_selected = st.sidebar.date_input(
        "Change the dates?", value=(dt.datetime(2020, 12, 1), dt.datetime.now())
    )
    if len(date_selected) != 2:
        st.info("Select a beginning and end date")
        st.stop()
    ##### Retrieve #####

    columns = [
        "location",
        "continent",
        "date",

        'total_vaccinations_per_hundred',
        "one_dose_vaccinated_per_hundred",
        "all_doses_vaccinated_per_hundred",
        'new_doses_administered_smoothed_per_million'
    ]

    my_df = pd.DataFrame(h.sql_orm_requester(columns, table, session))
    session.close()

    my_df["date"] = pd.to_datetime(my_df["date"])

    # st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
    region_options = ["Default", "Continents"]
    regions = ["North America", "West Europe", "East Europe", "Nordics", "Asia"]
    regions.sort()
    region_options = region_options + regions

    region = st.sidebar.radio("Preset locations", options=region_options, index=0)

    if region == "North America":
        default = ["Canada", "United States", "Mexico"]

    elif region == "Nordics":
        default = ["Sweden", "Finland", "Norway"]

    elif region == "West Europe":
        default = [
            "Austria",
            "Belgium",
            "France",
            "Germany",
            "Spain",
            "United Kingdom",
            "Portugal",
            "Netherlands",
            "Switzerland",
        ]

    elif region == "East Europe":
        default = [
            "Hungary",
            "Slovakia",
            "Austria",
            "Slovenia",
            "Croatia",
            "Serbia",
            "Romania",
            "Ukraine",
        ]

    elif region == "Continents":
        default = [
            "Europe",
            "North America",
            "South America",
            "Africa",
            "Asia",
            "Australia",
        ]

    elif region == "Asia":
        default = ["Japan", "South Korea", "Thailand", "India"]
        st.sidebar.info(
            "__Note__: China not included by default due to low reported numbers"
        )

    else:
        default = ["Canada", "Hungary", "United States"]
    default.sort()

    premade_df = h.dataset_filterer(my_df, "location", default_selected=default)

    plot_selected = plot_selected.lower()
    if "new doses" in plot_selected:
        ylabel = "new_doses_administered_smoothed_per_million"
        title = "New doses administered per million"
        graph_caller(ylabel, date_selected, premade_df, title)
    elif "fully vacc" in plot_selected:
        ylabel = "all_doses_vaccinated_per_hundred"
        title = "Fully vaccinated population per country"
        graph_caller(ylabel, date_selected, premade_df, title)
    elif "partially vacc" in plot_selected:
        ylabel = "one_dose_vaccinated_per_hundred"
        title = "Partially vaccinated population per country"
        graph_caller(ylabel, date_selected, premade_df, title)
    elif "all vacc" in plot_selected:
        ylabel = "all_doses_vaccinated_per_hundred"
        title = "Total doses administered per country"
        graph_caller(ylabel, date_selected, premade_df, title)
