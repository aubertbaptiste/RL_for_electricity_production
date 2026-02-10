import pandas as pd
import numpy as np
    

def get_scenario(df:pd.DataFrame):
    date = df["Date"].drop_duplicates().sample(1).tolist()
    df_day = df[df["Date"]==date[0]]
    df_day = df_day.sort_values("Heure")
    df_day_utils =pd.DataFrame()
    df_day_utils["Heure"]=df_day["Heure"]
    df_day_utils["Consommation"] = df_day["Fioul (MW)"] + df_day["Charbon (MW)"] + df_day["Gaz (MW)"] + df_day["Eolien (MW)"]+df_day["Eolien terrestre (MW)"]+df_day["Eolien offshore (MW)"]+df_day["Solaire (MW)"]+df_day["Hydraulique (MW)"]
    df_day_utils["Renouvelable"] = df_day["Eolien (MW)"]+df_day["Eolien terrestre (MW)"]+df_day["Eolien offshore (MW)"]+df_day["Solaire (MW)"]+df_day["Hydraulique (MW)"]
    grouping_index = pd.Series(range(len(df_day_utils))) // 4
    new_df = df_day_utils.groupby(grouping_index.values).mean(numeric_only=True)
    scenario = new_df.to_numpy().astype(int)
    return scenario,scenario[:,0].max(),scenario[:,1].max() # On récupère les max de consommation et de production pour la discretisation
