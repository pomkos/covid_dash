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
                                     'positive_rate',
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
        default_selected = ['North America',
                            'Asia',
                            'Africa',
                            'Europe',
                            'South America',
                            'Oceania']
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

def view_dataset(columns=None):
    '''View the dataset, certain or all columns'''
    if columns == None:
        columns = ['All'] + all_columns

    with st.beta_expander('Settings',expanded=True):
        column_choices = st.multiselect('Select variables',
                                        columns,
                                        default = ['location','date','new_cases_per_million', 
                                                   'new_deaths_per_million', 'population',
                                                   'population_density'],
                                        format_func=h.str_formatter)
        dataset = pd.DataFrame(h.sql_orm_requester(column_choices, table, session))
        
        if 'date' not in column_choices:
            st.error('As the dataset is in the time domain, "Date" must be passed')
            st.stop()

        if 'location' in column_choices: # only show option if needed
            countries = list(dataset['location'].unique())
            countries.sort()
            countries = ['All'] + countries
            ctry_choices = st.multiselect('Select countries of interest',
                              countries,
                              default = ['United States','Hungary'])
            if 'All' in ctry_choices:
                ctry_choices = list(dataset['location'].unique())
            dataset = dataset[dataset['location'].isin(ctry_choices)] # filter column to just selected countries
            
        if 'All' in column_choices:
            column_choices = all_columns
            
        col_date_df, col_group,col_grp_desc = st.beta_columns(3)

        with col_date_df:
            date_range_choices = st.date_input('Change the dates?', value=(dt.datetime(2020,1,1),dt.datetime.now()),key='chg_dts_df')
            show_df = dataset[column_choices]
            show_df['date'] = pd.to_datetime(show_df['date'])
            show_df = show_df[(show_df['date']>=pd.to_datetime(date_range_choices[0])) & 
                              (show_df['date']<=pd.to_datetime(date_range_choices[1]))]
        with col_group:
            group_choices = st.multiselect('What should we groupby?',
                                           ['Nothing'] + column_choices,
                                           format_func=h.str_formatter,default=['Nothing'])
        with col_grp_desc:
            group_desc = st.selectbox('How should each variable be grouped?',['Raw value','Mean','Median','Sum','Min','Max'])
        
        ##### Graph too? #####
        graph_me = st.radio('Show me the',['Dataset only','Dataset and graph'])
        ######################
        
        if len(column_choices) > 10:
            st.warning(f"WARNING: Loading {len(column_choices)} variables will load {round(len(column_choices)/len(dataset.columns) * 100)}% of the dataset.")
            col_allcont, col_allcanc = st.beta_columns(2)
            with col_allcont:
                all_continue = st.button('Continue')
            if all_continue == False:
                st.stop()
            else:
                pass        
        if ('Nothing' in group_choices):
            show_df = show_df
            st.warning(f"To save on memory, current settings will only load the first 20 rows of the dataset")
            nothing_continue = st.button('Continue')
            if nothing_continue == False:
                st.stop()
        else:
            if ('Raw' in group_desc) & (sum(pd.Series(group_choices).str.contains('Nothing')) == 0):
                st.error(f'ERROR: A grouping statistic must be picked to group by {[h.str_formatter(x) for x in group_choices]}')
                st.stop()
            if 'Mean' in group_desc:
                show_df = show_df.groupby(group_choices).mean()
            if 'Median' in group_desc:
                show_df = show_df.groupby(group_choices).median()
            if 'Sum' in group_desc:
                show_df = show_df.groupby(group_choices).sum()
            if 'Min' in group_desc:
                show_df = show_df.groupby(group_choices).min()
            if 'Max' in group_desc:
                show_df = show_df.groupby(group_choices).max()
    import time
    with st.spinner(text='Loading ...'):
        time.sleep(1)
        if ('Nothing' in group_choices):
            st.table(show_df.head(20))
            st.success(f'Showing the requested table!')
        else:
            st.table(show_df)
            st.success(f'Grouped each of {[h.str_formatter(x) for x in group_choices]} by {group_desc}!')
        
    if "graph" in graph_me.lower():
        y_options = list(show_df.columns)
        show_df = show_df.reset_index()
        x_options = y_options
        hue_options = ['Nothing'] + x_options

        col_gr_chc, col_gr_var, col_gr_txt = st.beta_columns(3)       
        with col_gr_chc:
            graph_type = st.radio('Type of Graph',['Bar graph','Line graph','Scatterplot'])

        with col_gr_var:
            x = st.selectbox('X axis',x_options,format_func=h.str_formatter)
            y = st.selectbox('Y axis',y_options,format_func=h.str_formatter)
            
        with col_gr_txt:
            hue = st.selectbox('Color by',hue_options,format_func=h.str_formatter)
            title = st.text_input('Title')
            
            if hue.lower() == 'nothing':
                hue = None
            if not title:
                st.info('Please enter a title')
                st.stop()
            
        if 'bar ' in graph_type.lower():
            st.plotly_chart(h.bar_plotter(show_df, x, y, hue, title=title))
        if 'line ' in graph_type.lower():
            st.plotly_chart(h.line_plotter(show_df, x, y, hue, title=title))
        if 'scatter' in graph_type.lower():
            with col_gr_chc:
                show_ols = st.checkbox('Do regression')
            if show_ols:
                regress = 'ols'
                st.write(regress)
            else:
                regress = None
            st.plotly_chart(h.scat_plotter(show_df, x, y, hue, title=title, do_ols=regress))
            
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
        
        columns = ['location','date','hosp_patients_per_million',
                   'new_cases_smoothed_per_million','new_deaths_smoothed_per_million',
                   'positive_rate']

        my_df=pd.DataFrame(h.sql_orm_requester(columns, table, session))
        my_df['date'] = pd.to_datetime(my_df['date'])
        
        premade_df = h.dataset_filterer(my_df, 'location',default_selected = ['Hungary','Mexico','United States'])
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
        st.write('to be implemented')
        view_dataset()