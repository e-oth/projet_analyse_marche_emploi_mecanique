import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(layout="wide")
st.title("Dashboard")
connection = sqlite3.connect("marche_emploi_mecanique.db")
df = pd.read_sql_query("SELECT * FROM offres", connection)
connection.close()

colonnes = {
    "Ville": "Toutes",
    "Secteur d'activité": "Tous",
    "Entreprise": "Tous",
    "Compétences techniques": "Toutes",
    "Langues": "Tous",
    "Contrat proposé": "Tous",
    "Titre du poste": "Tous",
    "Expérience": "Tous",
    "Soft skills": "Tous"
}

filtres = {}
for colonne, defaut in colonnes.items():
    if colonne in ["Secteur d'activité", "Compétences techniques", "Soft skills", "Langues"]:
        options = (df[colonne].dropna().str.split(",").explode().str.strip().unique().tolist())
    else:
        options = df[colonne].dropna().unique().tolist()
    filtres[colonne] = (st.sidebar.selectbox(colonne, [defaut] + sorted(options)),defaut)

for colonne, (valeur, valeur_par_defaut) in filtres.items():
    if valeur != valeur_par_defaut:
        if colonne in ["Secteur d'activité", "Compétences techniques", "Soft skills", "Langues"]:
            df = df[df[colonne].str.contains(valeur, na=False)]
        else:
            df = df[df[colonne] == valeur]

tab1, tab2, tab3 = st.tabs([ "Vue Macro-Économique",
                             "Analyse Sectorielle",
                             "Analyse des Compétences"])

with tab1:

    st.subheader("Répartition des offres par ville")
    villes = df[df["Ville"] != "Non spécifié"]["Ville"].value_counts().head(10)
    st.bar_chart(villes)

    st.subheader("Répartition des contrats")
    st.subheader("Niveau d'étude")

with tab2:

    st.subheader("Top secteurs")
    secteurs = df[df["Secteur d'activité"] != "Non spécifié"]["Secteur d'activité"].value_counts().head(10)
    st.bar_chart(secteurs)

    st.subheader("Top entreprises")

with tab3:

    st.subheader("Compétences techniques")

    competences = (df[df["Compétences techniques"] != "Non spécifié"]["Compétences techniques"].dropna().str.split(",").explode().str.strip())
    st.bar_chart(competences.value_counts().head(15))

    
    