import pandas as pd
import re
from bs4 import BeautifulSoup

liste_soft_skills = [
    "communication", "communiquer", "esprit d'équipe", "travail en équipe", "travailler en équipe",
    "autonomie","autonome", "rigueur", "organisation", "organisé", "créativité", "créatif",
    "leadership", "gestion de projet","innovation", "résolution de problèmes", "adaptabilité",
    "force de proposition", "proactivité", "relationnel", "initiative", "polyvalence", "flexibilité", 
    "sens de l'organisation", "réactivité", "esprit d'analyse"
]
liste_secteurs = [
    "automobile", "aéronautique", "métallurgie", "btp", "construction",
    "énergie", "agroalimentaire", "ferroviaire", "naval", "chimie",
    "plasturgie", "minier", "logistique", "bureau d'études",
    "pharmaceutique", "procédés", "recherche scientifique"
]

def nettoyer_texte(texte):
    return re.sub(r"[;\n\r]+", " ", texte).strip()                                       
# Fonctions d'analyse du texte
def detecter_langues(texte):
    texte = texte.lower()
    langues = []
    if "français" in texte or "francais" in texte:
        langues.append("Français")
    if "anglais" in texte or "english" in texte:
        langues.append("Anglais")
    if "arabe" in texte:
        langues.append("Arabe")
    return ", ".join(langues) if langues else "Non spécifié"

def detecter_etude(texte):
    texte = texte.lower()
    diplome = ["master", "bac+5", "bac+3", "bac+2", "licence", "deug", "dut", "bts"]
    for x in diplome:
        if x in texte:
            return x
    else:
        return "Non spécifié" 

def detecter_secteurs(texte):
    texte = texte.lower()
    secteurs_trouves = []
    for secteur in liste_secteurs:
        if secteur.lower() in texte:
            if secteur.capitalize() not in secteurs_trouves:                    
                secteurs_trouves.append(secteur.capitalize())
    if secteurs_trouves:
        return ", ".join(secteurs_trouves)
    else:
        return "Non spécifié"
    
def detecter_soft_skills(texte):
    texte = texte.lower()
    soft_skills_trouvees = []
    for skill in liste_soft_skills:
        if skill in texte:
            if skill.capitalize() not in soft_skills_trouvees:                   
                soft_skills_trouvees.append(skill.capitalize())
    if soft_skills_trouvees :
        return ", ".join(soft_skills_trouvees)
    else:
        return "Non spécifié"
# Fonction d'extraction par balises (Contrat/Experience/Compétences)   
def detecter_information(bloc, etiquette):
    for li in bloc.find_all("li"):
        texte_li = li.get_text(strip=True)

        if etiquette in texte_li:
            balise_strong = li.find("strong")
            if balise_strong is not None:
                return balise_strong.get_text(strip=True)
    return "Non spécifié"

#Traitement du titre/ville
def separer_titre_ville(titre):
    if " - " in titre:
        poste, ville = titre.rsplit(" - ", 1)                
        return poste.strip(), ville.strip()
    else:
        return titre.strip(), "Non spécifié"
    
def scraper_emploi(chemin_html="outerhtml.txt"):
    with open(chemin_html, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    liste_offres = []

    for bloc in soup.select("div.card.card-job"):

        titre_tag = bloc.select_one("h3 a")
        if titre_tag is None:
            continue

        titre = titre_tag.get_text(strip=True)
        lien = titre_tag.get("href", "")

        titre_poste, ville_titre = separer_titre_ville(titre) 

        texte_bloc = bloc.text.lower()
        entreprise_tag = bloc.find("a", class_="company-name") or bloc.find("div", class_="company")
        entreprise = entreprise_tag.text.strip() if entreprise_tag else "Non spécifié"


        offre = {"Titre du poste": nettoyer_texte(titre_poste),
                "Entreprise": nettoyer_texte(entreprise),
                "Ville": ville_titre,
                "Secteur d'activité": detecter_secteurs(texte_bloc),
                "Contrat proposé": detecter_information(bloc, "Contrat proposé"),
                "Niveau d'étude": detecter_etude(texte_bloc).capitalize(),
                "Expérience": detecter_information(bloc, "Niveau d'expérience"),
                "Compétences techniques": detecter_information(bloc, "Compétences clés").replace(" - ", ","),
                "Langues": detecter_langues(texte_bloc),
                "Soft skills": detecter_soft_skills(texte_bloc),
                "Lien de l'offre": lien if lien.startswith("http") else "https://www.emploi.ma" + lien,}
        liste_offres.append(offre)

# Exportation des offres vers un fichier CSV
    if liste_offres:
        df = pd.DataFrame(liste_offres)
        df.to_csv("offres_emploima.csv", index=False, sep=",", encoding="utf-8-sig")
        print(f"Extraction: {len(df)} offres")
        return df
    else:
        print("Aucune offre trouvée dans le fichier HTML.")
        return pd.DataFrame()
    
if __name__ == "__main__":
    scraper_emploi()