# Importing modules
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import mplcyberpunk
import plotly.graph_objects as go
import plotly.express as px
from functools import partial
from shiny.express import ui, input
from shinywidgets import render_plotly, render_widget
from shiny import reactive, render, req
from shiny.ui import page_navbar
from faicons import icon_svg as icons
import json

# TODO: Add a section to the bottom to display my name and the date of the last update of the dashboard

# Loading and configuring data
# hospitalisations data
data_p1 = pd.read_csv("data/indicateur-suivi.csv")
data_p1["date"] = pd.to_datetime(data_p1["date"])
data_p1["year"] = data_p1["date"].dt.year
data_p1["month"] = data_p1["date"].dt.month_name()

# vaccination data
data_p2 = pd.read_csv("data/vacsi-v-reg-2023-07-13-15h51.csv", sep=";")
data_p2["jour"] = pd.to_datetime(data_p2["jour"])
data_p2['jour'] = data_p2['jour'].dt.date

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
                int(data_p1_filtered()['hosp'].sum())

        # Total reanimations valuebox
        with ui.value_box(showcase=icons("bed-pulse"),
                            theme="bg-gradient-orange-cyan",
                            max_height="160px"):
            "Total In Reanimation"
            @render.express
            def total_rea():
                int(data_p1_filtered()['rea'].sum())

        # Total deaths valuebox
        with ui.value_box(showcase=icons("house-user"),
                            theme="bg-gradient-green-blue",
                            max_height="160px"):
            "Total Returning Home"
            @render.express
            def total_returns():
                int(data_p1_filtered()['rad'].max())

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

# TODO: Analyse the data or review the aggregation results
        # Pie chart od deaths
        @render_plotly
        def plot_deaths_pie():
            # Preparing data
            year = input.year_slider_p1()
            data = data_p1.groupby(['year']).agg({'dchosp': 'sum',
                                                    'esms_dc' : 'sum'}).reset_index()
            data = data_p1[data_p1['year'] == year]
            deaths = data[['dchosp', 'esms_dc']].sum()

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

            # Gouping data to unify the plot
            year = input.year_slider_p1()
            data = data_p1.groupby(['year', 'month']).agg({'hosp': 'sum',
                                                            'rea': 'sum',
                                                            'rad' : 'sum',
                                                            'dchosp' : 'sum'}).reset_index()
            data = data_p1[data_p1['year'] == year]
            
            # defining the plot
            fig = plt.figure(dpi=100)
            sns.lineplot(x=data['month'], y=data['hosp'], label="new hospitalizations", markers=True, marker="p", color="red")
            sns.lineplot(x=data['month'], y=data['rea'], label="in reanimations", markers=True, marker="4", color = "orange")
            sns.lineplot(x=data['month'], y=data['rad'], label="returned home", markers=True, marker="P", color="green")
            sns.lineplot(x=data['month'], y=data['dchosp'], label="died in hospital", markers=True, marker=".", color="dimgray")
            plt.title(f"Situation in hospitals in {year}", fontsize=13, fontweight="semibold")
            # Adding the cyberpunk style
            mplcyberpunk.add_underglow()
            mplcyberpunk.make_lines_glow(alpha_line=0.4)
            mplcyberpunk.add_gradient_fill(alpha_gradientglow=0.6)
            # Axis properties
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
