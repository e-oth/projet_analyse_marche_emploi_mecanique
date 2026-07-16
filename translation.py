import sqlite3
import pandas as pd

def creer_base_anglaise():
    with sqlite3.connect("marche_emploi_mecanique.db") as connection:

        df = pd.read_sql_query("SELECT * FROM offres", connection)
        df_en = df.copy()

        traduction_langues = {"Français": "French",
                            "Anglais": "English",
                            "Arabe": "Arabic"
                            }

        for fr, en in traduction_langues.items():
            df_en["Langues"] = df_en["Langues"].str.replace(fr, en, regex=False)

        traduction_villes = {"Tanger": "Tangier",
                             "Fès": "Fez",
                             "Meknès": "Meknes"
                         }
        for fr, en in traduction_villes.items():
            df_en["Ville"] = df_en["Ville"].str.replace(fr, en, regex=False)

        
        traduction_contrat = {"CDI": "Permanent contract",
                            "CDD": "Fixed-term contract",
                            "Stage": "Internship",
                            "Intérim": "Temporary contract",
                            "ANAPEC": "ANAPEC contract"
                            }

        df_en["Contrat proposé"] = df_en["Contrat proposé"].replace(traduction_contrat)

        traduction_secteurs = {
            "Automobile": "Automotive",
            "Logistique": "Logistics",
            "Construction": "Construction",
            "Procédés": "Process Engineering",
            "Agroalimentaire": "Food Industry",
            "Énergie": "Energy",
            "Aéronautique": "Aeronautics",
            "Ferroviaire": "Railway",
            "Chimie": "Chemicals",
            "Pharmaceutique": "Pharmaceutical Industry",
            "Pharmacie": "Pharmaceuticals",
            "Plasturgie": "Plastics",
            "Naval": "Shipbuilding",
            "Métallurgie": "Metallurgy",
            "Motos": "Motorcycles",
            "Informatique": "Information Technology",
            "Cycles": "Cycling",
            "Spatial": "Aerospace",
            "Telecom": "Telecommunications",
            "Santé": "Healthcare",
            "Génie Civil": "Civil Engineering",
            "Electro-mécanique": "Electromechanical Engineering",
            "Minier": "Mining",
            "Mécanique": "Mechanical Engineering",
            "Extraction": "Extraction",
            "Sidérurgie": "Steel Industry",
            "Centre d'appels": "Call Center",
            "Agriculture": "Agriculture",
            "Electricité": "Electricity",
            "Conseil": "Consulting",
            "Hôtellerie": "Hospitality",
            "Peintures": "Paints",
            "Intérim": "Temporary Employment",
            "Textile": "Textiles",
            "Pétrole": "Oil & Gas",
            "Marketing Direct": "Direct Marketing",
            "Finance": "Finance",
            "Comptabilité": "Accounting",
            "Communication": "Communication"
        }

        for fr, en in traduction_secteurs.items():
            df_en["Secteur d'activité"] = (df_en["Secteur d'activité"]
                                        .str.replace(fr, en, regex=False))

        traduction_soft = {
            "Organisation": "Organization",
            "Rigueur": "Attention to detail",
            "Communication": "Communication",
            "Innovation": "Innovation",
            "Autonomie": "Autonomy",
            "Travail en équipe": "Teamwork",
            "Leadership": "Leadership",
            "Réactivité": "Responsiveness",
            "Relationnel": "Interpersonal skills",
            "Résolution de problèmes": "Problem solving",
            "Initiative": "Initiative",
            "Gestion de projet": "Project management",
            "Créativité": "Creativity",
            "Flexibilité": "Flexibility",
            "Adaptabilité": "Adaptability",
            "Proactivité": "Proactivity",
            "Force de proposition": "Proactiveness",
            "Polyvalence": "Versatility",
            "Sens de l'organisation": "Organizational skills",
            "Esprit d'analyse": "Analytical thinking",
            "Esprit d'équipe": "Team spirit"
        }

        for fr, en in traduction_soft.items():
            df_en["Soft skills"] = (df_en["Soft skills"]
                                        .str.replace(fr, en, regex=False))
            
        traduction_compet = {
            "Modélisation" : "Modeling",
            "Automatisme"  : "Automation"
        }

        for fr, en in traduction_compet.items():
            df_en["Compétences techniques"] = (df_en["Compétences techniques"]
                                        .str.replace(fr, en, regex=False))
            
        traduction_experience = {
            "à" : "to",
            "ans" : "years",
            "an" : "year"
        }
        for fr, en in traduction_experience.items():
            df_en["Expérience"] = (df_en["Expérience"]
                                        .str.replace(fr, en, regex=False))


        df_en = df_en.rename(columns={
            "Titre du poste": "Job title",
            "Entreprise": "Company",
            "Ville": "City",
            "Secteur d'activité": "Sector",
            "Contrat proposé": "Contract",
            "Niveau d'étude": "Education level",
            "Expérience": "Experience",
            "Expérience numérique": "Numeric experience",
            "Compétences techniques": "Technical skills",
            "Langues": "Languages",
            "Soft skills": "Soft skills",
            "Lien de l'offre": "Offer link"
        })

        df_en = df_en.replace("Non spécifié", "Not specified")

        df_en.to_sql("offres_en", connection, if_exists="replace", index=False)
    print("Base anglaise créée.")

if __name__ == "__main__":
    creer_base_anglaise()