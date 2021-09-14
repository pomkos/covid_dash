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
table = meta.tables["covid_states"]
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
        st.info('The CDC [has not defined](https://www.cdc.gov/coronavirus/2019-ncov/communication/vaccination-toolkit.html) a threshold for herd immunity against COVID19, however 70% is cited by the [Mayoclinic](https://www.mayoclinic.org/diseases-conditions/coronavirus/in-depth/herd-immunity-and-coronavirus/art-20486808).')
        fig = h.line_plotter(
            "date",
            ylabel,
            date_selected,
            dataset=premade_df,
            hue="state",
            ylog=ylog,
            range_y=(0, 100),
            labels={
                ylabel: h.ylabel_format(ylabel, ylog),
                "date": "",
                "state": "",
            },
            title=title,
        )
        fig.add_hline(y=70, line_dash='dot', line_color='red', annotation_text='Herd immunity')
        st.plotly_chart(fig, use_container_width=False)
    else:
        st.plotly_chart(
            h.line_plotter(
                "date",
                ylabel,
                date_selected,
                dataset=premade_df,
                hue="state",
                ylog=ylog,
                labels={
                    ylabel: h.ylabel_format(ylabel, ylog),
                    "date": "",
                    "state": "",
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
    fig = px.line(
        data_frame=premade_df,
        x="date",
        y=ylabel,
        range_x=date_selected,
        labels={
            ylabel: h.ylabel_format(ylabel, ylog=False),
            "state": "",
            "date": "",
        },
        color="state",
        title="New doses administered per million"
    )
    unique_states = premade_df["state"].unique()
    st.plotly_chart(fig)

def overview(yesterday, dataframe):
    '''
    Show who's winning the vaccine wars
    '''
    choose = st.sidebar.radio("", options = ["Fully vaccinated", "Partially vaccinated"]).lower()
    top_df = dataframe[dataframe.date.apply(lambda x: True if x.date() == yesterday else False)]
    color = None
    sort = st.checkbox("Sort by region")
    if sort:
        color = 'region'
    if "fully" in choose:
        col = 'all_doses_vaccinated_per_hundred'
        res = top_df.sort_values(col, ascending=False)
        title='Fully vaccinated population'
        description = "__Description:__ Percent of population who are fully vaccinated, whether through one (ex: JJ) or two (ex: Pfizer) doses"

    elif "partially" in choose:
        col = 'one_dose_vaccinated_per_hundred'
        res = top_df.sort_values(col, ascending=False)
        title='At least one dose administered'
        description = "__Description:__ Percent of population who are only partially vaccinated (ex: one dose of Pfizer)"
    res = res[~res['state'].str.contains('Puerto')]
    fig = px.bar(
        data_frame = res,
        x='state',
        y=col,
        color=color,
        range_y=(0,100),
        title=title,
        labels={
            col:h.ylabel_format(col, ylog=False),
            'state':'',
            'region':'Region'
        }
    )

    fig.add_hline(y=70, line_dash='dot', line_color='red', annotation_text='Herd immunity')
    st.plotly_chart(fig)
    st.write("")
    st.write(description)
        
def app():
    options = [
        "Fully vaccinated",
        "Partially vaccinated",
        "New doses administered",
    ]
    plot_selected = st.sidebar.selectbox("Select a plot", options, index=0)

    ##### Retrieve #####

    columns = [
        "state",
        "region",
        "date",
        "total_vaccinations_per_hundred",
        "one_dose_vaccinated_per_hundred",
        'all_doses_vaccinated_per_hundred',
        "weekly_rolling_new_cases_per_100k",
    ]

    my_df = pd.DataFrame(h.sql_orm_requester(columns, table, session))
    session.close()
    my_df.columns = columns

    my_df["date"] = pd.to_datetime(my_df["date"])

    plot_selected = plot_selected.lower()

    date_selected = st.sidebar.date_input(
        "Change the dates?", value=(dt.datetime(2020, 12, 1), dt.datetime.now())
    )
    if len(date_selected) != 2:
        st.info("Select a beginning and end date")
        st.stop()
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

    premade_df = h.dataset_filterer(my_df, "state", default_selected=default)
    if "new doses" in plot_selected:
        # this one gets its own plot. With annotations and hookers!
        ylabel = "weekly_rolling_new_cases_per_100k"
        title = "New doses administered per 100k"
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

    if type(my_info) == str:
        st.info(my_info)
    yesterday = dt.datetime.now().date() - dt.timedelta(days=2)
    st.info('The CDC [has not defined](https://www.cdc.gov/coronavirus/2019-ncov/communication/vaccination-toolkit.html) a threshold for herd immunity against COVID19, however 70% is cited by the [Mayoclinic](https://www.mayoclinic.org/diseases-conditions/coronavirus/in-depth/herd-immunity-and-coronavirus/art-20486808).')
    overview(yesterday, my_df)
    my_info=None