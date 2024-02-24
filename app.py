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

# Loading and configuring data
# hospitalisations data
data_p1 = pd.read_csv("data/indicateur-suivi.csv")
data_p1["date"] = pd.to_datetime(data_p1["date"])
data_p1["year"] = data_p1["date"].dt.year
data_p1["month"] = data_p1["date"].dt.month_name()

# vaccination data
data_p2 = pd.read_csv("data/vacsi-v-fra.csv", sep=";")
data_p2["jour"] = pd.to_datetime(data_p2["jour"])
data_p2["year"] = data_p2["jour"].dt.year

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
                    icon=icons("hospital"), # Icon
                    ):
    # Main message
    f"Review of data on the situation in hospitals during the COVID-19 pandemic in France." 

    # Sidebar
    ui.input_slider(id="year_slider_p1", label="Year", min=2020, max=2023, value=2020, step=1)

    @reactive.calc
    def data_p1_filtered():
        year = input.year_slider_p1()
        return data_p1[data_p1['year'] == year]
    


    # Valueboxes Container
    with ui.layout_columns(fill=False):

        # Total positive cases valuebox
        with ui.value_box(showcase=icons("virus-covid"),
                            theme="bg-gradient-yellow-orange"):
            "Total Positive Cases"
            @render.express
            def total_pos():
                int(data_p1_filtered()['pos'].sum())

        # Total hospitalisations valuebox
        with ui.value_box(showcase=icons("truck-medical"),
                            theme="bg-gradient-red-purple"):
            "Total Hospitalizations"
            @render.express
            def total_hosp():
                int(data_p1_filtered()['hosp'].sum())

        # Total reanimations valuebox
        with ui.value_box(showcase=icons("bed-pulse"),
                            theme="bg-gradient-orange-cyan"):
            "Total In Reanimation"
            @render.express
            def total_rea():
                int(data_p1_filtered()['rea'].sum())

        # Total deaths valuebox
        with ui.value_box(showcase=icons("house-user"),
                            theme="bg-gradient-green-blue"):
            "Total Home Returns"
            @render.express
            def total_returns():
                int(data_p1_filtered()['rad'].max())

        # Total returns home valuebox
        with ui.value_box(showcase=icons("skull"),
                            theme="bg-gradient-black"):
            "Total Deaths"
            @render.express
            def total_deaths():
                int(data_p1_filtered()['dc_tot'].max())

    # Hospitalisation lineplot with plotly
    with ui.layout_columns(fill=False):

        @render.plot
        def plot_hospitalisations():
            import matplotlib.pyplot as plt
            import seaborn as sns
            import mplcyberpunk
            plt.style.use("seaborn-v0_8")

            year = input.year_slider_p1()
            data = data_p1.groupby(['year', 'month']).agg({'hosp': 'sum',
                                                            'rea': 'sum',
                                                            'rad' : 'sum',
                                                            'dchosp' : 'sum'}).reset_index()
            data = data_p1[data_p1['year'] == year]
            
            fig = plt.figure(dpi=100)
            sns.lineplot(x=data['month'], y=data['hosp'], label="new hospitalizations", markers=True, marker="p", color="red")
            sns.lineplot(x=data['month'], y=data['rea'], label="in reanimations", markers=True, marker="4", color = "orange")
            sns.lineplot(x=data['month'], y=data['rad'], label="returning home", markers=True, marker="P", color="green")
            sns.lineplot(x=data['month'], y=data['dchosp'], label="died in hospital", markers=True, marker=".", color="black")
            plt.title(f"Situation in hospitals in {year}", fontsize=20, color="white")
            mplcyberpunk.add_underglow()
            mplcyberpunk.make_lines_glow(alpha_line=0.4)
            mplcyberpunk.add_gradient_fill(alpha_gradientglow=0.6)
            plt.ylabel("Number of people")
            plt.xticks(rotation=45)
            plt.tight_layout()

            return fig




# ------------------------------------------------- #
######## Vaccination Situation Panel ########
# ------------------------------------------------- #

with ui.nav_panel(title="Vaccination Situation", # Title
                    icon=icons("syringe"),
                    ):
    # Main message
    f"Review of data on the overall vaccination situation" 

# TODO: Add a reactive sidebar. Maybe il will change the data
    # to take "data/vacsi-v-fra.csv" as input and plot a ipyleaflet Map

    # Sidebar
    ui.input_slider(id="year_slider_p2", label="Year", min=2020, max=2023, value=2020, step=1)

    @reactive.calc
    def data_p2_filtered():
        year = input.year_slider_p2()
        return data_p2[data_p2['year'] == year]

    # Valueboxes Container
    with ui.layout_columns(fill=False):

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


        # Plot
        


                
# ------------------------------------------------- #
######## Detailed Vaccination Situation Panel ########
# ------------------------------------------------- #

with ui.nav_panel(title="Detailed Vaccination", # Title
                    icon=icons("restroom"),
                    ):
    # Main message
    f"Review of data on the specific vaccination situation" 

# TODO: Add a reactive sidebar, a sex checkbox and a age range slider. May be the most reactive part of the app