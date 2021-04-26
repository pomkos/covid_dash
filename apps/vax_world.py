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

# connect to db
# engine = sq.create_engine(f'postgres://{us_pw}@{db_ip}:{port}')
engine = sq.create_engine("sqlite:///data/covid_db.sqlite", connect_args={"check_same_thread": False})
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

# connect to news engine
news_engine = sq.create_engine("sqlite:///data/covid_news.db", connect_args={"check_same_thread": False})
news_cnx = news_engine.connect()


def graph_caller(
    ylabel, date_selected, premade_df, title, ylog=False, perc_range=False
):
    """
    Calls h.line_plotter(). Created to avoid repetitive code.
    """
    if perc_range:
        st.plotly_chart(
            h.line_plotter(
                "date",
                ylabel,
                date_selected,
                dataset=premade_df,
                hue="location",
                ylog=ylog,
                range_y=(0, 100),
                labels={
                    ylabel: h.ylabel_format(ylabel, ylog),
                    "date": "",
                    "location": "",
                },
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
                hue="location",
                ylog=ylog,
                labels={
                    ylabel: h.ylabel_format(ylabel, ylog),
                    "date": "",
                    "location": "",
                },
                title=title,
            ),
            use_container_width=False,
        )

def graph_new_doses(ylabel, date_selected, premade_df, title):
    """
    Sole function to graph new doses and call functions to add annotations to the graph

    Source for annotations: https://plotly.com/python/reference/layout/annotations
    """
    info_box = st.empty()
    fig = px.line(
        data_frame=premade_df,
        x="date",
        y=ylabel,
        range_x=date_selected,
        labels={
            ylabel: h.ylabel_format(ylabel, ylog=False),
            "location": "",
            "date": "",
        },
        color="location",
        title="New doses administered per million"
    )
    unique_locations = premade_df["location"].unique()

    all_annotations = h.get_annotation_data(unique_locations, label='vax', conn=news_cnx)
    if not all_annotations:
        st.plotly_chart(fig)
    else:
        for country in all_annotations.keys():
            h.annotation_creator( # add annotations to the graph
                fig=fig, ylabel=ylabel, df=premade_df, annotation_settings=all_annotations[country]
            )
        info_box.info("__Tip__: Move cursor over annotations for more details")
        st.plotly_chart(fig)

def app():
    options = [
        "New doses administered",
        "Fully vaccinated",
        "Partially vaccinated",
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
        "total_vaccinations_per_hundred",
        "one_dose_vaccinated_per_hundred",
        "all_doses_vaccinated_per_hundred",
        "new_doses_administered_smoothed_per_million",
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
        # this one gets its own plot. With annotations and hookers!
        ylabel = "new_doses_administered_smoothed_per_million"
        title = "New doses administered per million"
        graph_new_doses(ylabel, date_selected, premade_df, title)
        my_info = "__Description:__ New doses administered this week, regardless of vaccine brand or type"
    else:
        if "fully vacc" in plot_selected:
            ylabel = "all_doses_vaccinated_per_hundred"
            title = "Percent population fully vaccinated"
            perc_range = True
            my_info = "__Description:__ Percent of population who are fully vaccinated, whether through one (ex: JJ) or two (ex: Pfizer) doses"
        elif "partially vacc" in plot_selected:
            ylabel = "one_dose_vaccinated_per_hundred"
            title = "Percent population partially vaccinated"
            perc_range = True
            my_info = "__Description:__ Percent of population who are only partially vaccinated (ex: one dose of Pfizer)"
        elif (
            "all doses" in plot_selected
        ):  # deprecated. shows USA as 60% vaxxed, which is clearly wrong ...
            ylabel = "total_vaccinations_per_hundred"
            title = "Percent population with at least one dose administered"
            perc_range = True
            my_info = "__Description:__ Percent of population who received at least one dose, including fully dosed populations"

        graph_caller(ylabel, date_selected, premade_df, title, perc_range=perc_range)
    st.info(my_info)
