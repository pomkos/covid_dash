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

### HELPER FUNCTIONS ###
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

def col_types(dataset,dtypes):
    '''
    Selects columns by dtype and stores in a dictionary
    '''
    col_dict = {}
    for t in dtypes:
        col_dict[f'cols_{t}'] = list(df.select_dtypes(t).columns)
    return col_dict


### PLOT FUNCTIONS ###
def scat_plotter(x,y,dataset=df,hue=None,xlog=False,ylog=False,title=None, do_ols=None):
    '''Plotly plots a scatterplot'''
    if title == None:
        title= f'{str_formatter(y)} vs {str_formatter(x)}'
    my_plot = px.scatter(dataset,
                         x= x,
                         log_x=xlog,
                         log_y=ylog,
                         title=title,
                         y= y,
                         color=hue,
                         trendline=do_ols,
                         labels={
                             x: str_formatter(x),
                             y: str_formatter(y),
                             hue:hue
                           })
    return my_plot

def line_plotter(x,y,date_selected, dataset=df,hue=None,xlog=False,ylog=False,title=None):
    '''Plotly plots a lineplot'''
#     if title == None:
#         title= f'{str_formatter(y)} vs {str_formatter(x)}'
    st.table(dataset)
    my_plot = px.line(data_frame=dataset,
                      x= x,
                      log_x = xlog,
                      log_y = ylog,
                      y= y,
                      title = title,
                      range_x = date_selected,
                      color=hue,
#                       labels={
#                           x: str_formatter(x),
# #                           y: y,
# #                           color:hue
#                       }
                     )
    return my_plot

def bar_plotter(x, y,dataset=df, hue=None,xlog=False,ylog=False,title=None):
    my_plot = px.bar(
        data_frame = dataset,
        x = x,
        log_x = xlog,
        y = y,
        color = hue,
        log_y = ylog,
        title = title,
        barmode = 'group', # group, overlay, relative
        labels = {
            x: str_formatter(x),
            y: str_formatter(y)
        })
    return my_plot

### VIEWS GUI ###
def premade(plot_selected, date_selected):
    '''Presents a couple premade, sanitized graphs'''
    if 'Deaths per mill' in plot_selected:
        st.plotly_chart(line_plotter('date',
                                     'new_deaths_smoothed_per_million',
                                     date_selected,
                                     title='Deaths per million by country'),
                        use_container_width = False)
    if 'Hosp patients per mill' in plot_selected:
        st.plotly_chart(line_plotter('date',
                                     'hosp_patients_per_million',
                                     date_selected,
                                     title='Hospital patients per million by country'),
                        use_container_width = False)
    if 'Positivity rate' in plot_selected:
        st.plotly_chart(line_plotter('date',
                                     'positive_rate',
                                     date_selected,
                                     title='Positivity rate by country'),
                        use_container_width = False)
    if 'Hospital vs Deaths' in plot_selected:
        st.plotly_chart(scat_plotter('new_cases_per_million',
                                     'hosp_patients_per_million',
                                     title='Hospital patients related to new cases'), 
                        use_container_width = False)
        
    update = st.button('Update Database')
    if update == True:
        import update_covid_db as ucd
        result = ucd.app()
        st.success(result)

def build_own(x_options,y_options,hue_options,date_selected):
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
  
    st.plotly_chart(line_plotter(x,y,date_selected,hue=hue,xlog=xlog,ylog=ylog))

def view_dataset(dataset, columns=None):
    '''View the dataset, certain or all columns'''
    if columns == None:
        columns = ['All'] + list(dataset.columns)
    columns.sort()
    with st.beta_expander('Settings',expanded=False):
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
            st.warning(f"WARNING: Current settings will load all rows of the dataset")
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
        st.table(show_df.head())
        
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
    st.title('Covid Dash')
    view_type = st.select_slider("",options=('Premade Plots','Build Your Own!','Dataset'))
    if view_type == "Premade Plots":
        col_sel, col_date = st.beta_columns(2)
        with col_sel:
            options = ['Deaths per mill','Hosp patients per mill','Hospital vs Deaths','Positivity rate']
            plot_selected = st.selectbox('Select a plot',options,index=2)        
        with col_date:
            date_selected = st.date_input('Change the dates?', value=(dt.datetime(2020,7,1),dt.datetime.now()))
        st.write('__Instructions:__ Move mouse into plot to interact. Drag and select to zoom. Double click to reset.')
        premade(plot_selected, date_selected)

    if view_type == "Build Your Own!":
        date_selected = st.date_input('Change the dates?', value=(dt.datetime(2020,1,1),dt.datetime.now()))
        x_options = []
        y_options = []
        hue_options = []

        x_options += list(df.select_dtypes(include=[np.datetime64,float,int]).columns)
        y_options += list(df.select_dtypes(include=[float,int]).columns)
        hue_options += list(df.select_dtypes(include=[object, 'category']).columns)

        build_own(x_options,y_options,hue_options,date_selected)
        
    if view_type == "Dataset":
        view_dataset(df)
################################# FOR TESTING #################################
app()
###############################################################################

