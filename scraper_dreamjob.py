import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from concurrent.futures import ThreadPoolExecutor

mots_cles = [
    "genie+mecanique", "maintenance", "production", "fabrication",
    "electromecanique","energetique","mecanique+industrielle", "conception+mecanique",
    "chef+projet+mecanique", "ingenieur+mecanique", "ingenieur+conception",
]
liste_competences = [
    "solidworks", "catia", "autocad", "creo", "nx", "pro/engineer","inventor", 
    "ansys", "matlab", "simulink", "abaqus", "samcef","nastran", "patran", "icem", 
    "cfd", "fea", "rdm", "cao", "dao", "conception mécanique", "modélisation",
    "fabrication additive", "gmao", "sap", "erp", "ms project", "automatisme", 
    "robotique", "amdec", "apqp", "ppap", "spc", "5s", "kaizen", "lean", 
    "lean manufacturing", "six sigma", "python", "sql", "vba", "excel"
]
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
liste_contrats = ["cdi", "cdd", "stage", "alternance", "intérim", "anapec"]

# Lecture du fichier contenant les villes marocaines
with open("villes_maroc.txt", "r", encoding="utf-8") as fichier_villes:
    villes = [ligne.strip() for ligne in fichier_villes if ligne.strip()]
villes.sort(key=len, reverse=True)

stats_pages = []      # Nombre d'offres par page et par mot-clé
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
session = requests.Session()
session.headers.update(headers)


# Collecte des liens
def collecter_toutes_les_offres_brutes():
    offres_collectees = []
    liens_visites = set()      # Evite les doublons
    
    print("DÉBUT DE LA COLLECTE DES LIENS ")
    for mot in mots_cles:
        premier_lien_precedent = None
        for page in range(1, 21):
            offre_page = 0
            url = f"https://www.dreamjob.ma/page/{page}/?s={mot}"
            print(f"Recherche : {mot} - page {page}")
            
            try: 
                response = session.get(url, timeout=15)
            except Exception as e: 
                print(f"Erreur de connexion à la page {page}: {e}")
                stats_pages.append({"Mot clé": mot, "Page": page, "Nombre d'offres": 0})
                continue

            if response.status_code != 200:
                print(f"Erreur, page {page} (Code: {response.status_code})")
                stats_pages.append({"Mot clé": mot, "Page": page, "Nombre d'offres": 0})
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.select("article.jeg_post")

            if len(articles) == 0:
                print(f"Plus d'offres pour '{mot}', arrêt à la page {page}")
                break

            premier_titre_tag = articles[0].select_one("h3.jeg_post_title a")
            premier_lien_actuel = premier_titre_tag.get("href", "") if premier_titre_tag is not None else None
            if premier_lien_actuel is not None and premier_lien_actuel == premier_lien_precedent:
                print(f"Page {page} identique à la précédente pour '{mot}', arrêt")
                break
            premier_lien_precedent = premier_lien_actuel

            for art in articles:
                titre_tag = art.select_one("h3.jeg_post_title a")
                if titre_tag is None:
                    continue

                titre = titre_tag.text.strip()
                lien = titre_tag.get("href", "")

                extrait_tag = art.select_one(".jeg_post_excerpt p")
                extrait = extrait_tag.text.strip() if extrait_tag is not None else ""

                texte_total = (titre + " " + extrait).lower()
                ville_trouvee = "Non spécifié"
                for v in villes:
                    if v.lower() in texte_total:
                        ville_trouvee = v
                        break

                resultat = re.search(r'^(.*?)\s+(recrute|cherche|ouvre)\b', titre, re.IGNORECASE)
                entreprise = resultat.group(1).strip() if resultat is not None else "Non spécifié"

                if lien != "" and lien not in liens_visites:
                    liens_visites.add(lien)
                    offres_collectees.append({  "titre": titre,
                                                "entreprise": entreprise,
                                                "ville_trouvee": ville_trouvee,
                                                "lien": lien  })
                                        
                offre_page += 1
                
            print(f"Page {page} - {mot} : {offre_page} offres")
            stats_pages.append({"Mot clé": mot, "Page": page, "Nombre d'offres": offre_page})
            time.sleep(0.5)                                              #Pause entre chaque page pour éviter d'être bloqué par le site
            
    return offres_collectees


# Analyse en parallele
def analyser_details_une_offre(offre_brute):
    titre = offre_brute["titre"]
    entreprise = offre_brute["entreprise"]
    ville_trouvee = offre_brute["ville_trouvee"]
    lien = offre_brute["lien"]
    
    langue = "Non specifié"
    contrat = "Non spécifié"
    niveau_etude = "Non spécifié"
    experience = "Non spécifié"
    secteur = "Non spécifié"
    competences_techniques = "Non spécifié"
    soft_skills = "Non spécifié"

    try:
        resp_offre = session.get(lien, timeout=15)
        
        if resp_offre.status_code == 200:
            soup_offre = BeautifulSoup(resp_offre.text, "html.parser")
            contenu_offre = soup_offre.select_one(".entry-content")
            
            if contenu_offre is not None:
                texte_offre = contenu_offre.text.lower()
                texte_recherche_complet = (titre + " " + contenu_offre.text).lower()
                
                # Langues
                langues = []
                for l in ["français", "francais", "anglais", "english", "arabe"]:
                    if l in texte_offre:
                        langues.append(l.capitalize())
                langue = ", ".join(langues) if langues else "Non spécifié"
                
                # Contrat proposé
                for c in liste_contrats:
                    if c in texte_offre:
                        if c in ("cdi", "cdd"):
                            contrat = c.upper()
                        else:
                            contrat = c.capitalize()
                        break
                
                # Niveau d'étude
                match_etude = re.findall(r'bac\s*\+\s*\d+', texte_offre)
                if match_etude:
                    niveau_etude = ", ".join(
                            sorted(set(e.replace(" ", "") for e in match_etude))).capitalize()
                
                # Expérience
                match_exp = re.search(r'(\d+\s*(?:à|-)\s*\d+\s*ans|\d+\s*ans|\d+\s*an)', texte_offre)
                if match_exp is not None:
                    experience = match_exp.group(1) 
                
                # Secteur d'activité
                secteurs_trouves = []
                for sec in liste_secteurs:
                    if re.search(r'\b' + re.escape(sec) + r'\b', texte_recherche_complet):
                        formatted_sec = sec.replace(" d\\'", " d'").capitalize()
                        secteurs_trouves.append(formatted_sec)
                if secteurs_trouves:
                    secteur = ", ".join(sorted(list(set(secteurs_trouves))))

                # Compétences Techniques
                ct_trouvees = []
                for comp in liste_competences:
                    if re.search(r'\b' + re.escape(comp) + r'\b', texte_recherche_complet):
                        if comp in ["solidworks", "catia", "nx", "ansys", 
                                    "matlab", "simulink", "abaqus", "samcef", "nastran", "icem", 
                                    "cfd", "fea", "rdm", "cao", "dao", 
                                    "gmao", "sap", "erp", "amdec", "apqp", 
                                    "ppap", "spc", "5s", "sql", "vba"]:   
                            ct_trouvees.append(comp.upper())
                        else:
                            ct_trouvees.append(comp.capitalize())
                if ct_trouvees:       
                    competences_techniques = ", ".join(sorted(list(set(ct_trouvees)))) 

                # Soft Skills
                ss_trouves = []
                for skill in liste_soft_skills:
                    if re.search(r'\b' + re.escape(skill) + r'\b', texte_recherche_complet):
                        formatted_skill = skill.replace(" d\'", " d'").replace("communiquer", "communication").capitalize()
                        ss_trouves.append(formatted_skill)
                if ss_trouves:
                    soft_skills = ", ".join(sorted(list(set(ss_trouves)))) 

    except Exception as e:
        print(f"Erreur lors du traitement de l'URL {lien}: {e}")

   
    return {
        "Titre du poste": titre, 
        "Entreprise": entreprise, 
        "Ville": ville_trouvee, 
        "Secteur d'activité": secteur,
        "Contrat proposé": contrat, 
        "Niveau d'étude": niveau_etude, 
        "Expérience": experience,  
        "Compétences techniques": competences_techniques, 
        "Langues": langue,
        "Soft skills": soft_skills, 
        "Lien de l'offre": lien
    }

def scraper_dreamjob():
   
    # Recuperation des offres
    offres_a_scrapper = collecter_toutes_les_offres_brutes()
    print(f"\n Collecte terminée. {len(offres_a_scrapper)} pages d'offres uniques prêtes à être analysées.")
    
    # Lancement de l'analyse parallele
    print("\nDÉBUT DE L'ANALYSE  EN PARALLÈLE")
    with ThreadPoolExecutor(max_workers=12) as executor:
        resultats = executor.map(analyser_details_une_offre, offres_a_scrapper)
    
    # Collecte des résultats
    liste_offres = list(resultats)

    # Exportation des résultats sous forme de fichier csv
    if len(liste_offres) > 0:
        df_dreamjob = pd.DataFrame(liste_offres)
        df_dreamjob.to_csv("offres_dreamjob_mecanique.csv", index=False, sep=",", encoding="utf-8-sig")
        print(f"Total : {len(df_dreamjob)} offres.")
        return df_dreamjob
    else:
        print("Aucune offre n'a été trouvée.")
        return pd.DataFrame()

if __name__ == "__main__":
    scraper_dreamjob()
