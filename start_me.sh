#!/bin/bash
# For use with crontab
source ~/miniconda3/bin/activate

cd $HOME/projects/covid_dash
conda activate covid_env # activate the new conda env
nohup streamlit run covid_dash.py --server.port 8504 & # run in background

echo "Running covid_dash.py on port 8504!"
