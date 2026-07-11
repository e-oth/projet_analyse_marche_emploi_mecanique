from scraper_dreamjob import scraper_dreamjob
from scraper_rekrute import scraper_rekrute
from scraper_emploi import scraper_emploi
from fusion_nettoyage import fusionner_csvs, nettoyer_donnees
from export_sql import exporter_sql


def main():
    print("Étape 1 : Scraping Dreamjob.ma")
    scraper_dreamjob()

    print("\n Étape 2 : Scraping Rekrute.com ")
    scraper_rekrute()

    print("\n Étape 3 : Extraction Emploi.ma ")

    input("Vérifie que 'outerhtml.txt' est à jour (page Emploi.ma sauvegardée), puis appuie sur Entrée")
    scraper_emploi()

    print("\n Étape 4 : Fusion des 3 sources")
    df = fusionner_csvs()

    print("\n Étape 5 : Nettoyage des données ")
    df = nettoyer_donnees(df)
    df.to_csv("ws_merged.csv", index=False, encoding="utf-8-sig")

    print("\n Étape 6 : Export vers SQLite ===")
    exporter_sql(df, "marche_emploi_mecanique.db")

    print(f"\nTerminé. {len(df)} offres au total dans la base finale.")


if __name__ == "__main__":
    main()