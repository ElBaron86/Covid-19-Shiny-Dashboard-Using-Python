"""This script is used to clean all the data that requires cleaning.
The cleaning process is different for each dataset, so the modifications are explained in this script.

Returns:
----------------
The cleaned data without the cumulative vaccination columns and adding vaccination names instead of codes.

Sources:
----------------
all the vascination data are from https://www.data.gouv.fr/fr/datasets/donnees-relatives-aux-personnes-vaccinees-contre-la-covid-19-1/
Vaccination data includes the following files:
    - vacsi-v-reg-2023-07-13-15h51.csv
    - vacsi-v-dep-2023-07-13-15h51.csv
    - vacsi-s-a-reg.csv
    - vacsi-s-a-dep.csv

- communes-departement-region : https://www.data.gouv.fr/fr/datasets/communes-de-france-base-des-codes-postaux/
- indicateur-suivi.csv : https://www.data.gouv.fr/fr/datasets/synthese-des-indicateurs-de-suivi-de-lepidemie-covid-19/
"""
# Modules importation
import pandas as pd
import numpy as np

# ------------------------------------------------- #
######## Vaccination Data ########
# ------------------------------------------------- #

#TODO: Add a zip to decompress the data
def clean_vaccination_data(path_locs : str = "data/communes-departement-region.csv",
                            path_vaccination_reg : str = "data/vacsi-v-reg-2023-07-13-15h51.csv",
                            path_vaccination_dep : str = "data/vacsi-v-dep-2023-07-13-15h51.csv"):
    
    # Loading the required files
    locs = pd.read_csv(path_locs, usecols=["code_departement", "code_region"])
    vacci_reg = pd.read_csv(path_vaccination_reg, sep=";")
    vacci_dep = pd.read_csv(path_vaccination_dep, sep=";", low_memory=False)

    # Preprocessing the data
    vacci_dep['jour'] = pd.to_datetime(vacci_dep['jour'])
    vacci_reg['jour'] = pd.to_datetime(vacci_reg['jour'])
    vacci_reg = vacci_reg[~vacci_reg['reg'].isin([7, 8])] # Regions 7 and 8 are not in the list of regions in France
    locs.dropna(subset=['code_departement', 'code_region'], inplace=True)
    locs['code_region'] = locs['code_region'].astype(int)

    def add_zero(col):
        if len(col) == 1:
            return "0" + col
        else:
            return col
    # Adding a '0' when the code_departement is a single digit
    locs['code_departement'] = locs['code_departement'].apply(add_zero)
    locs.drop_duplicates(inplace=True)
    locs.rename(columns={"code_departement": "dep", "code_region": "reg"}, inplace=True)

    vacci_reg = vacci_reg[vacci_reg['vaccin'] != 8] # vaccination code 8 doesn't exist in the documentation
    vacci_dep = vacci_dep[vacci_dep['vaccin'] != 8]


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
    vacci_dep["vaccin"] = vacci_dep["vaccin"].map(vaccins)

    # Merging regions and departments for the vaccination data
    vacci_dep = vacci_dep.merge(locs, on="dep", how="left")
    vacci_reg = vacci_reg.merge(locs, on="reg", how="left")

    vacci_dep.dropna(subset=['reg'], inplace=True)

    vacci = vacci_reg.merge(vacci_dep, on=["jour", "vaccin", "dep", "reg"], suffixes=('_reg', '_dep'))
    vacci.to_csv("data/vaccination.csv", index=False)

    return 0


# ------------------------------------------------- #
######## Detailed Vaccination Data ########
# ------------------------------------------------- #

def clean_vaccination_detailed_data(path_locs : str = "data/communes-departement-region.csv",
                            path_vaccination_reg : str = "data/vacsi-s-a-reg.csv",
                            path_vaccination_dep : str = "data/vacsi-s-a-dep.csv"):
    
    # Loading the required files
    locs = pd.read_csv(path_locs, usecols=["code_departement", "code_region"])
    vacci_reg = pd.read_csv(path_vaccination_reg, sep=";", low_memory=False)
    vacci_dep = pd.read_csv(path_vaccination_dep, sep=";", low_memory=False)

    # Preprocessing the data
    vacci_dep['jour'] = pd.to_datetime(vacci_dep['jour'])
    vacci_reg['jour'] = pd.to_datetime(vacci_reg['jour'])
    vacci_reg = vacci_reg[~vacci_reg['reg'].isin([7, 8])] # Regions 7 and 8 are not in the list of regions in France
    locs.dropna(subset=['code_departement', 'code_region'], inplace=True)
    locs['code_region'] = locs['code_region'].astype(int)

    def add_zero(col):
        if len(col) == 1:
            return "0" + col
        else:
            return col
    # Adding a '0' when the code_departement is a single digit
    locs['code_departement'] = locs['code_departement'].apply(add_zero)
    locs.drop_duplicates(inplace=True)
    locs.rename(columns={"code_departement": "dep", "code_region": "reg"}, inplace=True)

    # Mapping the vaccine code according to the documentation
    classe_age = {0 : "Tous ages",
                4 : "0-4",
                9 : "5-9",
                11 : "10-11",
                17 : "12-17",
                24 : "18-24",
                29 : "25-29",
                39 : "30-39",
                49 : "40-49",
                59 : "50-59",
                64 : "60-64",
                74 : "65-74",
                79 : "75-79",
                80 : "80 et +"}

    vacci_reg['clage_vacsi'] = vacci_reg['clage_vacsi'].map(classe_age)
    vacci_dep['clage_vacsi'] = vacci_dep['clage_vacsi'].map(classe_age)

    # Merging regions and departments for the vaccination data
    vacci_dep = vacci_dep.merge(locs, on="dep", how="left")
    vacci_reg = vacci_reg.merge(locs, on="reg", how="left")

    vacci_dep.dropna(subset=['reg'], inplace=True)

    vacci = vacci_reg.merge(vacci_dep, on=["jour", "clage_vacsi", "dep", "reg"], suffixes=('_reg', '_dep'))
    keep_cols = ['reg','dep', 'clage_vacsi', 'jour', 'n_cum_dose1_h_reg', 'n_cum_dose1_f_reg', 'n_cum_dose1_h_dep',
                'n_cum_dose1_f_dep', 'n_cum_rappel_h_reg', 'n_cum_rappel_f_reg', 'n_cum_rappel_h_dep', 'n_cum_rappel_f_dep',
                'n_cum_2_rappel_h_reg', 'n_cum_2_rappel_f_reg', 'n_cum_2_rappel_h_dep', 'n_cum_2_rappel_f_dep', 'n_cum_3_rappel_h_reg',
                'n_cum_3_rappel_f_reg', 'n_cum_3_rappel_h_dep', 'n_cum_3_rappel_f_dep']
    vacci = vacci[keep_cols]
    vacci.to_csv("data/vaccination_detailed.csv", index=False)

    return 0

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
    indicateurs.to_csv("data/indicateur-suivi.csv", index=False)

    return 0

if __name__ == "__main__":
    print("="*50)
    print("Data cleaning is starting...")
    clean_vaccination_data()
    print("Vaccination data is cleaned!")
    clean_vaccination_detailed_data()
    print("Vaccination detailed data is cleaned!")
    clean_hosp_data()
    print("Hospitalizations data is cleaned!")
    print("Data cleaning is done!")