"""This script is used to clean all the data that requires cleaning.
The cleaning process is different for each dataset, so the modifications are explained in this script.

Returns: The cleaned data without the cumulative vaccination columns and adding vaccination names instead of codes.
"""
# Modules importation
import pandas as pd
import numpy as np

# ------------------------------------------------- #
######## Hospitalizations Data ########
# ------------------------------------------------- #

def clean_vaccination_region_data(path : str = "data/vacsi-v-reg-2023-07-13-15h51.csv"):

    # Data loading
    vacci_reg = pd.read_csv("data/vacsi-v-reg-2023-07-13-15h51.csv", sep=";")
    vacci_reg['jour'] = pd.to_datetime(vacci_reg['jour'])
    vacci_reg['jour'] = vacci_reg['jour'].dt.date
    # vaccination code 8 doesn't exist in the documentation
    vacci_reg = vacci_reg[vacci_reg['vaccin'] != 8]

    # vaccination names according to the metadata
    vaccins = {0 : "Tous vaccins",
                1 : "COMIRNATY-30-adulte (Pfizer/BioNTech)",
                2 : "Spikevax (Moderna)",
                3 : "Vaxzevria (AstraZeneca)",
                4 : "Janssen (Johnson&Johnson)",
                5 : "COMIRNATY-10-enfant (Pfizer/BioNTech)",
                6 : "NUVAXOVID (Novavax)",
                9 : "Spikevax Bivalent (Moderna)",
                10 : "Sanofi VidPrevtyn Beta",
                11 : "COMIRNATY-3 pédiatrique 6 m-4a (Pfizer/BioNTech)",
                12 : "Spikevax Bivalent Ori/Omi BA.5 (Moderna)"}

    vacci_reg["vaccin"] = vacci_reg["vaccin"].map(vaccins)
    # dropping cumulative columns because i'm only interested in the daily data for aggregation in the app
    vacci_reg = vacci_reg.drop(columns=[col for col in vacci_reg.columns if 'cum' in col])
    return vacci_reg


# ------------------------------------------------- #
######## Hospitalizations Data ########
# ------------------------------------------------- #

def clean_hosp_data(path : str = "data/indicateur-suivi.csv"):
    """This function is used to clean the 'indicateur-suivi' data.
    The returned data is aggregated correctly according to each variable.

    Args:
    ----------------
        path (str): The path to the 'indicateur-suivi' data.

    Returns:
    ----------------
        The cleaned hospitalizations data.

    """
    # Data loading
    indicateurs = pd.read_csv(path)

    # Data cleaning
    indicateurs['date'] = pd.to_datetime(indicateurs['date'], format='%Y-%m-%d')
    indicateurs['year'] = indicateurs['date'].dt.year  
    indicateurs['month'] = indicateurs['date'].dt.month_name()

    # Aggregating the data
    indicateurs = indicateurs.groupby(['year', 'month']).agg({'TO' : 'mean',
                                                    'incid_hosp' : 'sum',
                                                    'incid_rea' : 'sum',
                                                    'incid_rad' : 'sum',
                                                    'incid_dchosp' : 'sum',
                                                    'pos' : 'sum',
                                                    'dc_tot' : 'max',
                                                    'esms_dc' : 'max',
                                                    'dchosp' : 'max'}).reset_index()
    
    # Ordering the months
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    indicateurs.sort_values('month', key=lambda x: x.map({v: i for i, v in enumerate(month_order)}), inplace=True)

    return indicateurs