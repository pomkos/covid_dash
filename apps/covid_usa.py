######################
## Import Libraries ##
######################
import streamlit as st # webgui

import pandas as pd # data
import numpy as np # check if datetime
import datetime as dt # date
import plotly.express as px # plots

import sqlalchemy as sq # sql
import sqlalchemy.orm as sqo # dynamically select columns
import os # current directory

from apps import helpers as h # helper functions

# connect to db
#engine = sq.create_engine(f'postgres://{us_pw}@{db_ip}:{port}')
engine = sq.create_engine('sqlite:///data/covid_db.sqlite')
cnx = engine.connect()
meta = sq.MetaData()
# get all schemas
meta.reflect(bind=engine)
# select schema
table = meta.tables['covid_states']
# retreive columns
all_columns = table.columns.keys()
all_columns.sort()

# create session
Session = sqo.sessionmaker(bind=engine)
session=Session()

st.title("Covid USA Test")
############ TESTING AREA ############

def premade(premade_df, plot_selected, date_selected):
    '''Presents a couple premade, sanitized graphs'''
    
    st.info('__Instructions:__ Move mouse into plot to interact. Drag and select to zoom. Double click to reset. Click the camera to save.')
    ylog = st.checkbox('log(y axis)')

    if 'Change in Cases' in plot_selected:
        st.plotly_chart(h.line_plotter('date',
                                     'weekly_rolling_new_cases',
                                     date_selected,
                                     dataset = premade_df,
                                     hue='state',
                                     ylog=ylog,
                                     labels={'weekly_rolling_new_cases':'Weekly new cases',
                                             'date':''},
                                     title='Change in mean weekly cases by state'),
                        use_container_width = False,)
    if 'Change in Deaths' in plot_selected:
        st.plotly_chart(h.line_plotter('date',
                                     'weekly_rolling_new_deaths',
                                     date_selected,
                                     dataset = premade_df,
                                     hue='state',
                                     ylog=ylog,
                                     labels={'weekly_rolling_new_deaths':'Weekly new deaths',
                                             'date':''},
                                     title='Change in mean weekly deaths by state'),
                        use_container_width = False)
    if 'Total Cases' in plot_selected:
        st.plotly_chart(h.line_plotter('date',
                                     'cases',
                                     date_selected,
                                     dataset = premade_df,
                                     hue='state',
                                     ylog=ylog,
                                     title='Total cases by state'),
                        use_container_width = False)

def app():
    options = ['Change in Cases','Change in Deaths','Total Cases']
    
    colb, cold = st.beta_columns(2)
    
    with colb:
        plot_selected = st.selectbox('Select a plot',options,index=0) 
    with cold:
        date_selected = st.date_input('Change the dates?', value=(dt.datetime(2020,3,1),dt.datetime.now()))

    if len(date_selected) != 2:
        st.info("Select a beginning and end date")
        st.stop()

    premade_cols = ['date', 'state', 'fips', 'cases', 'deaths', 'new_cases',
                    'weekly_rolling_new_cases', 'monthly_rolling_new_cases',
                    'new_deaths', 'weekly_rolling_new_deaths', 'monthly_rolling_new_deaths']

    resultset = h.sql_orm_requester(premade_cols,table, session)
    my_df = pd.DataFrame(resultset)
    my_df['date'] = pd.to_datetime(my_df['date'])

    premade_df = h.dataset_filterer(my_df, 'state', default_selected = ['Ohio','Texas','Florida'])

    premade(premade_df, plot_selected, date_selected)
    session.close()

