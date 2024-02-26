"""This script is used to clean all the data that requires cleaning.
The cleaning process is different for each dataset, so the modifications are explained in this script.

Returns: The cleaned data without the cumulative vaccination columns and adding vaccination names instead of codes.
"""
# Modules importation
import pandas as pd

# Data loading
vacci_reg = pd.read_csv("data/vacsi-v-reg-2023-07-13-15h51.csv", sep=";")
vacci_reg['jour'] = pd.to_datetime(vacci_reg['jour'])
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
vacci_reg.to_csv("data/vacsi-v-reg-2023-07-13-15h51.csv", index=False)

