import cloudscraper
import pandas as pd
from bs4 import BeautifulSoup
import time
import re

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
def scraper_rekrute():
    scraper = cloudscraper.create_scraper()                           #contourner code 403
    liste_offres = []
    for mot in mots_cles:
        for page in range(1, 5):     
            print("Recherche :", mot, "- page", page)                                         
            url = f"https://www.rekrute.com/fr/offres.html?s=1&p={page}&o=1&query={mot}&keyword={mot}&st=d&jobLocation=RK"
            try:
                response = scraper.get(url, timeout=15)                        #envoie des requetes au site
            except Exception as e:
                print("Erreur lors du scraping de la page", page, ":", e)
                continue

            if response.status_code != 200:
                print("Erreur de connexion sur la page", page, "(Code:", response.status_code, ")")
                continue

            soup = BeautifulSoup(response.text, "html.parser")                     
            offres_html = soup.select("li.post-id")                                #extraxtion du texte de la balise li classe postid
            compteur_page = 0

            for offre_html in offres_html:                                         # extraction du titre et du lien de chaque offre

                titre_tag = offre_html.select_one("a.titreJob")
                if titre_tag is None:
                    continue
                                                                        
                titre_complet = titre_tag.text.strip()                           
                lien = titre_tag.get("href", "")

                lien_complet = "https://www.rekrute.com" + lien
                try:
                    response = scraper.get(lien_complet, timeout=15)                        #envoie des requetes au site
                except Exception as e:
                    print("Erreur lors du scraping de la page", page, ":", e)
                    continue

                if response.status_code != 200:
                    continue
                                                                                    #requetes pour parcouri chaque offre(page detaillee)
                soup = BeautifulSoup(response.text, "html.parser")
                texte = soup.get_text(" ", strip=True).lower() 
                                                                                                #extraction des titres et des villes 
                if "|" in titre_complet:
                    morceaux = titre_complet.split("|")
                    titre = morceaux[0].strip()
                    ville = morceaux[1].strip()
                    ville = re.sub(r"\s*\(.*?\)", "", ville)   
                    ville = ville.strip() 
                else:
                    titre = titre_complet
                    ville = ""
                                                                                        
                img_tag = offre_html.select_one(".col-sm-2 img.photo")                            #extraction du nom de l entreprise via son logo
                if img_tag is not None:
                    entreprise = img_tag.get("title", "Confidentiel")  
                else:
                    entreprise = "Confidentiel"

                                                                        #extraction des langues requises
                langues = []
                for l in ["français", "francais", "anglais", "english", "arabe"]:                    
                    if l in texte:
                        langues.append(l.capitalize())
                langue = ", ".join(langues) if langues else "Non spécifié"
        
                competences = []
                for c in liste_competences:
                    if c in texte:
                        if c in ["solidworks", "catia", "nx", "ansys", 
                                "matlab", "samcef", "nastran", "icem", 
                                "cfd", "fea", "rdm", "cao", "dao", 
                                "gmao", "sap", "erp", "amdec", "apqp", 
                                "ppap", "spc", "5s", "sql", "vba"]: 
                            competences.append(c.upper())
                        else:
                            competences.append(c.capitalize())
                competence = ", ".join(competences) if competences else "Non spécifié"  
                
                soft_skills = []
                for s in liste_soft_skills:
                    if s in texte:
                        soft_skills.append(s.capitalize())
                soft_skill = ", ".join(soft_skills) if soft_skills else "Non spécifié"  
                            
                contrat = "Non spécifié"
                niveau_etude = "Non spécifié"                                                     #initialisation et extraction de ces 3 colonnes par la balise ul.featureInfo li
                experience = "Non spécifié"
                secteur = "Non spécifié"

                for li in offre_html.select("div.info li"):
                    texte = li.get_text(" ", strip=True)

                    if "Expérience requise" in texte:
                        a = li.find("a")
                        experience = a.get_text(strip=True) if a else texte.replace("Expérience requise :", "").strip()

                    elif "Niveau d'étude demandé" in texte:
                        a = li.find("a")
                        niveau_etude = a.get_text(strip=True) if a else texte.replace("Niveau d'étude demandé :", "").strip()

                    elif "Type de contrat" in texte:
                        a = li.find("a")
                        contrat = a.get_text(strip=True) if a else texte.replace("Type de contrat :", "").strip()

                    elif "Secteur d'activité" in texte:
                        a = li.find("a")
                        secteur = a.get_text(strip=True) if a else texte.replace("Secteur d'activité :", "").strip()
                        secteur = secteur.replace(" / ", ", ")
                            
        #stockage des informations dans un dic
                offre = {
                        "Titre du poste": titre,
                        "Entreprise": entreprise,
                        "Ville": ville,
                        "Secteur d'activité" : secteur,
                        "Contrat proposé": contrat,  
                        "Niveau d'étude": niveau_etude,
                        "Expérience": experience, 
                        "Compétences techniques": competence,
                        "Langues": langue,
                        "Soft skills": soft_skill,
                        "Lien de l'offre": lien_complet
                    }
        #trasnfert dans une liste
                liste_offres.append(offre)
                compteur_page += 1
            print("Page", page, "-", mot, ":", compteur_page, "offres")
        time.sleep(0.5)

    if len(liste_offres) > 0:
        df_rekrute = pd.DataFrame(liste_offres)
        df_rekrute.drop_duplicates(subset="Lien de l'offre", inplace=True)
        df_rekrute.to_csv("offres_rekrute_mecanique.csv", index=False, sep=",", encoding="utf-8-sig")
        print(" Total :", len(df_rekrute), "offres")
        return df_rekrute
    else:
        print("Aucune offre")
        return pd.DataFrame()
    
if __name__ == "__main__":
    scraper_rekrute()