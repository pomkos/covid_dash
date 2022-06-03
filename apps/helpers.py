import streamlit as st
import plotly.express as px
########################
### HELPER FUNCTIONS ###
########################


def source_viewer(url):
    '''
    Adds the source to the sidebar
    '''
    source = f"[Data source]({url})"
    st.sidebar.write(source)

def overview_plotter(yesterday, dataframe, title, y, x, sortby='region',):
    '''
    Show who's winning. Returns a bar graph of selected cat variables.
    '''
    top_df = dataframe[dataframe.date.apply(lambda x: True if x.date() >= yesterday else False)]
    sort = st.checkbox(f"Sort by {sortby}")
    if sort:
        color = sortby
        if (color == 'continent') | (color == 'region'):
            co = list(dataframe[color].unique())
            if None in co:
                co.remove(None)
            top_df = top_df[top_df[color].isin(co)]

    else:
        color = None

    res = top_df.sort_values(y, ascending=False)
    fig = px.bar(
        data_frame = res,
        x=x,
        y=y,
        color=color,
        title=title,
        labels={
            y: ylabel_format(y, ylog=False),
            x: str_formatter(x),
            sortby:sortby
        }
    )

    return fig

def ylabel_format(my_string, ylog):
    if my_string == "rolling_pos_per_tests":
        my_string = "Positivity ratio"
    elif "_per_hundred" in my_string:
        my_string = "Percent (%)"
    else:
        my_string = my_string.replace("smoothed_", "").replace("rolling_", "").replace("_", " ").capitalize()

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
    fig = px.line(
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
    fig.update_layout(hovermode="x")
    return fig


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

def find_xy_annotations(date, location, ylabel, df):
    """
    Finds the x and y values to place annotations in

    input
    ----
    date: str
    location: str
    """
    import pandas as pd
    sig_date = pd.to_datetime(date)
    temp_df = df[(df["location"] == location) & (df["date"] == sig_date)]
    ymax = temp_df[ylabel].max()
    return sig_date, ymax

def get_annotation_data(unique_locations, label, conn):
    '''
    Retrieves news data from db, returns a dictionary of lists. Each list has a dictionary.
    
    input
    -----
    unique_locations: list
        List of countries that annotations are needed for
    label: str
        String of "vax" or "cases", indicating which graph the data is used for
    conn: sqlalchemy conn
        Connection database
    '''
    import pandas as pd
    all_annotations = {}
    dataframe = pd.read_sql('news',conn)
    relevant_df = dataframe[dataframe['label']==label]
    for ctry in unique_locations:
        if ctry in relevant_df['location'].unique():
            data = relevant_df[relevant_df['location'] == ctry]
            sub_dict = {} # initialize sub dict
            for row in data.itertuples(index=False):
                data_dict = dict(row._asdict())
                if ctry in all_annotations.keys():
                    all_annotations[ctry].append(data_dict)
                else:
                    all_annotations[ctry] = [data_dict]
    return all_annotations

def annotation_creator(fig, ylabel, df, annotation_settings):
    """
    Adds annotations to plotly figure based on variable input, finds
    coordinates using find_xy_annotations()

    input
    ----
    fig: px.figure
        Figure created via plotly express
    ylabel: str
        Column to grab yaxis values from
    df: pd.DataFrame
        Dataframe to graph
    annotation_settings: dict
        Dictionary with the following keys and values
            dates: list
                List of strings in form of "December 07, 1998"
            location: str
                Location the annotation is relevant for
            titles: list
                List of strings with text the label should show
            hovertexts: list
                List of strings with text the label should show after hovering mouse over the label itself
            ax: int
                Number of pixels to shift annotation on the x axis
            ay: int
                Number of pixels to shift annotation on the y axis
    """
    
    # get coordinates
    for i in range(len(annotation_settings)):
        ctry_dict = annotation_settings[i]
        sig_date, ymax = find_xy_annotations(
            date=ctry_dict['dates'],
            location=ctry_dict["location"],
            ylabel=ylabel,
            df=df,
        )
        # add annotation to the figure
        fig.add_annotation(
            x=sig_date,
            y=ymax,
            text=ctry_dict["titles"],
            showarrow=True,
            arrowhead=2,
            arrowside="end",
            arrowsize=1,
            standoff=2,
            ax=ctry_dict["ax"],
            ay=ctry_dict["ay"],
            hovertext=ctry_dict["hovertexts"],
            align="left",
        )