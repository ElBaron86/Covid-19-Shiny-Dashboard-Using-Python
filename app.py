# Importing modules

# Data manipulation
import pandas as pd

# Data visualization
import matplotlib.pyplot as plt
import seaborn as sns
import mplcyberpunk
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

# My cleaning functions
from scripts.data_cleaning import clean_hosp_data, clean_vaccination_region_data

# TODO: Add a section to the bottom to display my name and the date of the last update of the dashboard

# Loading and configuring data
# hospitalisations data
data_p1 = clean_hosp_data()

# vaccination data
data_p2 = clean_vaccination_region_data()

## Geojson data
regions = json.load(open("data/regions.geojson", "r"))

# Adding page title 
ui.page_opts(
    title="COVID 19 Dashoard - France",
    # Adding a navbar to the page
    page_fn=partial(page_navbar, id="page_vavbar", fillable=True, bg="light"),
)

# ------------------------------------------------- #
######## Hopsital Situation Panel ########
# ------------------------------------------------- #

with ui.nav_panel(title="Hospital Situation", # Title
                    icon=icons("hospital")):
    # Main message
    ui.markdown("Review of data on the situation in hospitals during the COVID-19 pandemic in France. This data comes from the data.gouv.fr website")

    # Sidebar
    ui.input_slider(id="year_slider_p1", label="Year", min=2020, max=2023, value=2021, step=1)

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

# Card containing the information about the hospitalisations graph
    ui.markdown("The following graph shows the evolution of hospital observations during the pandemic. This data has been aggregated by month for the Situations plot and by year for the pie chart. SMSES stands for 'Social or medico-social establishment or service'.")

    # Hospitalisation plot with matplotlib & seaborn tuned with mplcyberpunk
    with ui.layout_columns(fill=False):

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
# TODO: change this plot to a plotly plot that look the same as the actual plot
        @render.plot
        def plot_hospitalisations():

            plt.style.use("seaborn-v0_8")

            # Preparing data
            year = input.year_slider_p1()
            data = data_p1[data_p1['year'] == year]

            colors = ['orange' if 0.7 < to < 0.9 else 'red' if to > 0.9 else 'blue' for to in list(data['TO'])]
            
            # defining the plot
            fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, sharey=False, gridspec_kw={'height_ratios': [0.6, 2]})

            #ax1.set_title(f"Hospital tension on intensive care capacity in {year}")
            ax1.set_ylabel("Tension rate")
            sns.barplot(data=data[data['year']==year], x='month', y='TO', hue='month', palette=colors, legend=False, ax=ax1)


            # Plot the line plot on the second subplot
            #ax2.set_title(f"Situation in hospitals in {year}")
            sns.lineplot(data= data, x='month', y='incid_hosp', label="new hospitalizations", markers=True, marker="p", color="red", ax=ax2)
            sns.lineplot(data = data, x='month', y='incid_rea', label="in reanimations", markers=True, marker="4", color = "orange", ax=ax2)
            sns.lineplot(data = data, x='month', y='incid_rad', label="returned home", markers=True, marker="P", color="green", ax=ax2)
            sns.lineplot(data = data, x='month', y='incid_dchosp', label="died in hospital", markers=True, marker=".", color="dimgray", ax=ax2)
            ax2.set_ylabel("Number of people")
            ax2.set_xticks(range(len(data['month'])))
            ax2.set_xticklabels(data['month'], rotation=45)

            # Adding the cyberpunk style
            mplcyberpunk.add_underglow()
            mplcyberpunk.make_lines_glow(alpha_line=0.4)
            mplcyberpunk.add_gradient_fill(alpha_gradientglow=0.6)

            plt.tight_layout()

            return fig
        


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
        return data_p2[(data_p2['jour'] >= input.date_range_p2()[0]) & (data_p2['jour'] <= input.date_range_p2()[1])].groupby(by=["reg", "jour"]).sum().reset_index()

    # Valueboxes Container
    with ui.layout_columns(fill=False):

# TODO: Analye the data to verify the aggregation results. 

        # Total 1st dose valuebox
        with ui.value_box(showcase=icons("syringe"),
                            theme="bg-gradient-yellow-green"):
            "One dose received"
            @render.express
            def total_dose1():
                int(data_p2_filtered()['n_dose1'].sum())

        # Total 2nd doses valuebox
        with ui.value_box(showcase=icons("syringe"),
                            theme="bg-gradient-green-orange"):
            "Two doses received"
            @render.express
            def total_dose2():
                int(data_p2_filtered()['n_dose2'].sum())

        # Total 3 doses valuebox
        with ui.value_box(showcase=icons("syringe"),
                            theme="bg-gradient-green-purple"):
            "Three doses received"
            @render.express
            def total_dose3():
                int(data_p2_filtered()['n_dose3'].sum())

        # Total 4 doses valuebox
        with ui.value_box(showcase=icons("syringe"),
                            theme="bg-gradient-purple-green"):
            "Four doses received"
            @render.express
            def total_dose4():
                int(data_p2_filtered()['n_dose4'].sum())
    # Message nefore the map
    ui.markdown("The following graph...")

# TODO: Analye the data to verify the aggregation results. Add a barplot with plotly for gender.
# The barplot will be placed between the radio buttons and the map
    with ui.layout_columns(fill=False):

        # Radio buttons for the type of vaccine
        ui.input_radio_buttons(  
            "radio_ndose","Number of doses",  
            {"n_dose1": "1 dose", "n_dose2": "2 doses", "n_dose3": "3 doses", "n_dose4": "4 doses"},  
            )  

        # Regions map of vaccination
        @render_plotly
        def regions_map():
            
            fig = px.choropleth_mapbox(data_p2_filtered(), geojson=regions, locations='reg', featureidkey="properties.code",
                                        color=input.radio_ndose(), color_continuous_scale="Viridis",
                                        range_color=(int(data_p2_filtered()[input.radio_ndose()].min()), int(data_p2_filtered()[input.radio_ndose()].max())),
                                        mapbox_style="carto-positron",
                                        zoom=4, center = {"lat": 46.18680055591775, "lon": 2.547157538666192},
                                        opacity=0.5)

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
