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
        "", ["USA Cases", "World Cases", "World Vaccination" , "Animations"], index=0
    )
    st.sidebar.write("--------")

    if "usa cases" in data_choice.lower():
        st.title("Covid Dash")
        from apps import covid_usa

        covid_usa.app()

    elif "animations" in data_choice.lower():
        ############### TESTING AREA ###############
        from apps import map_maker

        map_maker.app()
        ###########################################
    elif "world cases" in data_choice.lower():
        st.title("Covid Dash")
        from apps import covid_world

        covid_world.app()
        
    elif "world vacc" in data_choice.lower():
        st.title("Vaccine Dash")
        from apps import vax_world
        vax_world.app()

app()
