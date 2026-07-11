import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Analyse du marché de l'emploi", layout="wide")

st.title("Analyse du marché de l'emploi en génie mécanique")
st.write("Application développée dans le cadre d'un stage au HCP.")

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


recherche = st.text_input("Recherche")

if recherche:
    # 1. Convert all columns to strings and combine them horizontally into a single text block per row
    combined_rows = df.astype(str).agg(' '.join, axis=1)
    
    # 2. Filter the original DataFrame if that combined text block contains your search term
    df = df[combined_rows.str.contains(recherche, case=False, na=False)]
    
st.subheader("Statistiques générales")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Offres", len(df))
c2.metric("Entreprises", df["Entreprise"].nunique())
c3.metric("Villes", df["Ville"].nunique())
c4.metric("Secteurs", df["Secteur d'activité"].nunique())

st.subheader("Tableau général des offres")
df.index += 1

st.dataframe(df, use_container_width=True)

st.download_button("Télécharger le CSV",df.to_csv(index=False).encode("utf-8"),
                   file_name="offres.csv",mime="text/csv")
