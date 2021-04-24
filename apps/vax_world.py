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


def find_xy_annotations(date, location, ylabel, df):
    """
    Finds the x and y values to place annotations in

    input
    ----
    date: str
    location: str
    """
    sig_date = pd.to_datetime(date)
    temp_df = df[(df["location"] == location) & (df["date"] == sig_date)]
    ymax = temp_df[ylabel].max()
    return sig_date, ymax


def annotation_creator(fig, ylabel, df, annotation_settings):
    """
    Adds annotations to plotly figure based on variable input, finds
    coordinates using find_xy_annotations()

    input
    ----
    fig: px.figure
        Figure created via plotly express
    ylabel: str
        Column to grab yaxis values from
    df: pd.DataFrame
        Dataframe to graph
    annotation_settings: dict
        Dictionary with the following keys and values
            dates: list
                List of strings in form of "December 07, 1998"
            location: str
                Location the annotation is relevant for
            titles: list
                List of strings with text the label should show
            hovertexts: list
                List of strings with text the label should show after hovering mouse over the label itself
            ax: int
                Number of pixels to shift annotation on the x axis
            ay: int
                Number of pixels to shift annotation on the y axis
    """
    # get coordinates
    for i in range(len(annotation_settings["dates"])):
        sig_date, ymax = find_xy_annotations(
            date=annotation_settings["dates"][i],
            location=annotation_settings["location"],
            ylabel=ylabel,
            df=df,
        )
        # add the annotation
        fig.add_annotation(
            x=sig_date,
            y=ymax,
            text=annotation_settings["titles"][i],
            showarrow=True,
            arrowhead=2,
            arrowside="end",
            arrowsize=1,
            standoff=2,
            ax=annotation_settings["ax"],
            ay=annotation_settings["ay"],
            hovertext=annotation_settings["hovertexts"][i],
            align="left",
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
    )
    unique_locations = premade_df["location"].unique()

    all_annotations = {}
    if "United States" in unique_locations:
        location = "United States"
        annotations = {
            "location": location,
            "dates": ["April 13, 2021", "April 23, 2021"],
            "titles": ["JJ vaccine <br> paused", "JJ vaccine <br> unpaused"],
            "hovertexts": [
                "CDC and FDA pause distribution <br> of J&J vaccine due to reports of rare blood clots <br> (Centers for Disease Control)",
                "US lifts pause in use of J&J vaccine <br> after vote by expert panel <br> (NPR)",
            ],
            "ax": -30,
            "ay": -70,
        }
        all_annotations[location] = annotations

    if "Canada" in unique_locations:
        location = "Canada"
        annotations = {
            "location": location,
            "dates": ["March 29, 2021"],
            "titles": ["AZ vaccine pause <br> recommended"],
            "hovertexts": [
                "Suspend AstraZeneca use for people under 55, <br> vaccine committee recommends <br> (Canadian Broadcasting Corporation)"
            ],
            "ax": -50,
            "ay": -90,
        }
        all_annotations[location] = annotations
    if "North America" in unique_locations:
        location = "North America"
        annotations = {
            "location": location,
            "dates": ["March 29, 2021", "April 13, 2021", "April 23, 2021"],
            "titles": [
                "AZ vaccine pause <br> recommended",
                "JJ vaccine <br> paused",
                "JJ vaccine <br> unpaused",
            ],
            "hovertexts": [
                "Suspend AstraZeneca use for people under 55, <br> vaccine committee recommends <br> (Canadian Broadcasting Corporation)",
                "CDC and FDA pause distribution <br> of J&J vaccine due to reports of rare blood clots <br> (Centers for Disease Control)",
                "US lifts pause in use of J&J vaccine <br> after vote by expert panel <br> (NPR)",
            ],
            "ax": -30,
            "ay": -70,
        }
        all_annotations[location] = annotations

    if "Europe" in unique_locations:
        location = "Europe"
        annotations = {
            "location": "Europe",
            "dates": ["March 7, 2021", "April 3, 2021"],
            "titles": [
                "Austria suspends <br> AZ use",
                "EMA report <br> released",
            ],
            "hovertexts": [
                """Austria suspends AstraZeneca <br> COVID-19 vaccine batch after death <br> (Reuters)""",
                """EMA finds link to very rare cases of unusual blood clots <br> (European Medicines Agency)""",
            ],
            "ax": 20,
            "ay": -60,
        }
        all_annotations[location] = annotations

    for country in all_annotations.keys():
        st.write(country)
        annotations = all_annotations[country]
        annotation_creator(
            fig=fig, ylabel=ylabel, df=premade_df, annotation_settings=annotations
        )
    info_box.info("__Tip__: Move cursor over annotations for more details")
    st.plotly_chart(fig)


def app():
    options = [
        "Fully vaccinated",
        "Partially vaccinated",
        "New doses administered",
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
