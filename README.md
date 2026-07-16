# Mechanical Engineering Job Market Analysis

This project was developed during an observation internship at the High Commission for Planning (HCP), Morocco.

## Overview

The objective of this project is to collect, clean, store, and analyze mechanical engineering job offers in Morocco from multiple recruitment websites. An interactive bilingual (French/English) Streamlit application was developed to explore the collected data.

## Features

- Web scraping from:
  - Rekrute
  - Emploi.ma
  - DreamJob
- Data cleaning and standardization
- SQLite database generation
- Automatic English translation of the database
- Interactive dashboard built with Streamlit
- Dynamic filtering and data visualization using Plotly
- Bilingual user interface (French / English)

## Project Structure

- `main.py` – Executes the complete data pipeline.
- `scraper_rekrute.py` – Scrapes Rekrute.
- `scraper_emploi.py` – Extracts data from Emploi.ma.
- `scraper_dreamjob.py` – Scrapes DreamJob.
- `merge_cleaning.py` – Merges and cleans the collected data.
- `translation.py` – Generates the English version of the database.
- `export_sql.py` – Exports the cleaned dataset to SQLite.
- `app_DSIS/` – Streamlit application.

## Technologies

- Python
- Requests
- Cloudscraper
- BeautifulSoup
- Pandas
- SQLite
- Streamlit
- Plotly

## Installation

Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

Run the complete pipeline:

```bash
python main.py
```

Then launch the Streamlit application:

```bash
streamlit run app_DSIS/1_Accueil.py
```

## Author

Othmane El Alaoui

Observation Internship Project  
High Commission for Planning (HCP) – Morocco