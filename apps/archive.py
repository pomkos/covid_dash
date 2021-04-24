'''
Deprecated functions, in case I wanted to implement them later
'''
def byo_app():
    if view_type == "Build Your Own!":
        col_plots, col_dates = st.beta_columns(2)

        with col_plots:
            plt_type = st.selectbox(
                "Plot Type", ["Barplot", "Lineplot", "Scatterplot"], index=1
            )
        with col_dates:
            date_selected = st.date_input(
                "Change the dates?", value=(dt.datetime(2020, 3, 1), dt.datetime.now())
            )
        x_options = []
        y_options = []
        hue_options = []

        x_options += all_columns
        y_options += all_columns
        hue_options += all_columns

        build_own(x_options, y_options, hue_options, date_selected, plt_type)

    if view_type == "Dataset":
        from apps import dataset_viewer as dv

        dv.app(all_columns, table, session)

def build_own(x_options, y_options, hue_options, date_selected, plt_type="lineplot"):
    """Presents options for user to make own graph, then calls the appropriate plotter()"""
    # webgui

    my_cols = []
    col_x, col_y, col_hue = st.beta_columns(3)
    with col_x:
        x_default = h.find_default(x_options, "date")
        x = st.selectbox(
            "X axis", x_options, format_func=h.str_formatter, index=x_default
        )
        xlog = st.checkbox("log(x axis)")
    with col_y:
        y_default = h.find_default(y_options, "new_cases_smoothed_per_million")
        y = st.selectbox(
            "Y axis", y_options, format_func=h.str_formatter, index=y_default
        )
        ylog = st.checkbox("log(y axis)")
    with col_hue:
        hue_default = h.find_default(hue_options, "location")
        hue = st.selectbox(
            "Group by", hue_options, format_func=h.str_formatter, index=hue_default
        )

    if hue.lower() == "location":
        default_selected = ["Canada", "Hungary", "United States"]

    elif hue.lower() == "continent":
        default_selected = [
            "Africa" "Asia",
            "Europe",
            "North America",
            "Oceania",
            "South America",
        ]
    else:
        default_selected = None

    my_cols.append(x)
    my_cols.append(y)
    my_cols.append(hue)

    df = pd.DataFrame(h.sql_orm_requester(my_cols, table, session))
    byo_df = h.dataset_filterer(df, hue, default_selected=default_selected)

    if plt_type.lower() == "lineplot":
        st.plotly_chart(
            h.line_plotter(
                x, y, date_selected, dataset=byo_df, hue=hue, xlog=xlog, ylog=ylog
            )
        )
    elif plt_type.lower() == "scatterplot":
        st.plotly_chart(
            h.scat_plotter(x, y, dataset=byo_df, hue=hue, xlog=xlog, ylog=ylog)
        )
    else:
        st.plotly_chart(
            h.bar_plotter(x, y, dataset=byo_df, hue=hue, xlog=xlog, ylog=ylog)
        )