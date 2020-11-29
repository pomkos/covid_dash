# Description
Covid dash and analysis using streamlit.

See at: https://covid.peti.work

# Screenshot
<img src="https://github.com/pomkos/portfolio/blob/main/sample.png" width="620">

# How to Run

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
streamlit run covid_dash.py
```
5. Access the portfolio at `localhost:8501`
# How to Host Headless

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

nohup streamlit run covid_dash.py --server.port 8503 &
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

# Feature list

* [x] Premade plots
* [x] Usermade plots
  * [x] Group by string variables
  * [x] Date only on x-axis
  * [x] Floats and integers on x-, y-axes but not legend
  * [ ] Only categorical variables in legend
  * [ ] Ability to choose countries outside plotly
  * [x] Dynamic plot title
* [ ] Premade dataset summary
  * [x] Descriptive statistics
  * [ ] Comparative statistics
  * [ ] Predictive statistics
  * [x] Usermade customizable dataset summary
  * [ ] Download customized dataset
* [ ] Premade heatmaps
* [ ] Usermade heatmaps
