import sqlite3
import pandas as pd 

def exporter_sql(df, chemin_db="marche_emploi_mecanique.db"):
    connection = sqlite3.connect(chemin_db)
    df.to_sql("offres", connection, if_exists="replace", index=False)
    df_verif = pd.read_sql("SELECT * FROM offres", connection)
    connection.close()
    print(df_verif.head())
    return df_verif