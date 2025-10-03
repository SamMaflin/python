from bs4 import BeautifulSoup 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options  
import os, re, unicodedata, logging, random, time, io, pandas as pd, requests
from difflib import SequenceMatcher
from typing import Optional, Tuple, List, Dict
from bs4 import BeautifulSoup, Comment
from rapidfuzz import process, fuzz 

# --------------------
# Logging & Headers
# --------------------
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/121.0.0.0 Safari/537.36"),
    "Accept-Language": "en-GB,en;q=0.9",
    "Referer": "https://www.transfermarkt.co.uk/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive"
}

SOCCERWIKI_URL = "https://en.soccerwiki.org/download-data.php"


# --------------------
# Utility Functions
# --------------------
def fetch_url(session: requests.Session, url: str, retries: int = 3, timeout: int = 20) -> Optional[str]:
    """Fetch a URL with retries and backoff."""
    for attempt in range(1, retries + 1):
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logging.warning(f"Attempt {attempt} failed for {url}: {e}")
            if attempt < retries:
                time.sleep(random.uniform(5, 7))
            else:
                logging.error(f"Failed to fetch {url} after {retries} attempts.")
                return None


def clean_name(name: str) -> str:
    """Normalize and clean names for matching."""
    if not isinstance(name, str):
        return ""
    name = name.lower()
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("utf-8")
    name = re.sub(r"[^a-z0-9 ]", " ", name.replace("-", " ").replace("_", " "))
    return re.sub(r"\s+", " ", name).strip()


def fuzzy_match(name: str, candidates: List[str]) -> Tuple[Optional[str], float]:
    """Find closest candidate using SequenceMatcher."""
    best_match, best_score = None, 0.0
    for candidate in candidates:
        score = SequenceMatcher(None, name, candidate).ratio()
        if score > best_score:
            best_match, best_score = candidate, score
    return best_match, best_score



def get_soccerwiki_data() -> Dict:
    """Fetch full SoccerWiki dataset (players, clubs, managers, leagues, etc.)."""
    payload = {
        "format": "0",  # JSON
        "options[]": ["PlayerData", "ClubData", "ManagerData", "LeagueData"]
    }
    response = requests.post(SOCCERWIKI_URL, data=payload)
    response.raise_for_status()
    data = response.json()


    # Print LeagueData safely
    if "LeagueData" in data:
        print("\n📊 LeagueData Preview:")
        if isinstance(data["LeagueData"], list):
            # If it's a list of leagues
            for league in data["LeagueData"][:99999]:  # print first 5 leagues
                print(league)
        else:
            # If it's a dict
            for k, v in list(data["LeagueData"].items())[:99999]:
                print(f"{k}: {v}")
    else:
        print("⚠️ No LeagueData found in JSON.")

    return data


def get_clubs(league_mapping: Dict) -> pd.DataFrame:
    """Scrape Transfermarkt clubs and match with SoccerWiki club data."""
    session = requests.Session()
    session.headers.update(HEADERS)

    sw_data = get_soccerwiki_data()
    club_data = sw_data.get("ClubData", [])
    sw_df = pd.DataFrame(club_data)

    if not sw_df.empty and "Name" in sw_df.columns:
        sw_df["NameNorm"] = sw_df["Name"].apply(clean_name)
        sw_candidates = sw_df["NameNorm"].tolist()
    else:
        sw_candidates = []

    all_leagues = []
    club_counter = 1

    for league_name, info in league_mapping.items():
        url = info['transfermrkt_url']
        logging.info(f"[LEAGUE] Fetching clubs for {league_name}...")
        html = fetch_url(session, url)
        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", {"class": "items"})
        if not table:
            logging.warning(f"No clubs table found for {league_name}")
            continue

        rows = table.find_all("tr", {"class": ["odd", "even"]})
        tm_clubs = []

        for row in rows:
            link_tag = row.find("td", {"class": "hauptlink"}).find("a", href=True)
            if not link_tag:
                continue
            club_url = "https://www.transfermarkt.co.uk" + link_tag['href']
            team_name = re.search(r"transfermarkt\.co\.uk/([^/]+)/", club_url).group(1)
            tm_clubs.append({
                "league": league_name,
                "league_id": info['league_id'],
                "club_url": club_url,
                "club_id": club_counter,
                "NameNorm_tm": clean_name(team_name)
            })
            club_counter += 1

        tm_df = pd.DataFrame(tm_clubs)

        if sw_candidates:
            tm_df["SoccerWikiMatch"], tm_df["MatchConfidence"] = zip(
                *tm_df["NameNorm_tm"].apply(lambda n: fuzzy_match(n, sw_candidates))
            )
            merged_df = tm_df.merge(
                sw_df[["NameNorm", "Name", "ImageURL"]],
                left_on="SoccerWikiMatch", right_on="NameNorm",
                how="left"
            )
        else:
            merged_df = tm_df
            merged_df["Name"] = None
            merged_df["ImageURL"] = None

        # Keep only the requested final fields
        merged_df = merged_df[["league", "league_id", "club_url", "club_id", "Name", "ImageURL"]]

        all_leagues.append(merged_df)
        time.sleep(random.uniform(5, 7))

    final_df = pd.concat(all_leagues, ignore_index=True)
    os.makedirs("scrapers/data", exist_ok=True)
    final_df.to_csv("scrapers/data/clubs.csv", index=False, encoding="utf-8")
    logging.info("Saved all clubs to clubs.csv")
    return final_df


# --------------------
# Player Scraper
# --------------------
def get_players(clubs_df: pd.DataFrame) -> pd.DataFrame:
    """Scrape players from Transfermarkt and match with SoccerWiki player data."""
    session = requests.Session()
    session.headers.update(HEADERS)

    # Fetch SoccerWiki data
    sw_data = get_soccerwiki_data()
    player_data = sw_data.get("PlayerData", [])
    sw_df = pd.DataFrame(player_data)

    # Build candidate mapping
    name_to_indices, candidates = {}, []
    if not sw_df.empty:
        for idx, row in sw_df.iterrows():
            variants = []

            forename = (row.get("Forename") or "").strip()
            surname = (row.get("Surname") or "").strip()
            if forename and surname:
                variants.append(f"{forename} {surname}")
            if row.get("Name"):
                variants.append(row.get("Name").strip())
            if forename and not surname:
                variants.append(forename)
            if surname and not forename:
                variants.append(surname)
            for alt_key in ("ShortName", "CommonName", "DisplayName"):
                alt = (row.get(alt_key) or "").strip()
                if alt:
                    variants.append(alt)

            norm_variants = [clean_name(v) for v in variants if v]
            for nv in norm_variants:
                if nv not in name_to_indices:
                    name_to_indices[nv] = []
                    candidates.append(nv)
                name_to_indices[nv].append(idx)

    candidates = list(dict.fromkeys(candidates))

    # Known single-name player corrections
    NAME_CORRECTIONS = {
        "savinho": "moreira savinho",
        "rodri": "hernandez rodri",
        "murillo": "costa murillo",
        "alisson": "becker alisson",
        "morato": "felipe morato",
        "kevin": "kevin macedo",
        "rodrygo": "goes rodrygo",
        "casemiro": "carlos casemiro",
        "hannibal": "hannibal mejbri"
    }

    all_players = []
    logging.info("Fetching players for all clubs...")

    for _, club in clubs_df.iterrows():
        club_id, club_url, league_id = club["club_id"], club["club_url"], club["league_id"]
        club_name = club["Name"]
        logging.info(f"[PLAYER] Fetching players for club {club_id} — {club_name}")

        html = fetch_url(session, club_url)
        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select("table.items tbody > tr.odd, table.items tbody > tr.even")

        for row in rows:
            a_tag = row.select_one("td.posrela a[href*='/profil/spieler/']")
            if not a_tag:
                continue

            player_name = a_tag.get_text(strip=True)
            profile_url = "https://www.transfermarkt.co.uk" + a_tag["href"]
            position = row.select_one("td.posrela table.inline-table tr:nth-of-type(2) td")
            position = position.get_text(strip=True) if position else ""
            dob_age_td = row.select_one("td.zentriert:nth-of-type(3)")
            dob_age = dob_age_td.get_text(strip=True) if dob_age_td else ""
            flags = row.select("td.zentriert:nth-of-type(4) img.flaggenrahmen")
            nat = ", ".join([img["title"] for img in flags]) if flags else ""
            mv_td = row.select_one("td.rechts.hauptlink a")
            mv = mv_td.get_text(strip=True) if mv_td else ""
            number = row.select_one("td.rn_nummer").get_text(strip=True) if row.select_one("td.rn_nummer") else ""

            norm_name = clean_name(player_name)
            if norm_name in NAME_CORRECTIONS:
                norm_name = clean_name(NAME_CORRECTIONS[norm_name])

            match_candidate, score = fuzzy_match(norm_name, candidates) if candidates else (None, 0.0)
            sw_match, sw_id, sw_img = None, None, None
            if match_candidate:
                idx_list = name_to_indices.get(match_candidate, [])
                if idx_list:
                    sw_row = sw_df.loc[idx_list[0]]
                    sw_id = sw_row.get("ID") or sw_row.get("PlayerID")
                    sw_img = sw_row.get("ImageURL") or sw_row.get("PhotoURL")
                    sw_match = match_candidate

            all_players.append({
                "league_id": league_id,
                "club_id": club_id,
                "ClubName": club_name,
                "#": number,
                "PlayerName": player_name,
                "ProfileURL": profile_url,
                "Position": position,
                "DateOfBirth/Age": dob_age,
                "Nat.": nat,
                "MarketValue": mv, 
                "ImageURL": sw_img
            })

        time.sleep(random.uniform(5, 7))

    df = pd.DataFrame(all_players) 

    # --- Reset index and create player_id ---
    df = df.reset_index(drop=True)
    df.insert(0, "player_id", df.index + 1)  # player_id starts at 1
    df["dob_year"] = (
    df["DateOfBirth/Age"]
        .str.extract(r'(\d{4})')   # extract the 4-digit year
        .astype(float)             # convert to number, handles NaN if missing
        .astype("Int64")           # keep as nullable integer (instead of float)
    )
    df["temp_id"] = df["dob_year"].astype(str) + df["PlayerName"].str.replace(r"\s+", "", regex=True).str.lower()

    os.makedirs("scrapers/data", exist_ok=True)
    df.to_csv("scrapers/data/players.csv", index=False, encoding="utf-8")
    logging.info("Saved all players to players.csv")
    return df

 

# --- Selenium helper ---
def get_html_selenium(url, headless=True, timeout=15):
    """Fetch rendered HTML from a URL using Selenium."""
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    try:
        driver.set_page_load_timeout(timeout)
        driver.get(url)
        driver.implicitly_wait(2)
        return driver.page_source
    finally:
        driver.quit()


# --- DataFrame utilities ---
def flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Flatten MultiIndex columns into single strings."""
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [
            " ".join([str(c).strip() for c in col if str(c).strip() and str(c) != "nan"]).strip()
            for col in df.columns.values
        ]
    else:
        df.columns = [str(c).strip() for c in df.columns]
    return df


def remove_first_row_if_header(df: pd.DataFrame) -> pd.DataFrame:
    """Remove the first row if it duplicates column names (common on FBref)."""
    if all(str(df.iloc[0, i]).strip() == str(df.columns[i]).strip() for i in range(len(df.columns))):
        df = df.iloc[1:].reset_index(drop=True)
    return df


# --- Keeper table extractor (last table) ---
def extract_keeper_table_from_html(html):
    """
    Extract the last table from FBref HTML and remove repeated header row.
    """
    all_tables = pd.read_html(io.StringIO(html))
    if not all_tables:
        raise ValueError("No tables found in HTML.")
    
    df = all_tables[-1]  # always take last table
    df = flatten_columns(df)
    df = remove_first_row_if_header(df)
    return df

 
def clean_numeric(df, pct_cols):
    for col in df.columns:
        if col in pct_cols:
            df[col] = (
                df[col].astype(str)
                .str.replace("%", "", regex=False)
                .astype(float)
            )
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


# --- Main FBref scraper ---
def fbref_stats(
    league_mapping,
    season="2024-2025",
    output_csv=r"C:\Users\SMafl\python\scrapers\data\fbref_keeper_stats.csv"
):
    all_data = []

    # --- Scrape base URLs (current season) ---
    for league, info in league_mapping.items():
        url = info.get("fbref_url")
        if not url:
            print(f"[WARN] No fbref_url for {league}, skipping.")
            continue

        print(f"[INFO] Scraping {league} (base): {url}")
        try:
            html = get_html_selenium(url)
            df = extract_keeper_table_from_html(html)

            # Remove repeated headers
            first_col = df.columns[0] if df.columns.size > 0 else None
            if first_col:
                df = df[df[first_col] != first_col]

            df["league"] = league
            df["season"] = "current"
            all_data.append(df)
            print(f"  -> Collected {len(df)} rows.")
        except Exception as e:
            print(f"  -> Failed: {e}")
        time.sleep(5)

    # --- Scrape explicit season URLs ---
    for league, info in league_mapping.items():
        fbref_code = info.get("fbref league code")
        if not fbref_code:
            continue

        season_url = (
            info.get("season_url")
            or f"https://fbref.com/en/comps/{fbref_code}/{season}/keepersadv/{season}-{league.replace('_', '-').title()}-Stats"
        )

        print(f"[INFO] Scraping {league} ({season}): {season_url}")
        try:
            html = get_html_selenium(season_url)
            df = extract_keeper_table_from_html(html)

            # Remove repeated headers
            first_col = df.columns[0] if df.columns.size > 0 else None
            if first_col:
                df = df[df[first_col] != first_col]

            df["league"] = league
            df["season"] = season
            all_data.append(df)
            print(f"  -> Collected {len(df)} rows.")
        except Exception as e:
            print(f"  -> Failed: {e}")
        time.sleep(5)

    # --- Combine all data ---
    if not all_data:
        print("[WARN] No data collected, skipping save.")
        return

    final_df = pd.concat(all_data, ignore_index=True)

    # Build temp_id for fuzzy matching
    final_df["temp_id"] = (
        final_df["Unnamed: 6_level_0 Born"].astype(str).str.strip() + "_" +
        final_df["Unnamed: 1_level_0 Player"].str.replace(r"\s+", "", regex=True).str.lower()
    )

    # Rename columns to readable names
    final_df.columns = [
        "Rk", "Player", "Nation", "Pos", "Squad", "Age", "Born", "90s",
        "Goals GA", "Goals PKA", "Goals FK", "Goals CK", "Goals OG",
        "Expected PSxG", "Expected PSxG/SoT", "Expected PSxG+/-", "Expected /90",
        "Launched Cmp", "Launched Att", "Launched Cmp%", "Passes Att (GK)",
        "Passes Thr", "Passes Launch%", "Passes AvgLen", "Goal Kicks Att",
        "Goal Kicks Launch%", "Goal Kicks AvgLen", "Crosses Opp", "Crosses Stp",
        "Crosses Stp%", "Sweeper #OPA", "Sweeper #OPA/90", "Sweeper AvgDist",
        "Matches", "league", "season", "temp_id"
    ]

    # Columns for numeric aggregation
    columns_to_analyze = [
        "90s", "Goals GA", "Goals PKA", "Goals FK", "Goals CK", "Goals OG",
        "Expected PSxG", "Expected PSxG/SoT", "Expected PSxG+/-", "Expected /90",
        "Launched Cmp", "Launched Att", "Launched Cmp%", "Passes Att (GK)",
        "Passes Thr", "Passes Launch%", "Passes AvgLen", "Goal Kicks Att",
        "Goal Kicks Launch%", "Goal Kicks AvgLen", "Crosses Opp", "Crosses Stp",
        "Crosses Stp%", "Sweeper #OPA", "Sweeper #OPA/90", "Sweeper AvgDist"
    ]

    # --- Load players.csv and fuzzy match ---
    try:
        players_df = pd.read_csv("scrapers/data/players.csv")
        if "temp_id" not in players_df.columns:
            print("[WARN] players.csv missing temp_id column, skipping merge.")
            return

        def get_closest_player_id(temp_id):
            match, score, idx = process.extractOne(
                temp_id, players_df["temp_id"], scorer=fuzz.ratio
            )
            if score >= 80:
                return players_df.loc[idx, "player_id"]
            return None

        final_df["player_id"] = final_df["temp_id"].apply(get_closest_player_id)
        final_df = final_df[final_df["player_id"].notna()].copy()
        print(f"[INFO] Kept {len(final_df)} rows with matched player_id")

        # --- Aggregation step ---
        analysis_df = final_df[["player_id"] + columns_to_analyze].copy()

        pct_cols = [col for col in columns_to_analyze if "%" in col]
        non_pct_cols = [col for col in columns_to_analyze if col not in pct_cols]

        analysis_df = clean_numeric(analysis_df, pct_cols)

        grouped = analysis_df.groupby("player_id").agg(
            {**{col: "sum" for col in non_pct_cols},
             **{col: "mean" for col in pct_cols}}
        )

        # Round % and averages
        grouped[pct_cols] = grouped[pct_cols].round(2)
        # --- Keep metadata (first appearance) ---
        metadata_cols = [c for c in final_df.columns if c not in columns_to_analyze + ["player_id"]]
        metadata = final_df.groupby("player_id")[metadata_cols].first()
        # --- Join metadata + aggregated stats (both indexed by player_id) ---
        keeper_fbref = metadata.join(grouped, how="inner")
        # --- Reset index safely --- 
        keeper_fbref = keeper_fbref[["player_id", "Player", "90s", "Goals GA", "Goals PKA", "Goals FK", "Goals CK", "Goals OG", 
                                     "Expected PSxG", "Expected PSxG/SoT", "Expected PSxG+/-", "Expected /90", "Launched Cmp", 
                                     "Launched Att", "Passes Att (GK)", "Passes Thr", "Passes AvgLen", "Goal Kicks Att", "Goal Kicks AvgLen", 
                                     "Crosses Opp", "Crosses Stp", "Sweeper #OPA", "Sweeper #OPA/90", "Sweeper AvgDist", "Launched Cmp%", 
                                     "Passes Launch%", "Goal Kicks Launch%", "Crosses Stp%"]].reset_index()
        # --- Save result ---
        keeper_fbref.to_csv(output_csv, index=False)
        print(f"[INFO] Saved aggregated data with metadata to {output_csv}")

    except FileNotFoundError:
        print("[WARN] players.csv not found, skipping merge.")