######################
## Import Libraries ##
######################
import streamlit as st # webgui

import pandas as pd # data
import numpy as np # check if datetime
import datetime as dt # date
import plotly.express as px # plots

import sqlalchemy as sq # sql
import os # current directory

###############
## Load data ##
###############

parent = os.path.dirname(os.getcwd()) # get parent of current directory
#########################################################################
engine = sq.create_engine(f'sqlite:///data/covid.db')
#########################################################################
cnx = engine.connect()
meta = sq.MetaData()

raw_request = '''
SELECT *
FROM covid_world
'''

ResultSet = cnx.execute(raw_request).fetchall()
df=pd.DataFrame(ResultSet)
df.columns=ResultSet[0].keys()
df['date'] = pd.to_datetime(df['date'])
cols = list(df.columns)
cols.sort()
df = df[cols]

########################
### HELPER FUNCTIONS ###
########################

def str_formatter(my_str):
    '''
    To make choices and axes pretty
    '''
    return my_str.replace('_',' ').capitalize()

def find_default(my_list, my_string):
    '''Finds the index of some column in a list'''
    for i,obj in enumerate(my_list):
        if obj.lower() == my_string:
            my_index = i
    return my_index

def hue_formatter(x,y,hue):
    if hue == None:
        labels = {
                  x: str_formatter(x),
                  y: str_formatter(y),
                  #hue:str_formatter(hue)
              }
    else:
        labels = {
                  x: str_formatter(x),
                  y: str_formatter(y),
                  hue:str_formatter(hue)
              }
    return labels

def dataset_filterer(dataset, col, default_selected=None):
    '''
    Returns the dataset filtered by user's choice of unique values from given column
    '''
    options = list(dataset[col].unique())
    options.sort()
    chosen = st.multiselect(f'Select {col}s',
                          options,
                          default = default_selected
                         )
    new_df = dataset[dataset[col].isin(chosen)]
    return new_df

######################
### PLOT FUNCTIONS ###
######################

def scat_plotter(x,y,dataset=df,hue=None,xlog=False,ylog=False,title=None, do_ols=None):
    '''Plotly plots a scatterplot'''
    if title == None:
        title= f'{str_formatter(y)} vs {str_formatter(x)}'
    labels = hue_formatter(x,y,hue)
    my_plot = px.scatter(dataset,
                         x= x,
                         log_x=xlog,
                         log_y=ylog,
                         title=title,
                         # range_x =,
                         y= y,
                         color=hue,
                         trendline=do_ols,
                         labels=labels)
    return my_plot

def line_plotter(x,y,date_selected, dataset=df,hue=None,xlog=False,ylog=False,title=None):
    '''Plotly plots a lineplot'''
    if title == None:
        title= f'{str_formatter(y)} vs {str_formatter(x)}'
    labels = hue_formatter(x,y,hue)
    my_plot = px.line(data_frame=dataset,
                      x= x,
                      log_x = xlog,
                      log_y = ylog,
                      y= y,
                      title = title,
                      range_x = date_selected,
                      color=hue,
                      labels=labels
                     )
    return my_plot

def bar_plotter(x, y,dataset=df, hue=None,xlog=False,ylog=False,title=None):
    '''Plotly plots a barplot'''
    labels = hue_formatter(x,y,hue)
    my_plot = px.bar(
        data_frame = dataset,
        x = x,
        log_x = xlog,
        y = y,
        color = hue,
        log_y = ylog,
        title = title,
        barmode = 'group', # group, overlay, relative
        labels = labels)
    return my_plot

################
### MAIN APP ###
################
def premade(plot_selected, date_selected):
    '''Presents a couple premade, sanitized graphs'''
    premade_df = df[(df['location']=='Hungary') | (df['location']=='United States') | (df['location']=='Brazil') | (df['location']=='India')]
    if 'Deaths per mill' in plot_selected:
        st.plotly_chart(line_plotter('date',
                                     'new_deaths_smoothed_per_million',
                                     date_selected,
                                     dataset = premade_df,
                                     hue='location',
                                     title='Deaths per million by country'),
                        use_container_width = False)
    if 'Hosp patients per mill' in plot_selected:
        st.plotly_chart(line_plotter('date',
                                     'hosp_patients_per_million',
                                     date_selected,
                                     dataset = premade_df,
                                     hue='location',
                                     title='Hospital patients per million by country'),
                        use_container_width = False)
    if 'Positivity rate' in plot_selected:
        st.plotly_chart(line_plotter('date',
                                     'positive_rate',
                                     date_selected,
                                     dataset = premade_df,
                                     hue='location',
                                     title='Positivity rate by country'),
                        use_container_width = False)
    if 'Hospital vs Deaths' in plot_selected:
        st.plotly_chart(scat_plotter('new_cases_smoothed_per_million',
                                     'hosp_patients_per_million',
                                     dataset = premade_df,
                                     title='Hospital patients related to new cases',
                                     do_ols='ols',
                                     hue='location'), 
                        use_container_width = False)
        
    update = st.button('Update Database')
    if update == True:
        import update_covid_db as ucd
        with st.spinner('Beaming the bytes  ...'):
            result = ucd.app()
            st.success(result)
            
def build_own(x_options,y_options,hue_options,date_selected,plt_type='lineplot'):
    '''Presents options for user to make own graph, then calls line_plotter()'''
    # webgui
    col_x, col_y, col_hue = st.beta_columns(3)
    with col_x:
        x_default = find_default(x_options,'date')
        x = st.selectbox('X axis',x_options, format_func = str_formatter, index=x_default)
        xlog = st.checkbox('log(x axis)')
    with col_y:
        y_default = find_default(y_options, "new_cases_smoothed_per_million")
        y = st.selectbox('Y axis',y_options, format_func = str_formatter, index=y_default)
        ylog = st.checkbox('log(y axis)')
    with col_hue:
        hue_default = find_default(hue_options,'location')
        hue = st.selectbox('Group by',hue_options, format_func = str_formatter, index=hue_default)

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
        
    byo_df = dataset_filterer(df, hue, default_selected=default_selected)
    
    if plt_type.lower() == 'lineplot':
        st.plotly_chart(line_plotter(x,y,date_selected,dataset=byo_df,hue=hue,xlog=xlog,ylog=ylog))
    elif plt_type.lower() == 'scatterplot':
        
        st.plotly_chart(scat_plotter(x,y,dataset=byo_df,hue=hue,xlog=xlog,ylog=ylog))
    else:
        st.plotly_chart(bar_plotter(x,y,dataset=byo_df,hue=hue,xlog=xlog,ylog=ylog))

def view_dataset(dataset, columns=None):
    '''View the dataset, certain or all columns'''
    if columns == None:
        columns = ['All'] + list(dataset.columns)
    columns.sort()
    with st.beta_expander('Settings',expanded=True):
        column_choices = st.multiselect('Select variables',
                                        columns,
                                        default = ['location','date','new_cases_per_million', 
                                                   'new_deaths_per_million', 'population',
                                                   'population_density'],
                                        format_func=str_formatter)
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
            column_choices = list(dataset.columns)
            
        col_date_df, col_group,col_grp_desc = st.beta_columns(3)

        with col_date_df:
            date_range_choices = st.date_input('Change the dates?', value=(dt.datetime(2020,1,1),dt.datetime.now()),key='chg_dts_df')
            show_df = dataset[column_choices]
            show_df = show_df[(show_df['date']>=pd.to_datetime(date_range_choices[0])) & 
                              (show_df['date']<=pd.to_datetime(date_range_choices[1]))]
        with col_group:
            group_choices = st.multiselect('What should we groupby?',
                                           ['Nothing'] + column_choices,
                                           format_func=str_formatter,default=['Nothing'])
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
                st.error(f'ERROR: A grouping statistic must be picked to group by {[str_formatter(x) for x in group_choices]}')
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
            st.success(f'Showing the requested table!')
        else:
            st.success(f'Grouped each of {[str_formatter(x) for x in group_choices]} by {group_desc}!')
        st.table(show_df.head(20))
        
    if "graph" in graph_me.lower():
        y_options = list(show_df.columns)
        show_df = show_df.reset_index()
        x_options = y_options
        hue_options = ['Nothing'] + x_options

        col_gr_chc, col_gr_var, col_gr_txt = st.beta_columns(3)       
        with col_gr_chc:
            graph_type = st.radio('Type of Graph',['Bar graph','Line graph','Scatterplot'])

        with col_gr_var:
            x = st.selectbox('X axis',x_options,format_func=str_formatter)
            y = st.selectbox('Y axis',y_options,format_func=str_formatter)
            
        with col_gr_txt:
            hue = st.selectbox('Color by',hue_options,format_func=str_formatter)
            title = st.text_input('Title')
            
            if hue.lower() == 'nothing':
                hue = None
            if not title:
                st.info('Please enter a title')
                st.stop()
            
        if 'bar ' in graph_type.lower():
            st.plotly_chart(bar_plotter(show_df, x, y, hue, title=title))
        if 'line ' in graph_type.lower():
            st.plotly_chart(line_plotter(show_df, x, y, hue, title=title))
        if 'scatter' in graph_type.lower():
            with col_gr_chc:
                show_ols = st.checkbox('Do regression')
            if show_ols:
                regress = 'ols'
                st.write(regress)
            else:
                regress = None
            st.plotly_chart(scat_plotter(show_df, x, y, hue, title=title, do_ols=regress))
            
    
def app():
    '''Bulk of webgui, calls relevant functions'''
    col_title, col_dataset = st.beta_columns(2)
    with col_title:
        st.title('Covid Dash')
    with col_dataset:
        data_choice = st.radio('Which dataset?',['United States','World'],index=1)
        
    if data_choice.lower() == 'united states':
        st.info('Not implemented (yet)')
        st.stop()
    view_type = st.select_slider("",options=('Premade Plots','Build Your Own!','Dataset'))
    if view_type == "Premade Plots":
        col_sel, col_date = st.beta_columns(2)
        with col_sel:
            options = ['Deaths per mill','Hosp patients per mill','Hospital vs Deaths','Positivity rate']
            plot_selected = st.selectbox('Select a plot',options,index=2)        
        with col_date:
            date_selected = st.date_input('Change the dates?', value=(dt.datetime(2020,7,1),dt.datetime.now()))
        st.info('__Instructions:__ Move mouse into plot to interact. Drag and select to zoom. Double click to reset. Click the camera to save.')
        premade(plot_selected, date_selected)

    if view_type == "Build Your Own!":
        col_plots, col_dates = st.beta_columns(2)
        
        with col_plots:
            plt_type = st.selectbox('Plot Type',['Barplot','Lineplot','Scatterplot'], index=1)
        with col_dates:
            date_selected = st.date_input('Change the dates?', value=(dt.datetime(2020,1,1),dt.datetime.now()))
        x_options = []
        y_options = []
        hue_options = []

        x_options += list(df.select_dtypes(include=[np.datetime64,float,int]).columns)
        y_options += list(df.select_dtypes(include=[float,int]).columns)
        hue_options += list(df.select_dtypes(include=[object, 'category']).columns)

        build_own(x_options,y_options,hue_options,date_selected, plt_type)
        
    if view_type == "Dataset":
        view_dataset(df)

app()