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

# us_pw = sys.argv[1]  # user input: "my_user:password"
# db_ip = sys.argv[2]  # user input: 192.168.1.11
# port = sys.argv[3]   # user input: 5432

################
### MAIN APP ###
################

def app():
    '''Bulk of webgui, calls relevant functions'''
    st.title('Covid Dash')
    with st.beta_expander('Which dataset?'):
        data_choice = st.radio('',['United States','World'],index=1)
        
    if data_choice.lower() == 'united states':
        st.info('Not implemented (yet)')
        st.stop()
    else:
        from apps import covid_world
        covid_world.app()


app()
