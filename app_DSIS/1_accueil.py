import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Analyse du marché de l'emploi", layout="wide")

langue = st.sidebar.selectbox("Language / Langue",["Français", "English"])

if langue == "Français":
    st.title("Analyse du marché de l'emploi en génie mécanique")
else:
    st.title("Mechanical Engineering Job Market Analysis")

if langue == "Français":
    st.write("Application développée dans le cadre d'un stage au HCP.")
else:
    st.write("Application developed during an internship at HCP.")

# Ajout de la couleur rouge pour les bouttons
st.markdown("""
<style>

.stButton > button,
.stDownloadButton > button {
    background-color: #d32f2f !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background-color: #b71c1c !important;
}

section[data-testid="stSidebar"] button {
    background-color: #d32f2f !important;
    color: white !important;
    border: none !important;
}

section[data-testid="stSidebar"] button:hover {
    background-color: #b71c1c !important;
}

</style>
""", unsafe_allow_html=True)



table = "offres" if langue == "Français" else "offres_en"

with sqlite3.connect("marche_emploi_mecanique.db") as connection:
    df = pd.read_sql_query(f"SELECT * FROM {table}", connection)

if langue == "Français":
    VILLE = "Ville"
    SECTEUR = "Secteur d'activité"
    ENTREPRISE = "Entreprise"
    TECH = "Compétences techniques"
    LANGUES = "Langues"
    CONTRAT = "Contrat proposé"
    ETUDES = "Niveau d'étude"
    TITRE = "Titre du poste"
    EXPERIENCE = "Expérience"
    EXP_NUM = "Expérience numérique"

    TOUS = "Tous"
    TOUTES = "Toutes"
    NON_SPEC = "Non spécifié"

else:
    VILLE = "City"
    SECTEUR = "Sector"
    ENTREPRISE = "Company"
    TECH = "Technical skills"
    LANGUES = "Languages"
    CONTRAT = "Contract"
    ETUDES = "Education level"
    TITRE = "Job title"
    EXPERIENCE = "Experience"
    EXP_NUM = "Numeric experience"

    TOUS = "All"
    TOUTES = "All"
    NON_SPEC = "Not specified"

colonnes = {
    VILLE: TOUTES,
    SECTEUR: TOUS,
    ENTREPRISE: TOUTES,
    TECH: TOUTES,
    LANGUES: TOUTES,
    CONTRAT: TOUS,
    ETUDES: TOUS,
    TITRE: TOUS,
    EXPERIENCE: TOUTES,
    "Soft skills": TOUS
}

filtres = {}

# Initialisation des filtres
for colonne, defaut in colonnes.items():
    if colonne not in st.session_state:
        st.session_state[colonne] = defaut             # Conservation des donnees lorsque la page est actualisee

st.sidebar.markdown("Filtres" if langue == "Français" else "Filters")

filtres = {}
# Découpage des colonnes contenant plusieurs valeurs séparées par des virgules
for colonne, defaut in colonnes.items():
    if colonne in [SECTEUR, TECH, "Soft skills", LANGUES]:
        options = (df[colonne].dropna().str.split(",").explode().str.strip().unique().tolist())
    else:
        options = df[colonne].dropna().unique().tolist()

    filtres[colonne] = (st.sidebar.selectbox(colonne,[defaut] + sorted(options),               # Creation du menu deroulant
                        key=colonne),defaut)
    
st.sidebar.divider()

if st.sidebar.button("Réinitialiser" if langue == "Français" else "Reset"):
    for colonne in colonnes:
        st.session_state.pop(colonne, None)
    st.rerun()

# Filtrage des données selon les choix de l'utilisateur
for colonne, (valeur, valeur_par_defaut) in filtres.items():
    if valeur != valeur_par_defaut:
        if colonne in [SECTEUR, TECH, "Soft skills", LANGUES]:
            df = df[df[colonne].str.contains(valeur, na=False)]
        else:
            df = df[df[colonne] == valeur]

recherche = st.text_input("Recherche" if langue == "Français" else "Search")

def concatener_ligne(ligne):
    return " ".join(map(str, ligne))

if recherche:
    combined_rows = df.fillna("").apply(concatener_ligne, axis=1)
    df = df[combined_rows.str.contains(recherche, case=False, na=False)]
    
st.subheader("Statistiques générales" if langue == "Français" else "General statistics")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Offres d'emploi" if langue == "Français" else "Job offers", len(df))
c2.metric(ENTREPRISE, df[df[ENTREPRISE] != NON_SPEC][ENTREPRISE].nunique())
c3.metric(VILLE, df[df[VILLE] != NON_SPEC][VILLE].nunique())
c4.metric(SECTEUR, df[df[SECTEUR] != 
                             NON_SPEC][SECTEUR]
                             .str.split(",").explode().str.strip().nunique())
moyenne = df[EXP_NUM].mean()

titre_exp = ("Expérience moyenne requise"
             if langue == "Français"
             else "Average required experience")

if len(df) == 0 or pd.isna(moyenne):
    c5.metric(titre_exp, "-")
else:
    c5.metric(titre_exp, f"{moyenne:.1f} years" if langue == "English"
                                         else f"{moyenne:.1f} ans")

st.subheader("Tableau général des offres" if langue == "Français" else "General job offers table")
df.index += 1                        # Indexation des offres a partir de 1

st.dataframe(df.drop(columns=[EXP_NUM]), use_container_width=True)

st.download_button("Télécharger le CSV" if langue == "Français" else "Download CSV",
                   df.drop(columns=[EXP_NUM]).to_csv(index=False).encode("utf-8"),
                   file_name="offres.csv",mime="text/csv")
