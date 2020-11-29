# Table of Contents

1. [Description](#description)
2. [Screenshots](#screenshots)
    1. [Premade graphs](#premade-graphs)
    2. [Dynamic dataset](#dynamic-dataset)
3. [Feature list](#feature-list)
    1. [Finished](#finished)
    2. [WIP](#wip)
4. [How tos](#how-tos)
    1. [Run](#run)
    2. [Host](#host)
# Description
Covid dash and analysis using streamlit.

See at: https://covid.peti.work

# Screenshots
## Premade graphs
<img src="https://github.com/pomkos/covid_dash/blob/main/images/premade_demo.png" width="620">

## Dynamic dataset
<img src="https://github.com/pomkos/covid_dash/blob/main/images/dataset_demo.png" width="620">


# Feature list

## Finished
* Premade plots
  * [x] Hospital patients per mill over time
  * [x] Deaths per mill over time
  * [x] Hospital patients per mill vs New cases per mill (with OLS regression)
  * [x] Positivity rate over time
* Usermade plots
  * [x] Group by string variables
  * [x] Date only on x-axis
  * [x] Floats and integers on x-, y-axes but not legend
  * [x] Dynamic plot title
* Premade dataset summary
  * [x] Descriptive statistics
  * [x] Usermade customizable dataset summary
  
## WIP
* Premade plots
  * [ ] Description of each plot
  * [ ] Positivity rate per country
      * [ ] With customizable date
* Usermade plots
  * [ ] Only categorical variables in legend
  * [ ] Ability to choose countries outside plotly
* Premade dataset summary
  * [ ] Comparative statistics
  * [ ] Predictive statistics
  * [ ] Download customized dataset
* [ ] Premade heatmaps
* [ ] Usermade heatmaps

# How tos
## Run

1. Clone the repository:
```
git clone https://github.com/pomkos/covid_dash
cd covid_dash
```

2. Create a conda environment (optional):

```
conda create --name "covid_env"
```

3. Activate environment, install python, install dependencies.

```
conda activate covid_env
conda install python=3.8
pip install -r requirements.txt
```
3. Start the application:
```
streamlit run apps/covid_dash.py
```
5. Access the portfolio at `localhost:8501`

## Host

1. Create a new file outside the `covid_dash` directory:

```
cd
nano covid_dash.sh
```

2. Paste the following in it, then save and exit:

```
#!/bin/bash

source ~/anaconda3/etc/profile.d/conda.sh

cd ~/covid_dash
conda activate covid_env

nohup streamlit run apps/covid_dash.py --server.port 8504 &
```

3. Edit crontab so portfolio is started when server reboots

```
crontab -e
```

4. Add the following to the end, then save and exit

```
@reboot /home/covid_dash.sh
```

5. Access the portfolio at `localhost:8503`
