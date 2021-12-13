#!/bin/bash
# For use with crontab
source ~/miniconda3/bin/activate

cd $HOME/projects/covid_dash
conda activate covid_env # activate the new conda env
python update_covid_db.py
