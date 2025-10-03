from scrapers.scraper import get_clubs, get_players, fbref_stats 
import pandas as pd
# set display options
pd.set_option("display.max_columns", 99999)
pd.set_option("display.width", 99999)
pd.set_option("display.max_colwidth", 99999) 
 

league_mapping = {
        "premier_league": {"league_id": 1, "transfermrkt_url": "https://www.transfermarkt.co.uk/premier-league/startseite/wettbewerb/GB1", "soccerwiki": "Premier League", "country_code": "ENG", "fbref league code": "9", "fbref_url": "https://fbref.com/en/comps/9/keepersadv/Premier-League-Stats"},
        #"ligue_1": {"league_id": 11, "transfermrkt_url": "https://www.transfermarkt.co.uk/ligue-1/startseite/wettbewerb/FR1", "soccerwiki": "Ligue 1", "country_code": "FRA", "fbref league code": "13", "fbref_url": "https://fbref.com/en/comps/13/keepersadv/Ligue-1-Stats"},
        #"championship": {"league_id": 2, "transfermrkt_url": "https://www.transfermarkt.co.uk/premier-league/startseite/wettbewerb/GB2", "soccerwiki": "Championship", "country_code": "ENG", "fbref league code": "10", "fbref_url": "https://fbref.com/en/comps/10/keepersadv/Championship-Stats"},
        #"eredivisie": {"league_id": 3, "transfermrkt_url": "https://www.transfermarkt.co.uk/eredivisie/startseite/wettbewerb/NL1", "soccerwiki": "Eredivisie", "country_code": "NED", "fbref league code": "23", "fbref_url": "https://fbref.com/en/comps/23/keepersadv/Eredivisie-Stats"},
        #"liga_portgual": {"league_id": 4, "transfermrkt_url": "https://www.transfermarkt.co.uk/liga-portugal/startseite/wettbewerb/PO1", "soccerwiki": "Primeira Liga", "country_code": "POR", "fbref league code": "32", "fbref_url": "https://fbref.com/en/comps/32/keepersadv/Liga-Portuguesa-Stats"},
        #"süper_lig": {"league_id": 5, "transfermrkt_url": "https://www.transfermarkt.co.uk/super-lig/startseite/wettbewerb/TR1", "soccerwiki": "Süper Lig", "country_code": "TUR", "fbref league code": "23", "fbref_url": "https://fbref.com/en/comps/23/keepersadv/Super-Lig-Stats"},
        #"mls": {"league_id": 6, "transfermrkt_url": "https://www.transfermarkt.co.uk/major-league-soccer/startseite/wettbewerb/MLS1", "soccerwiki": "Major League Soccer", "country_code": "USA", "fbref league code": "22", "fbref_url": "https://fbref.com/en/comps/22/keepersadv/Major-League-Soccer-Stats"},
        #"la_liga": {"league_id": 8, "transfermrkt_url": "https://www.transfermarkt.co.uk/la-liga/startseite/wettbewerb/ES1", "soccerwiki": "La Liga", "country_code": "ESP", "fbref league code": "12", "fbref_url": "https://fbref.com/en/comps/12/keepersadv/La-Liga-Stats"},
        #"serie_a": {"league_id": 9, "transfermrkt_url": "https://www.transfermarkt.co.uk/serie-a/startseite/wettbewerb/IT1", "soccerwiki": "Serie A", "country_code": "ITA", "fbref league code": "11", "fbref_url": "https://fbref.com/en/comps/11/keepersadv/Serie-A-Stats"},
        #"bundesliga": {"league_id": 10, "transfermrkt_url": "https://www.transfermarkt.co.uk/bundesliga/startseite/wettbewerb/L1", "soccerwiki": "Bundesliga", "country_code": "GER", "fbref league code": "20", "fbref_url": "https://fbref.com/en/comps/20/keepersadv/Bundesliga-Stats"},
        #"jupiter_league": {"league_id": 12, "transfermrkt_url": "https://www.transfermarkt.co.uk/jupiler-pro-league/startseite/wettbewerb/BE1", "soccerwiki": "Pro League", "country_code": "BEL", "fbref league code": "37", "fbref_url": "https://fbref.com/en/comps/37/keepersadv/Pro-League-Stats"},
        #"campeonato_brasileiro": {"league_id": 13, "transfermrkt_url": "https://www.transfermarkt.co.uk/campeonato-brasileiro-serie-a/startseite/wettbewerb/BRA1", "soccerwiki": "Brasileirão Série A", "country_code": "BRA", "fbref league code": "24", "fbref_url": "https://fbref.com/en/comps/24/keepersadv/Campeonato-Brasileiro-Stats"}
    }

# Scrape clubs
#print("[INFO] Scraping clubs...")
#clubs = get_clubs(league_mapping)
#print(f"[DONE] {len(clubs)} clubs scraped!") 

# Scrape players
#print("[INFO] Scraping players...")
#players = get_players(clubs)
#print(f"[DONE] {len(players)} players scraped!")

#fbref_stats(league_mapping, season="2024-2025", output_csv="scrapers/data/fbref_keeper_stats.csv")

from sqlalchemy import create_engine
# from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Construct the SQLAlchemy connection string
DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)
# If using Transaction Pooler or Session Pooler, we want to ensure we disable SQLAlchemy client side pooling -
# https://docs.sqlalchemy.org/en/20/core/pooling.html#switching-pool-implementations
# engine = create_engine(DATABASE_URL, poolclass=NullPool)

# Test the connection
try:
    with engine.connect() as connection:
        print("Connection successful!")
except Exception as e:
    print(f"Failed to connect: {e}")