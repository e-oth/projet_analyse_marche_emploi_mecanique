import pandas as pd
import re

# Partie fusion
def fusionner_csvs():
    df1 = pd.read_csv("./offres_rekrute_mecanique.csv", encoding="utf-8-sig", sep=",", engine='python', on_bad_lines='skip')
    df2 = pd.read_csv("./offres_emploima.csv", encoding="utf-8-sig", sep=",", engine='python', on_bad_lines='skip')
    df3 = pd.read_csv("./offres_dreamjob_mecanique.csv", encoding="utf-8-sig", sep=",", engine='python', on_bad_lines='skip')

    df_bis = pd.concat([df1, df2, df3], ignore_index=True)

    df_bis = df_bis.astype(object)                   # Conversion des colonnes au type objet afin de faciliter le traitement
    df_bis.fillna("Non spécifié", inplace=True)
    print("Après fusion :", len(df_bis))
    return df_bis

# Partie nettoyage et uniformisation
def nettoyer_donnees(df_bis):
    df_bis.drop_duplicates(subset=["Titre du poste", "Entreprise"], keep="first", inplace=True)
    print("Après suppression des doublons :", len(df_bis))

    # Uniformisation de l ecriture du niveau d etude
    niveau = df_bis["Niveau d'étude"].str.extract(r'(Bac\s*\+\s*\d+)', expand=False)
    df_bis["Niveau d'étude"] = niveau.fillna(df_bis["Niveau d'étude"])
    df_bis["Niveau d'étude"] = (df_bis["Niveau d'étude"].str.strip()
                                                        .str.replace(r"\s*\+\s*", "+", regex=True)
                                                        .str.title())

    # Suppression des offres non pertinentes
    df_bis = df_bis[~df_bis["Titre du poste"].str.lower().str.contains(
        "téléconseiller|télévendeur|chargé de clientèle|maroquinerie|recouvrement|ambulancier|operateur de câblage|serivce client|
        ressources humaines|chargé de recrutement|chargé rh|assistant rh|rh"
        ,na=False)]

    df_bis = df_bis.replace(["Autres","Non Spécifié"], "Non spécifié")

    # Correction de faux positifs
    liens_faux_positifs_anapec = [
    "https://www.dreamjob.ma/emploi/stellantis-recrute-operateurs/",
    "https://www.dreamjob.ma/emploi/grande-campagne-de-recrutement-calliope-plusieurs-postes-a-saisir-partout-au-maroc/",
    "https://www.dreamjob.ma/emploi/lear-morocco-recrute-4-postes-strategiques-a-pourvoir-a-tanger-et-meknes/",
    "https://www.dreamjob.ma/emploi/continental-est-a-la-recherche-de-5-profils/",
    "https://www.dreamjob.ma/emploi/sebn-ma-recrute-plusieurs-profils-2023/" ]
    df_bis.loc[df_bis["Lien de l'offre"].isin(liens_faux_positifs_anapec),
                      "Contrat proposé"] = "Non spécifié"
    
    faux_positifs_etudes = {
        "https://www.dreamjob.ma/emploi/super-auto-group-lance-une-campagne-de-recrutement-pour-divers-postes/": "Bac+5",
        "https://www.dreamjob.ma/emploi/dxc-cdg-ouvre-11-postes-a-rabat/": "Bac+5",
        "https://www.dreamjob.ma/emploi/dxc-cdg-lance-une-campagne-de-recrutement-17-postes-ouverts/": "Bac+5",
        "https://www.dreamjob.ma/emploi/centrale-automobile-cherifienne-cac-lance-une-campagne-de-recrutement-pour-divers-postes/": "Bac+5",
        "https://www.dreamjob.ma/emploi/dxc-technology-morocco-lance-une-campagne-de-recrutement-pour-divers-postes/": "Bac+5",
        "https://www.dreamjob.ma/emploi/aiguebelle-lance-une-campagne-de-recrutement-pour-divers-postes/": "Bac+5",
        "https://www.dreamjob.ma/emploi/somacos-recrute-a-meknes-plus-de-10-profils-en-cdi-et-cdd/": "Bac+2",
        "https://www.dreamjob.ma/emploi/8-postes-ouverts-chez-somacos-a-meknes/": "Bac+2"
    }
    df_bis["Niveau d'étude"] = df_bis["Lien de l'offre"].map(faux_positifs_etudes).fillna(df_bis["Niveau d'étude"])

    # Uniformisation des langues
    df_bis["Langues"] = (df_bis["Langues"].str.replace("English", "Anglais", regex=False)
                                        .str.replace("Francais", "Français", regex=False))
    
    # Uniformisation des secteurs
    df_bis["Secteur d'activité"] = (df_bis["Secteur d'activité"].str.replace("BTP", "Construction", regex=False)
                                                                .str.replace("Btp", "Construction")
                                                                .str.replace("Mines", "Minier", regex=False))
    
    # Uniformisation des soft skills
    df_bis["Soft skills"] = (df_bis["Soft skills"].str.replace("Communiquer", "Communication")
                                                  .str.replace("Organisé", "Organisation")
                                                  .str.replace("Autonome", "Autonomie")
                                                  .str.replace("Créatif", "Créativité")
                                                  .str.replace("Travailler en équipe", "Travail en équipe"))
    
    df_bis["Contrat proposé"] = df_bis["Contrat proposé"].str.replace("Autre", "Non spécifié")

    df_bis["Secteur d'activité"] = df_bis["Secteur d'activité"].replace(
                                   ["Autres services", "Autres Industries", "Indifférent"], "Non spécifié")

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
        "Chtouka ait baha - agadir": "Agadir",
        "Temara" : "Témara",
        "Maroc": "Non spécifié",
        "Tout le maroc": "Non spécifié"
        }
    df_bis["Ville"] = df_bis["Ville"].replace(correction_villes)
    
    # Uniformisation des informations relatives à l'expérience
    def nettoyer_texte_experience(exp):
        if "non spécifié" in str(exp).lower() or pd.isna(exp):
            return "Non spécifié"

        texte = str(exp).lower()

        if "-1" in texte or "jeune diplômé" in texte:
            return "0 an"

        if "débutant" in texte:
            return "2 ans"

        nombres = [int(n) for n in re.findall(r"\d+", texte)]

        if len(nombres) == 2:
            return f"{nombres[0]} à {nombres[1]} ans"

        elif len(nombres) == 1:
            if nombres[0] == 1:
                return "1 an"
            elif nombres[0] == 0:
                return "0 an"
            else:
                return f"{nombres[0]} ans"

        return "Non spécifié"

    df_bis["Expérience"] = df_bis["Expérience"].apply(nettoyer_texte_experience)

    nb_non_specifies = df_bis.eq("Non spécifié").sum(axis=1)
    # Affichage de la répartition de "Non specifie"
    print(nb_non_specifies.value_counts().sort_index())

    def experience_max(exp):
        nombres = re.findall(r"\d+", str(exp))
        if not nombres:
            return 0
        return max(map(int, nombres))
    
    # Calcul de la moyenne pour l'application
    def experience_moyenne(exp):
        nombres = re.findall(r"\d+", str(exp))
        if len(nombres) == 2:
            return (int(nombres[0]) + int(nombres[1])) / 2
        elif len(nombres) == 1:
            return int(nombres[0])
        return None

    # Filtrage par pertinence et credibilite 
    df_bis = df_bis[nb_non_specifies <= 3]
    df_bis = df_bis[df_bis["Expérience"].apply(experience_max) <= 10]
    df_bis["Expérience numérique"] = df_bis["Expérience"].apply(experience_moyenne) # Colonne fictive pour l'application

    # Nombre d'offres restantes
    print("Nombre d'offres :", len(df_bis))

    return df_bis

if __name__ == "__main__":
    from export_sql import exporter_sql

    df = fusionner_csvs()
    df = nettoyer_donnees(df)
    
    df.to_csv("ws_merged.csv", index=False, encoding="utf-8-sig")
    print("Fichier CSV mis à jour.")

    exporter_sql(df, "marche_emploi_mecanique.db")
    print("Base SQLite mise à jour.")

