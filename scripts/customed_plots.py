"""This script contains some customed plots functions used in the app.

Returns:
----------------
    fig: a matplotlib figure object
"""

# Importing the libraries
from typing import List, Dict
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import plotly.express as px
import pandas as pd


import plotly.graph_objects as go
from plotly.subplots import make_subplots

def generate_subplot_figure(year, data_p1):
    """Generate a subplot figure with a bar plot of the tension rate and a line plot of the hospitalizations.

    Args:
    ----------------
        year : The shiny ui input object with the attribute year_slider_p1
        data_p1 (pd.DataFrame): The filtered data for the first part of the app

    Returns:
    ----------------
        fig: The subplot figure
    """
    plt.style.use("seaborn-v0_8")

    # Preparing data
    data = data_p1[data_p1['year'] == year]

    colors = ['orange' if 0.7 < to < 0.9 else 'red' if to > 0.9 else 'blue' for to in list(data['TO'])]

    # Subplot for tension rate & hospitalizations
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        subplot_titles=(f"Average tension rate per month in {year}", ""),
                        row_heights=[0.2, 0.8], vertical_spacing=0.02)
    # Bar plot for tension rate
    fig.add_trace(go.Bar(
        x=data['month'],
        y=data['TO'],
        marker=dict(color=colors),
        name="Tension Rate"
    ), row=1, col=1)
    # New hospitalizations line plot
    fig.add_trace(go.Scatter(
        x=data['month'],
        y=data['incid_hosp'],
        mode='lines+markers',
        name="New Hospitalizations",
        line=dict(color='red'),
        marker=dict(symbol='circle')
    ), row=2, col=1)
    # Reanimation line plot
    fig.add_trace(go.Scatter(
        x=data['month'],
        y=data['incid_rea'],
        mode='lines+markers',
        name="In Reanimations",
        line=dict(color='orange'),
        marker=dict(symbol='square')
    ), row=2, col=1)
    # Returned home line plot
    fig.add_trace(go.Scatter(
        x=data['month'],
        y=data['incid_rad'],
        mode='lines+markers',
        name="Returned Home",
        line=dict(color='green'),
        marker=dict(symbol='diamond')
    ), row=2, col=1)
    # Death line plot
    fig.add_trace(go.Scatter(
        x=data['month'],
        y=data['incid_dchosp'],
        mode='lines+markers',
        name="Died in Hospital",
        line=dict(color='dimgray'),
        marker=dict(symbol='cross')
    ), row=2, col=1)

    # Show legend on the bottom subplot
    fig.update_traces(showlegend=True, row=2, col=1)
    # Update layout
    fig.update_layout(
        yaxis=dict(title="Tension rate", range=[0, 1.5]),
        yaxis2=dict(title="Number of people", range=[0, 100000]),
        xaxis2=dict(title="Month"),
        height=600,
        showlegend=False
    )

    return fig


def generate_choropleth_map(input, data, departments, regions):
    """Generate a choropleth map of the vaccination by region or department.

    Args:
    ----------------
        input (): shiniy ui input object with attributes loc_type and radio_ndose
        data (pd.DataFrame): The filtered data
        departments (geojson): The geojson file of the departments
        regions (geojson): The geojson file of the regions

    Returns:
        fig: The choropleth map
    """
    data = data.groupby(by=[input.loc_type()]).agg({(input.radio_ndose()+'_'+input.loc_type()) : "max"}).reset_index()
    if input.loc_type() == "dep":
        loc = departments
    else:
        loc = regions

    fig = px.choropleth_mapbox(data, geojson=loc, locations=input.loc_type(), featureidkey="properties.code",
                                color=(input.radio_ndose()+'_'+input.loc_type()), color_continuous_scale="Viridis",
                                range_color=(data[(input.radio_ndose()+'_'+input.loc_type())].min(), int(data[(input.radio_ndose()+'_'+input.loc_type())].max())),
                                mapbox_style="carto-positron",
                                zoom=4, center={"lat": 46.18680055591775, "lon": 2.547157538666192},
                                opacity=0.5)

    fig.update_layout(title=f"Vaccination by Region")
    return fig

def repart(details : Dict, category_dose : List[str] = ["First doses", "Booster doses", "Second booster doses", "Third booster doses"]):
    """Plot a stacked bar chart of the repartition of the doses by category.

    Args:
    ----------------
        details (dict): A dictionary containing the number of doses by age class. The keys are the age classes ('25-29', ...) and the values are
        a list of the number of people who received a specific categories of doses.
        category_dose (list): The list of the categories of doses.

    Returns:
    ----------------
        _type_: _description_
    """
    plt.style.use('seaborn-v0_8')

    labels = list(details.keys())
    values = np.array(list(details.values()))
    values_cum = np.cumsum(values, axis=1)
    category_colors = plt.get_cmap('RdYlGn')(np.linspace(0.15, 0.85, values.shape[1]))
    fig, ax = plt.subplots()
    ax.invert_yaxis()
    ax.xaxis.set_visible(True)
    ax.set_xlim(0, np.sum(values))
    ax.set_xlabel('Number of people')
    ax.set_ylabel('Age class')

    for i, category in enumerate(category_dose):
        ax.barh(labels, values_cum[:, i], left=np.sum(values_cum[:, :i], axis=1), height=0.8, label=category, color=category_colors[i])
    ax.legend(ncol=len(category_dose), bbox_to_anchor=(0, 1), loc='lower left', fontsize='small')
    
    return fig
