# Importing modules

# Data manipulation
import pandas as pd
import numpy as np

# Data visualization
import matplotlib.pyplot as plt
import seaborn as sns
from plotly.subplots import make_subplots
import plotly.tools as tls
import plotly.graph_objects as go
import plotly.express as px
import json

# Dashboard modules
from shiny.express import ui, input
from shinywidgets import render_plotly, render_widget
from shiny import reactive, render, req
from functools import partial
from shiny.ui import page_navbar
from faicons import icon_svg as icons

# Loading prepared data
# Hospitalisations data
data_p1 = pd.read_csv("data/indicateur-suivi.csv")

# Vaccination data
data_p2 = pd.read_csv("data/vaccination.csv", low_memory=False)
data_p2['jour'] = pd.to_datetime(data_p2['jour']).dt.date

# Vaccination detailed data
data_p3 = pd.read_csv("data/vaccination_detailed.csv", low_memory=False)
data_p3['jour'] = pd.to_datetime(data_p3['jour']).dt.date

# Geojson data
regions = json.load(open("data/regions.geojson", "r"))
departments = json.load(open("data/departements.geojson", "r"))

# Adding page title 
ui.page_opts(
    title="COVID 19 Dashoard - France",
    # Adding a navbar to the page
    page_fn=partial(page_navbar, id="page_vavbar", fillable=True, bg="mediumpurple"),
)

# ------------------------------------------------- #
######## Hopsital Situation Panel ########
# ------------------------------------------------- #

with ui.nav_panel(title="Hospital Situation", # Title
                    icon=icons("hospital")):
    # Main message
    ui.markdown("**About :**\n"
                "This dashboard offers an analysis of data on the Covid-19 pandemic in France. This data comes from [data.gouv](https://www.data.gouv.fr/fr/datasets/) and was used for free exploration purposes.")

    # Sidebar
    ui.input_slider(id="year_slider_p1", label="Year", min=2020, max=2023, value=2020, step=1)

    # Reactive data filtering
    @reactive.calc
    def data_p1_filtered():
        year = input.year_slider_p1()
        return data_p1[data_p1['year'] == year]
    
    # Valueboxes Container
    with ui.layout_columns(fill=False):

        # Total positive cases valuebox
        with ui.value_box(showcase=icons("virus-covid"),
                            theme="bg-gradient-yellow-orange",
                            max_height="160px"):
            "Total Positive Cases" # Box title
            @render.express
            def total_pos():
                int(data_p1_filtered()['pos'].sum())

        # Total hospitalisations valuebox
        with ui.value_box(showcase=icons("truck-medical"),
                            theme="bg-gradient-red-purple",
                            max_height="160px"):
            "Total Hospitalizations"
            @render.express
            def total_hosp():
                int(data_p1_filtered()['incid_hosp'].sum())

        # Total reanimations valuebox
        with ui.value_box(showcase=icons("bed-pulse"),
                            theme="bg-gradient-orange-cyan",
                            max_height="160px"):
            "Total In Reanimation"
            @render.express
            def total_rea():
                int(data_p1_filtered()['incid_rea'].sum())

        # Total deaths valuebox
        with ui.value_box(showcase=icons("house-user"),
                            theme="bg-gradient-green-blue",
                            max_height="160px"):
            "Total Returning Home"
            @render.express
            def total_returns():
                int(data_p1_filtered()['incid_rad'].max())

        # Total returns home valuebox
        with ui.value_box(showcase=icons("skull"),
                            theme="bg-gradient-black",
                            max_height="160px"):
            "Total Deaths" 
            @render.express
            def total_deaths():
                int(data_p1_filtered()['dc_tot'].max())

# Displaying a description of graphs
    ui.markdown("**About the graphs :**\n"
                "The following graph shows the evolution of hospital observations during the pandemic. This data has been aggregated by month for the Situations plot and by year for the pie chart. SMSES stands for 'Social or medico-social establishment or service and 'Tension rate' is the COVID-19 intensive care unit bed occupancy rate.")

    # Hospitalisation plot
    with ui.layout_columns(col_widths=[3, 9], fill=False):

        @render_plotly
        def plot_deaths_pie():
            # Preparing data
            year = input.year_slider_p1()
            data = data_p1[data_p1['year'] == year]
            deaths = data.groupby(by=['year']).agg({'dchosp' : 'max',
                                                    'esms_dc' : 'max'}).reset_index()
            
            # Sum just to unify the plot and provide error handling
            deaths = deaths.drop(columns=['year']).sum()
            # Pie chart of deaths
            pie_chart = px.pie(deaths, values=deaths, names=["in hospitals", "in SMSES"],title=f"Deaths in {year}",
                                color=["Prism", "Safe"],
                                color_discrete_map={"Prism": "rgb(102, 102, 102)",
                                                    "Safe": "rgb(179, 179, 179)"})
            
            return pie_chart

        @render_plotly
        def plot_hospitalisations():

            plt.style.use("seaborn-v0_8")

            # Preparing data
            year = input.year_slider_p1()
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
        
    # About Me
    ui.markdown("**About Me :**\n"
                "I made this dashboard to practice my shiny visualization skills and to provide a tool for the public to understand the Covid-19 situation in France. I hope you find it useful. If you have any questions or suggestions, feel free to visit my [github](https://github.com/ElBaron86/Covid-19-Shiny-Dashboard-Using-Python.git).")


# ------------------------------------------------- #
######## Vaccination Situation Panel ########
# ------------------------------------------------- #

with ui.nav_panel(title="Vaccination Situation", # Title
                    icon=icons("syringe"),
                    ):
    # Date range input
    ui.input_date_range("date_range_p2", "Date Range", start="2020-12-27")
    
    # Reactive data filtering
    @reactive.calc
    def data_p2_filtered():
        return data_p2[(data_p2['jour'] >= input.date_range_p2()[0]) & (data_p2['jour'] <= input.date_range_p2()[1])]

    # Valueboxes Container
    with ui.layout_columns(fill=False):

# TODO: Analye the data to verify the aggregation results. 

        # Total 1st dose valuebox
        with ui.value_box(showcase=icons("syringe"),
                            theme="bg-gradient-yellow-green"):
            "One dose received"
            @render.express
            def total_dose1():
                regs = list(data_p2_filtered()['reg'].unique())
                res = [data_p2_filtered()[data_p2_filtered()['reg'] == reg]['n_cum_dose1_reg'].max() for reg in regs]
                int(np.sum(res))

        # Total 2nd doses valuebox
        with ui.value_box(showcase=icons("syringe"),
                            theme="bg-gradient-green-orange"):
            "Two doses received"
            @render.express
            def total_dose2():
                regs = list(data_p2_filtered()['reg'].unique())
                res = [data_p2_filtered()[data_p2_filtered()['reg'] == reg]['n_cum_dose2_reg'].max() for reg in regs]
                int(np.sum(res))

        # Total 3 doses valuebox
        with ui.value_box(showcase=icons("syringe"),
                            theme="bg-gradient-green-purple"):
            "Three doses received"
            @render.express
            def total_dose3():
                regs = list(data_p2_filtered()['reg'].unique())
                res = [data_p2_filtered()[data_p2_filtered()['reg'] == reg]['n_cum_dose3_reg'].max() for reg in regs]
                int(np.sum(res))

        # Total 4 doses valuebox
        with ui.value_box(showcase=icons("syringe"),
                            theme="bg-gradient-purple-green"):
            "Four doses received"
            @render.express
            def total_dose4():
                regs = list(data_p2_filtered()['reg'].unique())
                res = [data_p2_filtered()[data_p2_filtered()['reg'] == reg]['n_cum_dose4_reg'].max() for reg in regs]
                int(np.sum(res))
    # Message nefore the map
    ui.markdown("The following graph...")

# TODO: Analye the data to verify the aggregation results. Add a barplot with plotly for gender.
# The barplot will be placed between the radio buttons and the map
    with ui.layout_columns(col_widths=(2, 2, 8),fill=False):

        # Radio buttons for the type of vaccine
        ui.input_radio_buttons(  
            "radio_ndose","Number of doses",  
            {"n_cum_dose1": "1 dose", "n_cum_dose2": "2 doses", "n_cum_dose3": "3 doses", "n_cum_dose4": "4 doses"},  
            )  
        
        # Selectsize for regions or departments
        ui.input_selectize("loc_type", "Select a option below:", {"reg": "Regions", "dep": "Departments"},)

        # Regions map of vaccination
        @render_plotly
        def regions_map():

            # data preparation
            data = data_p2_filtered()
            data = data.groupby(by=[input.loc_type()]).agg({(input.radio_ndose()+'_'+input.loc_type()) : "max"}).reset_index()
            if input.loc_type() == "dep":
                loc = departments
            else:
                loc = regions
            
            fig = px.choropleth_mapbox(data, geojson = loc, locations = input.loc_type(), featureidkey = "properties.code",
                                        color = (input.radio_ndose()+'_'+input.loc_type()), color_continuous_scale = "Viridis",
                                        range_color = (data[ (input.radio_ndose()+'_'+input.loc_type()) ].min(), int(data[ (input.radio_ndose()+'_'+input.loc_type()) ].max())),
                                        mapbox_style = "carto-positron",
                                        zoom = 4, center = {"lat": 46.18680055591775, "lon": 2.547157538666192},
                                        opacity = 0.5)

            fig.update_layout(title=f"Vaccination by Region")
            return fig

# ------------------------------------------------- #
######## Detailed Vaccination Situation Panel ########
# ------------------------------------------------- #
# TODO: Combine the data, add vaccines names, add a departments map, radio buttons for the type of vaccine, barplot for ages
with ui.nav_panel(title="Detailed Vaccination", # Title
                    icon=icons("restroom"),
                    ):
    # Main message
    f"Review of data on the specific vaccination situation" 

    # Date range input
    ui.input_date_range("date_range_p3", "Date Range", start="2020-12-27")

    # Reactive data filtering
    @reactive.calc
    def data_p3_filtered():
        return data_p3[(data_p3['jour'] >= input.date_range_p3()[0]) & (data_p3['jour'] <= input.date_range_p3()[1])]
    

