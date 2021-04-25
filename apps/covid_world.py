######################
## Import Libraries ##
######################
import streamlit as st  # webgui

import pandas as pd  # data
import datetime as dt  # date

import sqlalchemy as sq  # sql
import sqlalchemy.orm as sqo  # dynamically select columns

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

def annotation_data(unique_locations):
    '''
    Temporarily stores data for covid annotations, eventually will move to db. See vax_world for vaccine annots.
    '''
    all_annotations = {}
    if "India" in unique_locations:
        location="India"
        annotations = {
            "location": location,
            "dates": ["March 29, 2021"],
            "titles": [
                "Mumbai hospitals <br> under gov ctrl",
            ],
            "hovertexts": [
                """Mumbai put all hospitals and nursing homes under temporary gov control, <br>
                ordered them to discharge asymptomatic patients without comorbidities, <br>
                and instructed private hospitals to reserve ICUs for COVID19 patients <br> (NPR)""",
            ],
            "ax": -30,
            "ay": -70,
        }
        all_annotations[location] = annotations
    if "Hungary" in unique_locations:
        location="Hungary"
        annotations = {
            "location": location,
            "dates": ["April 22, 2021"],
            "titles": [
                "Hungary limited <br> reopening",
            ],
            "hovertexts": [
                "Hungary expected to reopen restaurant terraces as COVID shots accelerate <br> (Reuters)",
            ],
            "ax": -30,
            "ay": -75,
        }
        all_annotations[location] = annotations
    else: # if there are no countries in the db, then return none
        return None
    return all_annotations


def graph_caller(ylabel, date_selected, premade_df, title, ylog=False, yrange = None, hue='location'):
    '''
    Calls h.line_plotter(). Created to avoid repetitive code.
    
    input
    -----
    yrange: tuple
        None or tuple. If tuple, indicates the min and max values for y axis
    '''
    if not yrange: # no limit on the y axis
            fig = h.line_plotter( # h.lineplotter returns a tuple with 1 item, the fig
                "date",
                ylabel,
                date_selected,
                dataset=premade_df,
                hue=hue,
                ylog=ylog,
                labels={ylabel: h.ylabel_format(ylabel, ylog), "date": "", "location":""},
                title=title,
            ),

    else: # y axis is limited by tuple
            fig = h.line_plotter( # h.lineplotter returns a tuple with 1 item, the fig
                "date",
                ylabel,
                date_selected,
                dataset=premade_df,
                hue=hue,
                ylog=ylog,
                range_y=yrange,
                labels={ylabel: h.ylabel_format(ylabel, ylog), "date": "", "location":""},
                title=title,
            ),
    all_locations = premade_df['location'].unique()
    all_annotations = annotation_data(all_locations)

    if not all_annotations: # all_annotations is None, dont call annotation creator
        st.plotly_chart(fig[0])
    else:
        for country in all_annotations.keys():
            h.annotation_creator(fig[0], ylabel, df = premade_df, annotation_settings = all_annotations[country])
        st.plotly_chart(fig[0])


def app():
    """
    Covid world webgui
    """
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
    if "positivity rate" in plot_selected:
        # cant do log of this data, so checkbox not needed
        st.info(
            "W.H.O. guidelines recommend a positivity rate of at most __0.05__ for two weeks before nations reopen."
        )

        ylabel = "rolling_pos_per_tests"
        title="Positivity rate by location"
        graph_caller(ylabel, date_selected, premade_df, title, ylog=False, yrange = (0,0.5))
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

        if "new deaths" in plot_selected:
            ylabel = "new_deaths_smoothed_per_million"
            title="New deaths per million by location"
        elif "new cases" in plot_selected:
            ylabel = "new_cases_smoothed_per_million"
            title="New cases per million by location"
        elif "total cases" in plot_selected:
            ylabel = "total_cases_per_million"
            title="Total cases per million by location"
        elif "total deaths" in plot_selected:
            ylabel = "total_deaths_per_million"
            title="Total deaths per million by location"
        elif "hosp patients per mill" in plot_selected:
            ylabel = "hosp_patients_per_million"
            title="Hospital patients per million by location"
            placeholder.warning("The graph may be blank as not all countries publish hospital data")
        graph_caller(ylabel, date_selected, premade_df, title, ylog=ylog)