#!/bin/bash
source $HOME/miniconda3/bin/activate

echo "What would you like to do?"
echo "[1] Install covid_dash"
echo "[2] Add to crontab"
echo
read input

function edit_cron(){
    crontab -l > file
    echo "# start after each reboot" >> file
    echo "@reboot      $HOME/projects/covid_dash/start_me.sh > $HOME/projects/covid_dash/start_me.log 2>&1" >> file
    echo "# run five minutes after midnight, every day" >> file
    echo "5 0 * * *      $HOME/projects/covid_dash/update_db.sh > $HOME/projects/covid_dash/update_db.log 2>&1" >> file
    crontab file
    rm file
    echo "covid_dash will start every reboot"
    echo "covid db will be updated once a day"

}

function install_covid()
{
    conda create -y --name "covid_env"
    conda activate covid_env
    conda install -y -c conda-forge python=3.8
    cd $HOME/projects/covid_dash
    pip install --no-input -r requirements.txt
    python update_covid_db.py # initiate database
    nohup streamlit run covid_dash.py --server.port 8504 &
    conda deactivate

    read cron "Append covid_dash to crontab? [y/n] "
    echo


    if [[ $cron == "Y" || $cron == "y" ]]
    then
        edit_cron
    fi

    echo "covid_dash installed on port 8504"

}

if [[ $input == 1 ]]
then
    install_covid
elif [[ $input == 2 ]]
then
    edit_cron
else
    echo "No option selected"
    exit 1
fi
