# COVID-19 Dashboard for France

This project is a web application that displays various indicators and visualizations related to the COVID-19 pandemic in France. It uses data from the official sources of the Ministry of Solidarity and Health and Public Health France, as well as other open data platforms.

The dashboard allows users to explore the following aspects of the pandemic:

- Key numbers: total cases, deaths, hospitalizations, intensive care, vaccinations, etc.

- Hospital: number and rate of hospital admissions, discharges, and deaths for COVID-19 patients, etc.
- Vaccination: number and rate of doses administered, coverage by age group, etc.

- Regional-level data: comparison and evolution of the indicators by region, department, or city, etc.

The dashboard is interactive and allows users to filter, zoom, and customize the visualizations according to their preferences. It also provides links to the original data sources and additional information on the methodology and definitions used.

## Implementation

This project is implemented using [**Shiny**](https://shiny.posit.co/py/), a recent Python package that is designed to make it easy to build interactive web applications with the power of Python’s data and scientific stack. Shiny integrates with popular visualization packages like Matplotlib, Seaborn, and Plotly.

This project is an opportunity for me to explore this new library of Python and to showcase my skills in data analysis and visualization. I have learned a lot from the [documentation](https://shiny.posit.co/py/docs/overview.html) and [examples](https://shiny.posit.co/py/gallery/) provided by Shiny, as well as from other online resources and tutorials.

## How to run

To run this project, you need to have Python 3.8 or higher installed on your machine, as well as the packages in [requirements.txt](requirements.txt).

It is recommended to create a virtual environment for your project, in order to isolate dependencies and avoid conflicts with other projects or libraries. You can use Python's venv module to create and activate a virtual environment, for example:

```bash
python -m venv env
source env/bin/activate
```

You can install them using pip or conda, for example:

```bash
pip install -r requirements.txt
```

Then, you can clone this repository or download the zip file and extract it. In the project folder, you can run the following command to launch the app:

```bash
shiny run app.py --reload --launch-browser
```

This will open a browser window with the dashboard. You can also access it from another device on the same network by using the URL displayed in the terminal.

## Screenshots

Here are some screenshots of the dashboard:

![Hospitalisations](https://github.com/ElBaron86/Covid-19-Shiny-Dashboard-Using-Python/blob/main/screenshots/hospitalisations.png)

![Vaccination](https://github.com/ElBaron86/Covid-19-Shiny-Dashboard-Using-Python/blob/main/screenshots/vaccination.png)


## Sources

I would like to thank the following sources for providing the data and the inspiration for this project:

- [vaccinations](https://www.data.gouv.fr/fr/datasets/donnees-relatives-aux-personnes-vaccinees-contre-la-covid-19-1/)

- [indicateurs-suivi](https://www.data.gouv.fr/fr/datasets/synthese-des-indicateurs-de-suivi-de-lepidemie-covid-19/)

- [communes-departement-region](https://www.data.gouv.fr/fr/datasets/communes-de-france-base-des-codes-postaux/)

- [geojson files](https://france-geojson.gregoiredavid.fr/)


