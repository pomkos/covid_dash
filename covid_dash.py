######################
## Import Libraries ##
######################
import streamlit as st  # webgui

# us_pw = sys.argv[1]  # user input: "my_user:password"
# db_ip = sys.argv[2]  # user input: 192.168.1.11
# port = sys.argv[3]   # user input: 5432

################
### MAIN APP ###
################
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
<script src="https://cdn.jsdelivr.net/npm/darkmode-js@1.5.7/lib/darkmode-js.min.js"></script>
<script>
  function addDarkmodeWidget() {
    new Darkmode().showWidget();
  }
  window.addEventListener('load', addDarkmodeWidget);
</script>

"""
st.set_page_config(page_title="Covid Dash")

st.markdown(hide_streamlit_style, unsafe_allow_html=True)  # hides the hamburger menu


def app():
    """Bulk of webgui, calls relevant functions"""
    data_choice = st.sidebar.radio(
        "", ["USA Vaccinations", "World Vaccinations", "USA Cases", "World Cases", "Animations"], index=0
    )
    st.sidebar.write("--------")

    if "usa cases" in data_choice.lower():
        st.title("Covid Dash")
        from apps import covid_usa
        url = "https://github.com/nytimes/covid-19-data"
        covid_usa.app()

    elif "animations" in data_choice.lower():
        ############### TESTING AREA ###############
        from apps import map_maker
        map_maker.app()
        url = "https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series"
        ###########################################
    elif "world cases" in data_choice.lower():
        st.title("Covid Dash")
        url = "https://github.com/owid/covid-19-data/tree/master/public/data"
        from apps import covid_world

        covid_world.app()

    elif "world vacc" in data_choice.lower():
        st.title("Vaccine Dash")
        url = "https://github.com/owid/covid-19-data/tree/master/public/data"
        from apps import vax_world
        vax_world.app()
    elif "usa vacc" in data_choice.lower():
        st.title("Vaccine Dash")
        url = "https://github.com/owid/covid-19-data/tree/master/public/data/vaccinations"
        from apps import vax_usa
        vax_usa.app()
    source = f"[Data source]({url})"
    st.sidebar.write(source)
app()
