import pandas as pd
import re

def fusionner_csvs():
    df1 = pd.read_csv("./offres_rekrute_mecanique.csv", encoding="utf-8-sig", sep=",", engine='python', on_bad_lines='skip')
    df2 = pd.read_csv("./offres_emploima.csv", encoding="utf-8-sig", sep=",", engine='python', on_bad_lines='skip')
    df3 = pd.read_csv("./offres_dreamjob_mecanique.csv", encoding="utf-8-sig", sep=",", engine='python', on_bad_lines='skip')

    df1.columns = df1.columns.str.strip()
    df2.columns = df2.columns.str.strip()
    df3.columns = df3.columns.str.strip()

    ordre_logique = ["Titre du poste","Entreprise","Ville", "Secteur d'activité", "Contrat proposé", "Niveau d'étude",	
                    "Expérience",	"Compétences techniques", "Langues", "Soft skills", "Lien de l'offre" 	]

    toutes_les_colonnes = list(set(df1.columns) | set(df2.columns) | set(df3.columns))
    for col in toutes_les_colonnes:
        if col not in ordre_logique:
            ordre_logique.append(col)

    df1_aligne = df1.reindex(columns=ordre_logique)
    df2_aligne = df2.reindex(columns=ordre_logique)
    df3_aligne = df3.reindex(columns=ordre_logique)

    df_bis = pd.concat([df1_aligne, df2_aligne, df3_aligne], ignore_index=True)

    df_bis = df_bis.astype(object)
    df_bis.fillna("Non spécifié", inplace=True)

    return df_bis



def nettoyer_donnees(df_bis):
    df_bis.drop_duplicates(subset=["Titre du poste", "Entreprise"], keep="first", inplace=True)

    niveau = df_bis["Niveau d'étude"].str.extract(r'(Bac\s*\+\s*\d+)', expand=False)
    df_bis["Niveau d'étude"] = niveau.fillna(df_bis["Niveau d'étude"])

    df_bis = df_bis[~df_bis["Titre du poste"].str.lower().str.contains(
        "téléconseiller|télévendeur|chargé de clientèle|service client|recouvrement", na=False)]

    df_bis = df_bis.replace("Autres", "Non spécifié")
    df_bis["Langues"] = (df_bis["Langues"].str.replace("English", "Anglais", regex=False)
                                        .str.replace("Francais", "Français", regex=False))
    df_bis["Ville"] = df_bis["Ville"].replace(["Maroc", "Tout le maroc"], "Non spécifié")
    df_bis["Ville"] = df_bis["Ville"].str.lower()
    df_bis["Ville"] = df_bis["Ville"].str.capitalize()

    correction_villes = {
        "Mohammédia": "Mohammedia",
        "Meknes": "Meknès",
        "Ksar el kébir": "Ksar El Kébir",
        "Ain sebaa": "Casablanca",
        "Tit mellill": "Casablanca",
        "Tit mellil" : "Casablanca",
        "Lissasfa": "Casablanca",
        "Casablanca ain sebaa": "Casablanca",
        "Casablanca/bouskoura": "Bouskoura",
        "Casablanca-nouaceur": "Nouaceur",
        "Casablanca-chefchaouen" : "Casablanca",
        "Technopolis": "Salé",
        "Parc technopolis rabat": "Salé",
        "Taliouine- askaoune": "Taliouine",
        "Taliouine - askaoun": "Taliouine",
        "Chtouka ait baha - agadir": "Agadir"
        }
    df_bis["Ville"] = df_bis["Ville"].replace(correction_villes)

    def nettoyer_texte_experience(exp):
        if "non spécifié" in str(exp).lower() or pd.isna(exp):
            return "Non spécifié"

        texte = str(exp).lower()

        if "-1" in texte or "jeune diplômé" in texte:
            return "0 an"

        if "débutant" in texte:
            return "2 ans"

        nombres = re.findall(r"\d+", texte)

        if len(nombres) == 2:
            return f"{nombres[0]} à {nombres[1]} ans"
        elif len(nombres) == 1:
            return f"{nombres[0]} ans"

        return "Non spécifié"

    df_bis["Expérience"] = df_bis["Expérience"].apply(nettoyer_texte_experience)
    nb_non_specifies = df_bis.eq("Non spécifié").sum(axis=1)
    # Affichage de la répartition
    print(nb_non_specifies.value_counts().sort_index())

    def experience_max(exp):
        nombres = re.findall(r"\d+", str(exp))
        if not nombres:
            return 0
        return max(map(int, nombres))

    df_bis = df_bis[nb_non_specifies <= 3]
    df_bis = df_bis[df_bis["Expérience"].apply(experience_max) <= 10]

    # Nombre d'offres restantes
    print("Nombre d'offres :", len(df_bis))

    return df_bis

