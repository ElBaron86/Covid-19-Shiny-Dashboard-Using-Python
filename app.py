# Importing modules
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from functools import partial
from shiny.express import ui, input
from shinywidgets import render_plotly
from shiny import reactive, render, req
from shiny.ui import page_navbar
from faicons import icon_svg as icons

# Loading data
data_p1 = pd.read_csv("data\indicateur-suivi.csv")
data_p1["date"] = pd.to_datetime(data_p1["date"])
data_p1["year"] = data_p1["date"].dt.year

# Adding page title and sidebar
ui.page_opts(
    title="COVID 19 Exploration",
    page_fn=partial(page_navbar, id="page_vavbar", fillable=True, bg="light"),
)

# TODO: Add a reactive sidebar to select the year
# Commenting out the code block
# with ui.sidebar(open="desktop"):
#     ui.input_slider(id="year_selector", label="Year",
#                     min=data_p1["year"].min(), max=data_p1["year"].max(), value=data_p1["year"].min())

# ------------------------------------------------- #
# Hopsital Situation Panel
# ------------------------------------------------- #

with ui.nav_panel(title="Hospital Situation", # Title
                    icon=icons("hospital"), # Icon
                    ):
    # Main message
    f"Revue des donnes sur la situation dans les hopitaux durant la pandemie de COVID-19 en France." 


#    with ui.sidebar(open="desktop"):
#            ui.input_slider(id="year_selector", label="Year",
#                            min=data_p1["year"].min(), max=data_p1["year"].max(), value=data_p1["year"].min())


    # Valueboxes Container
    with ui.layout_columns(fill=False):

        # Total positive cases valuebox
        with ui.value_box(showcase=icons("virus-covid"),
                            theme="bg-gradient-yellow-orange"):
            "Total Positive Cases"
            @render.express
            def total_pos():
                data_p1[data_p1['year'] == 2020]['pos'].sum()

        # Total hospitalisations valuebox
        with ui.value_box(showcase=icons("truck-medical"),
                            theme="bg-gradient-red-purple"):
            "Total Hospitalisations"
            @render.express
            def total_hosp():
                data_p1[data_p1['year'] == 2020]['pos'].sum() ######

        # Total reanimations valuebox
        with ui.value_box(showcase=icons("bed"),
                            theme="bg-gradient-orange-cyan"):
            "Total In Reanimation"
            @render.express
            def total_rea():
                data_p1[data_p1['year'] == 2020]['rea'].sum() ######

        # Total deaths valuebox
        # TODO: Set background color to gray and text color to white
        with ui.value_box(showcase=icons("skull"),
                            theme="bg-gradient-black"):
            "Total Deaths"
            @render.express
            def total_deaths():
                data_p1[data_p1['year'] == 2021]['dc_tot'].max()

    # Plots Container
# #
#    with ui.layout_columns(fill=False):
    #Hospialisations & reanimations & Home returns & Deaths
        
#        @render_plotly
#        def plot_hosp():
#            data = data_p1[data_p1['year'] == 2020]
#            fig_hosp = data.plot(x='date', y=['incid_hosp'], kind='line')
            
            # Converting the Axes object to a Plotly object
#            fig_hosp = go.Figure(fig_hosp)

#            return fig_hosp
        

# ------------------------------------------------- #
# Reactivity
# ------------------------------------------------- #
        
#@reactive.calc
#def total_pos():
#    data_p1[data_p1['year'] == 2020]['pos'].sum()
                






## Vaccination Situation Panel ##
#with ui.nav_panel(title="Vaccination Situation",
#                    icon=icons("syringe"),
#                    ):
#    "Revue des donnees sur la vaccination contre le COVID-19 en France."
        

        def plot_hosp():
            data = data_p1[data_p1['year'] == 2020]
            fig_hosp = data.plot(x='date', y=['incid_hosp', 'incid_rea', 'incid_rad', 'dchosp'], kind='line')
            
            # Convertir l'objet Axes en un objet Plotly
            fig_hosp = go.Figure(fig_hosp)
            
            return fig_hosp