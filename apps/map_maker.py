import pycountry
import streamlit as st
import pandas as pd

st.title('Confirmed Covid Cases in 2020')

def get_country_code(name):
    'Get the three-letter country codes for each country'
    try:
        return pycountry.countries.lookup(name).alpha_3
    except:
        return None

class covidMapper():
    def __init__(self,start=False):
        '''
        Maps covid data using plotly chloropleth (mom wrote it!)
        '''
        if start == True:
            df_confirm = pd.read_csv('data/time_series_covid19_confirmed_global.csv')        
            df_confirm = df_confirm.drop(columns=['Province/State','Lat', 'Long'])
            df_confirm = df_confirm.groupby('Country/Region').agg('sum')
            date_list = list(df_confirm.columns)

            df_confirm['country'] = df_confirm.index
            df_confirm['iso_alpha_3'] = df_confirm['country'].apply(get_country_code)

            # Transform the dataset to a long format
            df_long = pd.melt(df_confirm, id_vars=['country','iso_alpha_3'], value_vars=date_list)
            df_long.columns = ['Country','ISO','Date','Confirmed Cases']
            self.dataframe = df_long
        
    def map_creator(self):
        '''
        Creates the map
        '''
        import plotly.express as px
        my_map = px.choropleth(self.dataframe,                            # Input Dataframe
                     locations="ISO",           # identify country code column
                     color="Confirmed Cases",                     # identify representing column
                     hover_name="Country",              # identify hover name
                     animation_frame="Date",        # identify date column
                     projection="equirectangular",        # select projection
                     color_continuous_scale = 'Peach',  # select prefer color scale
                     range_color=[0,50000]              # select range of dataset
                     )        
        return my_map
    
    
def app():
    data_map = covidMapper(start=True)
    my_map = data_map.map_creator()
    st.plotly_chart(my_map)
    
    
    
    