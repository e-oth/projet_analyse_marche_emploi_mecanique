import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(layout="wide")
langue = st.sidebar.selectbox(
    "Language / Langue",
    ["Français", "English"]
)
st.title("Tableau de bord" if langue == "Français" else "Dashboard")

table = "offres" if langue == "Français" else "offres_en"

st.markdown("""
<style>
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

def afficher_indicateurs(df):

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Offres d'emploi" if langue=="Français" else "Job offers", len(df))
    c2.metric(
        "Entreprises" if langue=="Français" else "Companies",
        df[df[ENTREPRISE] != NON_SPEC][ENTREPRISE].nunique()
    )

    c3.metric(
        "Villes" if langue=="Français" else "Cities",
        df[df[VILLE] != NON_SPEC][VILLE].nunique()
    )

    c4.metric(
        "Secteurs" if langue=="Français" else "Sectors",
        df[df[SECTEUR] != NON_SPEC][SECTEUR]
        .str.split(",").explode().str.strip().nunique()
    )

    moyenne = df[EXP_NUM].mean()
    if len(df) == 0 or pd.isna(moyenne):
        c5.metric(
            "Expérience moyenne requise" if langue=="Français"
            else "Average required experience","-"
        )
    else:
        c5.metric(
            "Expérience moyenne requise" if langue=="Français"
            else "Average required experience",
            f"{moyenne:.1f} ans" if langue=="Français"
            else f"{moyenne:.1f} years"
        )
                
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

coordonnees = {
    "Casablanca": (33.5731, -7.5898),
    "Tanger": (35.7595, -5.8340),
    "Kénitra": (34.2610, -6.5802),
    "Rabat": (34.0209, -6.8416),
    "Salé": (34.0331, -6.7985),
    "Nouaceur": (33.3670, -7.6210),
    "Marrakech": (31.6295, -7.9811),
    "Bouskoura": (33.4490, -7.6480),
    "Berrechid": (33.2655, -7.5875),
    "Mohammédia": (33.6861, -7.3829),
    "El jadida": (33.2316, -8.5007),
    "Agadir": (30.4278, -9.5981),
    "Meknès": (33.8935, -5.5473),
    "Tétouan": (35.5889, -5.3626),
    "Nador": (35.1688, -2.9335),
    "Jorf lasfar": (33.1167, -8.6333),
    "Fès": (34.0331, -5.0003),
    "Skhirat": (33.8500, -7.0333),
    "Had soualem": (33.4210, -7.8510),
    "Témara": (33.9287, -6.9066),
    "Sidi bennour": (32.6500, -8.4333),
    "Dar bouazza": (33.5330, -7.8330),
    "Dakhla": (23.6848, -15.9570),
    "Taliouine": (30.5290, -7.9120),
    "Ouarzazate": (30.9335, -6.9370),
    "Safi": (32.2994, -9.2372),
    "Youssoufia": (32.2460, -8.5290),
    "Oujda": (34.6814, -1.9086),
    "Benguerir": (32.2359, -7.9538),
    "Errachidia": (31.9314, -4.4247),
    "Sidi slimane": (34.2610, -5.9250),
    "Chefchaouen": (35.1714, -5.2697),
    "Fnideq": (35.8490, -5.3570),
    "Berkane": (34.9218, -2.3188),
    "Larache": (35.1932, -6.1557),
    "Oued zem": (32.8660, -6.5660),
    "Taroudant": (30.4703, -8.8769),
    "Ksar El Kébir": (35.0000, -5.9000),
}

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
for colonne, defaut in colonnes.items():
    if colonne not in st.session_state:
        st.session_state[colonne] = defaut

st.sidebar.markdown("Filtres" if langue == "Français" else "Filters")

filtres = {}
for colonne, defaut in colonnes.items():
    if colonne in [SECTEUR, TECH, "Soft skills", LANGUES]:
        options = (df[colonne].dropna().str.split(",").explode().str.strip().unique().tolist())
    else:
        options = df[colonne].dropna().unique().tolist()

    filtres[colonne] = (st.sidebar.selectbox(colonne,[defaut] + sorted(options),
                        key=colonne),defaut)
    
st.sidebar.divider()

if st.sidebar.button("Réinitialiser" if langue=="Français" else "Reset"):
    for colonne in colonnes:
        st.session_state.pop(colonne, None)
    st.rerun()

for colonne, (valeur, valeur_par_defaut) in filtres.items():
    if valeur != valeur_par_defaut:
        if colonne in [SECTEUR, TECH, "Soft skills", LANGUES]:
            df = df[df[colonne].str.contains(valeur, na=False)]
        else:
            df = df[df[colonne] == valeur]

st.caption("Les valeurs « Non spécifié » sont exclues des visualisations. "
           "Les répartitions et pourcentages sont calculés uniquement à partir "
           "des offres pour lesquelles l'information est disponible.")

tab1, tab2, tab3, tab4 = st.tabs(["Aperçu du marché",
                                  "Analyse sectorielle",
                                  "Analyse des compétences",
                                  "Aperçu géographique"]
    if langue == "Français"
    else ["Market overview",
          "Sector analysis",
          "Skills analysis",
          "Geographic overview"])

with tab1:

    st.header("Vue d'ensemble du marché"
              if langue=="Français"
              else "Market overview")
    
    afficher_indicateurs(df)

    c1, c2 = st.columns(2)

    # Villes
    with c1:
        st.subheader("Top 10 des villes")

        if len(df) == 0:
            st.info("Aucune ville disponible pour cette sélection.")

        elif filtres[VILLE][0] != TOUTES:
            st.info(f"Ville sélectionnée : **{filtres[VILLE][0]}**\n\n"
                    f"Nombre d'offres : **{len(df)}**"
            )

        else:
            villes = (df[df[VILLE] != NON_SPEC][VILLE]
                      .value_counts().head(10).sort_values())

            if villes.empty:
                st.info("Aucune ville disponible pour cette sélection.")
            else:
                fig = px.bar(
                    x=villes.values,
                    y=villes.index,
                    orientation="h",
                    text=villes.values,
                    labels={"x": "Nombre d'offres", "y": ""}
                )

                fig.update_traces(textangle=0)
                fig.update_layout(height=400)

                st.plotly_chart(fig, use_container_width=True, key="ville")

    # Contrats
    with c2:
        st.subheader("Répartition des contrats")
        if len(df) == 0:
            st.info("Aucun contrat disponible pour cette sélection.")

        elif filtres[CONTRAT][0] != TOUS:
            st.info(f"Contrat sélectionné : **{filtres[CONTRAT][0]}**\n\nNombre d'offres : **{len(df)}**")
        else:
            contrats = df[df[CONTRAT] != NON_SPEC][CONTRAT].value_counts()
            if contrats.empty:
                st.info("Aucun contrat disponible pour cette sélection.")
            else:
                fig = px.pie(
                    values=contrats.values,
                    names=contrats.index,
                    hole=0.4
                )
                fig.update_traces(textposition="inside", textinfo="percent+label")

                st.plotly_chart(fig, use_container_width=True, key="contrat")
       

    c3, c4 = st.columns(2)

    # Niveau d'étude
    with c3:
        st.subheader("Répartition du niveau d'étude")
        if filtres[ETUDES][0] == TOUS:
            etudes = df[df[ETUDES] != NON_SPEC][ETUDES].value_counts()
            if etudes.empty or len(df) == 0:
                st.info("Aucun niveau d'étude disponible pour cette sélection.")
            else:
                fig = px.pie(
                    values=etudes.values,
                    names=etudes.index,
                    hole=0.4
                )

                fig.update_traces(textposition="inside", textinfo="percent+label")

                st.plotly_chart(fig, use_container_width=True, key="niveau")
        else:
            st.info(f'Niveau d\'étude sélectionné : **{filtres[ETUDES][0]}**\n\n'
                    f'Nombre d\'offres : **{len(df)}**')

    # Profil
    with c4:
        st.subheader("Profils les plus recherchés")
        if len(df) ==0:
            st.info("Aucun profil disponible pour cette sélection.")
        else:
            mots_cles = ["ingénieur","technicien","responsable","chef","dessinateur",
                        "projeteur","conducteur","coordinateur","superviseur",
                        "inspecteur","manager","planificateur" ]

            top = {mot: df[TITRE].str.contains(mot, case=False, na=False).sum()
                for mot in mots_cles}
            top = (pd.Series(top).sort_values(ascending=True))
        
            fig = px.bar(
                x=top.values,
                y=top.index,
                orientation="h",
                text=top.values,
                labels={"x": "Nombre d'offres", "y": ""}
            )
            fig.update_traces(textangle=0)
            fig.update_layout(height=400)

            st.plotly_chart(fig, use_container_width=True, key = "experience")

with tab2:
    st.header("Vue d'ensemble du marché")
    afficher_indicateurs(df)

    c1, c2 = st.columns(2)

    # Secteurs
    with c1:
        st.subheader("Top 10 des secteurs")
        if len(df) == 0:
            st.info("Aucun secteur disponible pour cette sélection.")

        elif filtres[SECTEUR][0] != TOUS:
            st.info(f'Secteur d\'activité sélectionné : **{filtres[SECTEUR][0]}**\n\n'
                    f'Nombre d\'offres : **{len(df)}**')
            
        else:
            secteurs = (df[df[SECTEUR] != NON_SPEC][SECTEUR]
                        .dropna().str.split(",").explode().str.strip().value_counts()
                        .head(10).sort_values())
            if secteurs.empty or len(df) == 0:
                st.info("Aucun secteur disponible pour cette sélection.")
            else:
                fig = px.bar(
                    x=secteurs.values,
                    y=secteurs.index,
                    orientation="h",
                    text=secteurs.values,
                    labels={"x": "Nombre d'offres", "y": ""}
                )
                fig.update_traces(textangle=0)
                fig.update_layout(height=400)

                st.plotly_chart(fig, use_container_width=True, key = "secteur")
        
            

    # Entreprises
    with c2:
        st.subheader("Top 15 des entreprises")
        if len(df) == 0:
            st.info("Aucune entreprise disponible pour cette sélection.")

        elif filtres[ENTREPRISE][0] != TOUTES:
            st.info(f"Entreprise sélectionnée : **{filtres[ENTREPRISE][0]}**\n\nNombre d'offres : **{len(df)}**")
        else:
            entreprises = df[~df[ENTREPRISE].isin([NON_SPEC, "Confidentiel"])][ENTREPRISE].value_counts().head(15).sort_values()
            if entreprises.empty or len(df) == 0:
                st.info("Aucune entreprise disponible pour cette sélection.")
            else:
                fig = px.bar(
                    x=entreprises.values,
                    y=entreprises.index,
                    orientation="h",
                    text=entreprises.values,
                    labels={"x": "Nombre d'offres", "y": ""}
                )
                fig.update_traces(textangle=0)
                fig.update_layout(height=400)

                st.plotly_chart(fig, use_container_width=True, key = "entreprise")
        
with tab3:

    st.header("Vue d'ensemble du marché")
    afficher_indicateurs(df)

    c1, c2 = st.columns(2)

    # Competences
    with c1:
        st.subheader("Top 15 des compétences techniques")
        if len(df) == 0:
                    st.info("Aucune compétence disponible pour cette sélection.")

        elif filtres[TECH][0] != TOUTES:
            st.info(f"Compétences techniques sélectionnées: **{filtres[TECH][0]}**\n\nNombre d'offres : **{len(df)}**")
        else:
            competences = (df[df[TECH] != NON_SPEC][TECH]
                        .dropna().str.split(",").explode().str.strip().value_counts()
                        .head(15).sort_values())
            if competences.empty or len(df) == 0:
                st.info("Aucune compétence disponible pour cette sélection.")
            else:
                fig = px.bar(
                    x=competences.values,
                    y=competences.index,
                    orientation="h",
                    text=competences.values,
                    labels={"x": "Nombre d'offres", "y": ""}
                )
                fig.update_traces(textangle=0)
                fig.update_layout(height=400)

                st.plotly_chart(fig, use_container_width=True, key = "competence")
        
    
    with c2:
        st.subheader("Top 15 des soft skills")
        if len(df) == 0:
                    st.info("Aucun soft skill disponible pour cette sélection.")

        elif filtres["Soft skills"][0] != TOUS:
            st.info(f"Soft skills sélectionnés: **{filtres['Soft skills'][0]}**\n\nNombre d'offres : **{len(df)}**")
        else:
            skills = (df[df["Soft skills"] != NON_SPEC]["Soft skills"]
                        .dropna().str.split(",").explode().str.strip().value_counts()
                        .head(15).sort_values())
            if skills.empty or len(df) == 0:
                st.info("Aucun soft skill disponible pour cette sélection.")
            else:
                fig = px.bar(
                    x=skills.values,
                    y=skills.index,
                    orientation="h",
                    text=skills.values,
                    labels={"x": "Nombre d'offres", "y": ""}
                )
                fig.update_traces(textangle=0)
                fig.update_layout(height=400)

                st.plotly_chart(fig, use_container_width=True, key = "skill")

    left, center, right = st.columns([1,2,1])

    with center:
        st.subheader("Langues")

        if len(df) == 0:
            st.info("Aucune langue disponible pour cette sélection.")

        elif filtres[LANGUES][0] != TOUTES:
            st.info(f"Langue sélectionnée : **{filtres[LANGUES][0]}**\n\nNombre d'offres : **{len(df)}**")
        else:
            langues = df[df[LANGUES] != NON_SPEC][LANGUES].dropna().str.split(",").explode().str.strip().value_counts()
            if langues.empty:
                st.info("Aucune langue disponible pour cette sélection.")
            else:
                fig = px.pie(
                    values=langues.values,
                    names=langues.index,
                    hole=0.4
                )
                fig.update_traces(textposition="inside", textinfo="percent+label")
                fig.update_layout(height=550)

                st.plotly_chart(fig, use_container_width=True, key="langue")



with tab4:
    st.header("Répartition géographique des offres" if langue == "Français" else "Geographic distribution of job offers")

    # Nombre d'offres par ville
    carte = (
        df[df[VILLE] != NON_SPEC]
        .groupby(VILLE)
        .size()
        .reset_index(name="Offres")
    )

    # Coordonnées
    carte["Latitude"] = None
    carte["Longitude"] = None

    for i in carte.index:
        ville = carte.loc[i, VILLE]
        if ville in coordonnees:
            carte.loc[i, "Latitude"] = coordonnees[ville][0]
            carte.loc[i, "Longitude"] = coordonnees[ville][1]

    # Suppression des villes sans coordonnées
    carte = carte.dropna(subset=["Latitude", "Longitude"])

    if carte.empty:
        st.info("Aucune donnée géographique disponible pour cette sélection.")

    else:
        # Réduit l'écart entre les grandes et petites villes
        carte["Poids"] = np.sqrt(carte["Offres"])

        fig = px.density_map(
            carte,
            lat="Latitude",
            lon="Longitude",
            z="Poids",
            hover_name=VILLE,
            hover_data={"Offres": True},
            radius=65,
            zoom=5.5,
            center={"lat": 31.79, "lon": -7.09},
            map_style="carto-darkmatter",
            color_continuous_scale="Plasma",
            height=700,
        )

        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            coloraxis_colorbar_title="Intensité"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="carte_density"
        )