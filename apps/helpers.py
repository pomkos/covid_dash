import streamlit as st
import plotly.express as px

########################
### HELPER FUNCTIONS ###
########################


def ylabel_format(my_string, ylog):
    if my_string == "rolling_pos_per_tests":
        my_string = "Positivity ratio"
    elif "_per_hundred" in my_string:
        my_string = "Percent (%)"
    else:
        my_string = my_string.replace("smoothed_", "").replace("_", " ").capitalize()

    if ylog:
        my_string += " (log)"
    return my_string

def str_formatter(my_str):
    """
    To make choices and axes pretty
    """
    return my_str.replace("_", " ").capitalize()


def find_default(my_list, my_string):
    """Finds the index of some column in a list"""
    for i, obj in enumerate(my_list):
        if obj.lower() == my_string:
            my_index = i
    return my_index


def hue_formatter(x, y, hue):
    if hue == None:
        labels = {
            x: str_formatter(x),
            y: str_formatter(y),
            # hue:str_formatter(hue)
        }
    else:
        labels = {x: str_formatter(x), y: str_formatter(y), hue: str_formatter(hue)}
    return labels


def dataset_filterer(dataset, col, default_selected=None):
    """
    Returns the dataset filtered by user's choice of unique values from given column
    """
    options = list(dataset[col].unique())
    if col == "continent":
        options.remove(None)
    options.sort()
    chosen = st.sidebar.multiselect(f"Select {col}s", options, default=default_selected)
    new_df = dataset[dataset[col].isin(chosen)]
    return new_df


def file_downloader_html(bin_file, file_label="File"):
    with open(bin_file, "rb") as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download</a>'
    return href


def sql_orm_requester(columns, table, session):
    """
    Created to standardize grabbing columns of interest from sql table.
    Returns sqlorm query results
    """
    colspec = [getattr(table.c, col) for col in columns]
    ResultSet = session.query(*colspec)
    return ResultSet


######################
### PLOT FUNCTIONS ###
######################
def scat_plotter(
    x, y, dataset, hue=None, xlog=False, ylog=False, title=None, do_ols=None, **kwargs
):
    """Plotly plots a scatterplot"""
    if title == None:
        title = f"{str_formatter(y)} vs {str_formatter(x)}"
    labels = hue_formatter(x, y, hue)
    my_plot = px.scatter(
        dataset,
        x=x,
        log_x=xlog,
        log_y=ylog,
        title=title,
        # range_x =,
        y=y,
        color=hue,
        trendline=do_ols,
        **kwargs,
    )
    return my_plot


def line_plotter(
    x, y, date_selected, dataset, hue=None, xlog=False, ylog=False, title=None, **kwargs
):
    """Plotly plots a lineplot"""
    if title == None:
        title = f"{str_formatter(y)} vs {str_formatter(x)}"
    labels = hue_formatter(x, y, hue)
    my_plot = px.line(
        data_frame=dataset,
        x=x,
        log_x=xlog,
        log_y=ylog,
        y=y,
        title=title,
        range_x=date_selected,
        color=hue,
        **kwargs,
    )
    my_plot.update_layout(hovermode="x")
    return my_plot


def bar_plotter(x, y, dataset, hue=None, xlog=False, ylog=False, title=None, **kwargs):
    """Plotly plots a barplot"""
    labels = hue_formatter(x, y, hue)
    my_plot = px.bar(
        data_frame=dataset,
        x=x,
        log_x=xlog,
        y=y,
        color=hue,
        log_y=ylog,
        title=title,
        barmode="group",  # group, overlay, relative
        **kwargs,
    )
    return my_plot
