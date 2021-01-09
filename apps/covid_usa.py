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
    if 'Change in Cases' in plot_selected:
        st.plotly_chart(h.line_plotter('date',
                                     'positiveIncrease',
                                     date_selected,
                                     dataset = premade_df,
                                     hue='state',
                                     title='Change in cases by state'),
                        use_container_width = False)
    if 'Change in Deaths' in plot_selected:
        st.plotly_chart(h.line_plotter('date',
                                     'deathIncrease',
                                     date_selected,
                                     dataset = premade_df,
                                     hue='state',
                                     title='Change in deaths by state'),
                        use_container_width = False)
    if 'Hospitalized' in plot_selected:
        st.plotly_chart(h.line_plotter('date',
                                     'hospitalizedCurrently',
                                     date_selected,
                                     dataset = premade_df,
                                     hue='state',
                                     title='Currently hospitalized patients by state'),
                        use_container_width = False)
    if 'Positivity Rate' in plot_selected:
        st.plotly_chart(h.line_plotter('date',
                                     'pos_per_tests',
                                     date_selected,
                                     dataset = premade_df,
                                     hue='state',
                                     title='Positivity rate by state', range_y=(0,0.5)),
                        use_container_width = False)
        st.info('W.H.O. guidelines recommend a positivity rate of at most 0.05 for two weeks before nations reopen.')
    if 'Hospital vs Deaths' in plot_selected:
        st.plotly_chart(h.scat_plotter('deathIncrease',
                                     'hospitalizedCurrently',
                                     dataset = premade_df,
                                     title='Hospital patients related to new cases',
                                     do_ols='ols',
                                     hue='state'), 
                        use_container_width = False)

def app():
    options = ['Change in Cases','Change in Deaths','Hospitalized', 'Positivity Rate', "Hospital vs Deaths"]
    
    colb, cold = st.beta_columns(2)
    
    with colb:
        plot_selected = st.selectbox('Select a plot',options,index=0) 
    with cold:
        date_selected = st.date_input('Change the dates?', value=(dt.datetime(2020,3,1),dt.datetime.now()))

    if len(date_selected) != 2:
        st.info("Select a beginning and end date")
        st.stop()

    premade_cols = ['date','state',
                    'positive','positiveIncrease',
                    'hospitalizedCurrently','hospitalizedIncrease',
                    'inIcuCurrently',
                    'death', 'deathIncrease','pos_per_tests']

    resultset = h.sql_orm_requester(premade_cols,table, session)
    my_df = pd.DataFrame(resultset)
    my_df['date'] = pd.to_datetime(my_df['date'])

    premade_df = h.dataset_filterer(my_df, 'state',default_selected = ['OH','TX','FL'])

    premade(premade_df, plot_selected, date_selected)

    ######################################

