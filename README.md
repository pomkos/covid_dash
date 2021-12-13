[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://covid.peti.work)

The only purpose of this branch is to allow streamlit.io to clone the project with an included sqlite dataset. 
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
* Dataset summary
  * [x] Descriptive statistics
  * [x] Usermade customizable dataset summary
* Get the data
  * [x] Download plot (via plotly)
  
## WIP
* Premade plots
  * [ ] Description of each plot
  * [x] Positivity rate per country
      * [ ] With customizable date
* Usermade plots
  * [ ] Only categorical variables in legend
    * [ ] Depending on plot type (bar, line, scatter)
  * [x] Ability to choose countries outside plotly
* Dataset summary
  * [ ] Comparative statistics (traditional stats)
  * [ ] Predictive statistics (machine learning)
  * [ ] Download customized dataset
* [ ] Premade heatmaps
* [ ] Usermade heatmaps

# Host

```bash
sudo chmod +x install.sh
sudo chmod +x start_me.sh
sudo chmod +x update_db.sh

./install.sh
```

Installer script will:

1. Create new environment
2. Install all required python libraries
3. Add a cronjob to cron (if user desires, can be done post installation as well)
4. Start the covid_dash script on `port 8504`
