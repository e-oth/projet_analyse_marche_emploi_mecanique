import sqlite3
import pandas as pd 

def exporter_sql(df, chemin_db="marche_emploi_mecanique.db"):
    connection = sqlite3.connect(chemin_db)
    df.to_sql("offres", connection, if_exists="replace", index=False)
    connection.close()
    