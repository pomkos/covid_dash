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

import base64
import sys # for script args

from apps import helpers as h # helper functions

###################
## Load metadata ##
###################

# connect to db
#engine = sq.create_engine(f'postgres://{us_pw}@{db_ip}:{port}')
engine = sq.create_engine('sqlite:///data/covid_db.sqlite')
cnx = engine.connect()
meta = sq.MetaData()
# get all schemas
meta.reflect(bind=engine)
# select schema
table = meta.tables['covid_world']
# retreive columns
all_columns = table.columns.keys()
all_columns.sort()

# create session
Session = sqo.sessionmaker(bind=engine)
session=Session()

def premade(premade_df, plot_selected, date_selected):
    '''Presents a couple premade, sanitized graphs'''
    
    st.info('__Instructions:__ Move mouse into plot to interact. Drag and select to zoom. Double click to reset. Click the camera to save.')
    if 'Deaths per mill' in plot_selected:
        st.plotly_chart(h.line_plotter('date',
                                     'new_deaths_smoothed_per_million',
                                     date_selected,
                                     dataset = premade_df,
                                     hue='location',
                                     title='Deaths per million by country'),
                        use_container_width = False)
    if 'Cases per mill' in plot_selected:
        st.plotly_chart(h.line_plotter('date',
                                     'new_cases_smoothed_per_million',
                                     date_selected,
                                     dataset = premade_df,
                                     hue='location',
                                     title='Cases per million by country'),
                        use_container_width = False)
    if 'Hosp patients per mill' in plot_selected:
        st.plotly_chart(h.line_plotter('date',
                                     'hosp_patients_per_million',
                                     date_selected,
                                     dataset = premade_df,
                                     hue='location',
                                     title='Hospital patients per million by country'),
                        use_container_width = False)
    if 'Positivity rate' in plot_selected:
        st.plotly_chart(h.line_plotter('date',
                                     'rolling_pos_per_tests',
                                     date_selected,
                                     dataset = premade_df,
                                     hue='location',
                                     title='Positivity rate by country', range_y=(0,0.5)),
                        use_container_width = False)
        st.info('W.H.O. guidelines recommend a positivity rate of at most 0.05 for two weeks before nations reopen.')
    if 'Hospital vs Deaths' in plot_selected:
        st.plotly_chart(h.scat_plotter('new_cases_smoothed_per_million',
                                     'hosp_patients_per_million',
                                     dataset = premade_df,
                                     title='Hospital patients related to new cases',
                                     do_ols='ols',
                                     hue='location'), 
                        use_container_width = False)
            
def build_own(x_options,y_options,hue_options,date_selected,plt_type='lineplot'):
    '''Presents options for user to make own graph, then calls the appropriate plotter()'''
    # webgui
    
    my_cols = []
    col_x, col_y, col_hue = st.beta_columns(3)
    with col_x:
        x_default = h.find_default(x_options,'date')
        x = st.selectbox('X axis',x_options, format_func = h.str_formatter, index=x_default)
        xlog = st.checkbox('log(x axis)')
    with col_y:
        y_default = h.find_default(y_options, "new_cases_smoothed_per_million")
        y = st.selectbox('Y axis',y_options, format_func = h.str_formatter, index=y_default)
        ylog = st.checkbox('log(y axis)')
    with col_hue:
        hue_default = h.find_default(hue_options,'location')
        hue = st.selectbox('Group by',hue_options, format_func = h.str_formatter, index=hue_default)

    if hue.lower() == 'location':
        default_selected = ['Canada','Hungary','United States']
    
    elif hue.lower() == 'continent':
        default_selected = ['Africa'
                            'Asia',
                            'Europe',
                            'North America',
                            'Oceania',
                            'South America'
                            ]
    else:
        default_selected = None
        
    my_cols.append(x)
    my_cols.append(y)
    my_cols.append(hue)
    
    df = pd.DataFrame(h.sql_orm_requester(my_cols, table, session))
    byo_df = h.dataset_filterer(df, hue, default_selected=default_selected)
    
    if plt_type.lower() == 'lineplot':
        st.plotly_chart(h.line_plotter(x,y,date_selected,dataset=byo_df,hue=hue,xlog=xlog,ylog=ylog))
    elif plt_type.lower() == 'scatterplot':        
        st.plotly_chart(h.scat_plotter(x,y,dataset=byo_df,hue=hue,xlog=xlog,ylog=ylog))
    else:
        st.plotly_chart(h.bar_plotter(x,y,dataset=byo_df,hue=hue,xlog=xlog,ylog=ylog))

def app():
    '''
    Covid world webgui
    '''
    view_type = st.select_slider("",options=('Premade Plots','Build Your Own!','Dataset'))
    if view_type == "Premade Plots":
        col_sel, col_date = st.beta_columns(2)
        with col_sel:
            options = ['Cases per mill','Deaths per mill','Hosp patients per mill','Hospital vs Deaths','Positivity rate']
            plot_selected = st.selectbox('Select a plot',options,index=0)        
        with col_date:
            date_selected = st.date_input('Change the dates?', value=(dt.datetime(2020,3,1),dt.datetime.now()))
        if len(date_selected) != 2:
            st.info("Select a beginning and end date")
            st.stop()
        ##### Retrieve #####
        
        columns = ['location','continent','date','hosp_patients_per_million',
                   'new_cases_smoothed_per_million','new_deaths_smoothed_per_million',
                   'rolling_pos_per_tests']

        my_df=pd.DataFrame(h.sql_orm_requester(columns, table, session))
        my_df['date'] = pd.to_datetime(my_df['date'])
        
        if st.checkbox("Hungary and surrounding countries only"):
            default = ['Hungary','Slovakia','Austria','Slovenia',
                       'Croatia','Serbia','Romania','Ukraine']
            default.sort()
        else:
            default = ['Canada', 'Hungary', 'Mexico','United States']
            
        premade_df = h.dataset_filterer(my_df, 'location', default_selected = default)
        premade(premade_df, plot_selected, date_selected)
        
    if view_type == "Build Your Own!":
        col_plots, col_dates = st.beta_columns(2)
        
        with col_plots:
            plt_type = st.selectbox('Plot Type',['Barplot','Lineplot','Scatterplot'], index=1)
        with col_dates:
            date_selected = st.date_input('Change the dates?', value=(dt.datetime(2020,3,1),dt.datetime.now()))
        x_options = []
        y_options = []
        hue_options = []

        x_options += all_columns
        y_options += all_columns
        hue_options += all_columns

        build_own(x_options,y_options,hue_options,date_selected, plt_type)
        
    if view_type == "Dataset":
        from apps import dataset_viewer as dv
        dv.app(all_columns, table, session)
    session.close()