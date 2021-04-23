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


def ylabel_format(my_string, ylog):
    if my_string == "rolling_pos_per_tests":
        my_string = "Positivity ratio"
    else:
        my_string = my_string.replace("smoothed_", "").replace("_", " ").capitalize()

    if ylog:
        my_string += " (log)"
    return my_string


def premade(premade_df, plot_selected, date_selected):
    """Presents a couple premade, sanitized graphs"""
    if "Positivity rate" in plot_selected:
        st.info(
            "W.H.O. guidelines recommend a positivity rate of at most __0.05__ for two weeks before nations reopen."
        )

        # cant do log of this data
        ylabel = "rolling_pos_per_tests"
        ylog = False
        st.plotly_chart(
            h.line_plotter(
                "date",
                ylabel,
                date_selected,
                dataset=premade_df,
                hue="location",
                labels={ylabel: ylabel_format(ylabel, ylog), "date": ""},
                title="Positivity rate by location",
                range_y=(0, 0.5),
            ),
            use_container_width=False,
        )
        st.write(
            "The positivity rate is calculated as 'number of positive tests' / 'positive + negative tests'"
        )

    else:
        placeholder = st.empty()
        placeholder.info(
            "__Instructions:__ Move mouse into plot to interact. Drag and select to zoom. Double click to reset. Click the camera to save."
        )
        ylog = st.checkbox("log(y axis)")

        if ylog:
            placeholder.info(
                "The log of these values indicates the speed of transmission, making the flattening of curves more apparent."
            )

        if "New deaths" in plot_selected:
            ylabel = "new_deaths_smoothed_per_million"
            st.plotly_chart(
                h.line_plotter(
                    "date",
                    ylabel,
                    date_selected,
                    dataset=premade_df,
                    hue="location",
                    ylog=ylog,
                    labels={ylabel: ylabel_format(ylabel, ylog), "date": ""},
                    title="New deaths per million by location",
                ),
                use_container_width=False,
            )
        if "New cases" in plot_selected:
            ylabel = "new_cases_smoothed_per_million"
            st.plotly_chart(
                h.line_plotter(
                    "date",
                    ylabel,
                    date_selected,
                    dataset=premade_df,
                    hue="location",
                    ylog=ylog,
                    labels={ylabel: ylabel_format(ylabel, ylog), "date": ""},
                    title="New cases per million by location",
                ),
                use_container_width=False,
            )
        if "Total cases" in plot_selected:
            ylabel = "total_cases_per_million"
            st.plotly_chart(
                h.line_plotter(
                    "date",
                    ylabel,
                    date_selected,
                    dataset=premade_df,
                    hue="location",
                    ylog=ylog,
                    labels={ylabel: ylabel_format(ylabel, ylog), "date": ""},
                    title="Total cases per million by location",
                ),
                use_container_width=False,
            )
        if "Total deaths" in plot_selected:
            ylabel = "total_deaths_per_million"
            st.plotly_chart(
                h.line_plotter(
                    "date",
                    ylabel,
                    date_selected,
                    dataset=premade_df,
                    hue="location",
                    ylog=ylog,
                    labels={ylabel: ylabel_format(ylabel, ylog), "date": ""},
                    title="Total deaths per million by location",
                ),
                use_container_width=False,
            )
        if "Hosp patients per mill" in plot_selected:
            ylabel = "hosp_patients_per_million"
            st.plotly_chart(
                h.line_plotter(
                    "date",
                    ylabel,
                    date_selected,
                    dataset=premade_df,
                    hue="location",
                    ylog=ylog,
                    labels={ylabel: ylabel_format(ylabel, ylog), "date": ""},
                    title="Hospital patients per million by location",
                ),
                use_container_width=False,
            )


def build_own(x_options, y_options, hue_options, date_selected, plt_type="lineplot"):
    """Presents options for user to make own graph, then calls the appropriate plotter()"""
    # webgui

    my_cols = []
    col_x, col_y, col_hue = st.beta_columns(3)
    with col_x:
        x_default = h.find_default(x_options, "date")
        x = st.selectbox(
            "X axis", x_options, format_func=h.str_formatter, index=x_default
        )
        xlog = st.checkbox("log(x axis)")
    with col_y:
        y_default = h.find_default(y_options, "new_cases_smoothed_per_million")
        y = st.selectbox(
            "Y axis", y_options, format_func=h.str_formatter, index=y_default
        )
        ylog = st.checkbox("log(y axis)")
    with col_hue:
        hue_default = h.find_default(hue_options, "location")
        hue = st.selectbox(
            "Group by", hue_options, format_func=h.str_formatter, index=hue_default
        )

    if hue.lower() == "location":
        default_selected = ["Canada", "Hungary", "United States"]

    elif hue.lower() == "continent":
        default_selected = [
            "Africa" "Asia",
            "Europe",
            "North America",
            "Oceania",
            "South America",
        ]
    else:
        default_selected = None

    my_cols.append(x)
    my_cols.append(y)
    my_cols.append(hue)

    df = pd.DataFrame(h.sql_orm_requester(my_cols, table, session))
    byo_df = h.dataset_filterer(df, hue, default_selected=default_selected)

    if plt_type.lower() == "lineplot":
        st.plotly_chart(
            h.line_plotter(
                x, y, date_selected, dataset=byo_df, hue=hue, xlog=xlog, ylog=ylog
            )
        )
    elif plt_type.lower() == "scatterplot":
        st.plotly_chart(
            h.scat_plotter(x, y, dataset=byo_df, hue=hue, xlog=xlog, ylog=ylog)
        )
    else:
        st.plotly_chart(
            h.bar_plotter(x, y, dataset=byo_df, hue=hue, xlog=xlog, ylog=ylog)
        )


def app():
    """
    Covid world webgui
    """
    options = [
        "New cases",
        " New deaths",
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
    premade(premade_df, plot_selected, date_selected)

    session.close()


def other_functions(view_type="Dataset"):
    """
    Deprecated build your own and dataset stuff
    """
    if view_type == "Build Your Own!":
        col_plots, col_dates = st.beta_columns(2)

        with col_plots:
            plt_type = st.selectbox(
                "Plot Type", ["Barplot", "Lineplot", "Scatterplot"], index=1
            )
        with col_dates:
            date_selected = st.date_input(
                "Change the dates?", value=(dt.datetime(2020, 3, 1), dt.datetime.now())
            )
        x_options = []
        y_options = []
        hue_options = []

        x_options += all_columns
        y_options += all_columns
        hue_options += all_columns

        build_own(x_options, y_options, hue_options, date_selected, plt_type)

    if view_type == "Dataset":
        from apps import dataset_viewer as dv

        dv.app(all_columns, table, session)
