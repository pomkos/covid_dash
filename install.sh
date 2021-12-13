#!/bin/bash
source $HOME/miniconda3/bin/activate

conda create -y --name "covid_env"
conda activate covid_env
conda install -y -c conda-forge python=3.8
cd $HOME/projects/covid_dash
pip install --no-input -r requirements.txt
python update_covid_db.py # initiate database
nohup streamlit run covid_dash.py --server.port 8504 &
conda deactivate

echo "covid_dash installed on 8504"
