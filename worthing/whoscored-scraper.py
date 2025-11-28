#!/usr/bin/env python3
"""
WhoScored league-season scraper + Hybrid JSON Loader (Option B, fixed)

This version:

1. Scrapes all match links for a league-season
2. Inserts match links into match_links
3. Selects FIRST match
4. Scrapes matchCentreData JSON
5. Saves JSON structure to ./match_structure_<match_id>.txt
6. Inserts JSON and extracted entities into the Hybrid Schema:
      - matches
      - teams
      - players
      - match_players
      - player_stats  (per-player stats)
      - events
      - event_qualifiers
      - formations
      - formation_positions
      - shot_zones
      - expanded_minutes

Aligned with your MySQL schema (no start_time column, safe JSON parsing).
"""

import re
import time
import json
import logging
from typing import Dict, Any, Optional, Set, List

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import mysql.connector
import inquirer


# ==============================
# Config
# ==============================
HEADLESS = True
SELENIUM_WAIT = 20
SCROLL_PAUSE = 0.8
CLICK_PAUSE = 1.0
MAX_STABLE_LOOP = 2

DB_CONFIG = dict(
    host="localhost",
    user="root",
    password="root",
    database="football",
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


# ==============================
# DB Helpers
# ==============================
def get_cursor():
    conn = mysql.connector.connect(**DB_CONFIG)
    return conn, conn.cursor(dictionary=True)


def ensure_match_links_schema(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS match_links (
            match_id BIGINT NOT NULL AUTO_INCREMENT,
            league_season_id INT NOT NULL,
            url VARCHAR(500) NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (match_id),
            UNIQUE KEY unique_league_season_url (league_season_id, url)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)


def fetch_incomplete_seasons(cursor):
    cursor.execute("""
        SELECT 
            lsl.league_season_id,
            l.league_name,
            s.season_code,
            s.season_name,
            lsl.url
        FROM league_season_links lsl
        JOIN leagues l ON lsl.league_id = l.league_id
        JOIN seasons s ON lsl.season_id = s.season_id
        WHERE lsl.complete = 0
    """)
    return cursor.fetchall()


# ==============================
# Selenium Setup
# ==============================
def make_driver():
    opts = Options()
    if HEADLESS:
        opts.add_argument("--headless")
    return webdriver.Firefox(options=opts)


# ==============================
# Link Scraping
# ==============================
def get_links_on_page(driver, wait) -> Set[str]:
    try:
        wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "a.Match-module_score__5Ghhj")
            )
        )
    except Exception:
        return set()

    links = set()
    for el in driver.find_elements(By.CSS_SELECTOR, "a.Match-module_score__5Ghhj"):
        try:
            href = el.get_attribute("href")
            if href:
                links.add(href)
        except Exception:
            pass
    return links


def find_chevron(driver):
    try:
        img = driver.find_element(By.XPATH, "//img[@alt='chevron-left']")
        return img.find_element(By.XPATH, "./ancestor::button|./ancestor::a")
    except Exception:
        return None


def scrape_whoscored_matches(url: str) -> Set[str]:
    driver = make_driver()
    wait = WebDriverWait(driver, SELENIUM_WAIT)

    logger.info(f"Opening: {url}")
    driver.get(url)
    time.sleep(1)

    collected = get_links_on_page(driver, wait)
    logger.info(f"Initial links: {len(collected)}")

    stable = 0
    while True:
        before = set(collected)
        chevron = find_chevron(driver)
        clicked = False

        if chevron:
            try:
                chevron.click()
            except Exception:
                driver.execute_script("arguments[0].click();", chevron)
            time.sleep(CLICK_PAUSE)
            collected |= get_links_on_page(driver, wait)
            clicked = True
        else:
            driver.execute_script("window.scrollBy(0,1200)")
            time.sleep(SCROLL_PAUSE)
            collected |= get_links_on_page(driver, wait)
            clicked = True

        if len(collected) == len(before):
            stable += 1
            if stable >= MAX_STABLE_LOOP:
                break
        else:
            stable = 0

    driver.quit()
    return collected


# ==============================
# Insert match links
# ==============================
def insert_new_links(cursor, conn, links, league_season_id):
    cursor.execute(
        "SELECT url FROM match_links WHERE league_season_id=%s",
        (league_season_id,)
    )
    existing = {r["url"] for r in cursor.fetchall()}

    new = [l for l in links if l not in existing]
    logger.info(f"Inserting {len(new)} new links")

    if new:
        cursor.executemany(
            "INSERT INTO match_links (league_season_id, url) VALUES (%s,%s)",
            [(league_season_id, l) for l in new]
        )
        conn.commit()

    return new


# ==============================
# JSON Scraper
# ==============================
def scrape_match_json(match_url: str) -> Optional[Dict[str, Any]]:
    driver = make_driver()
    driver.get(match_url)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    script = soup.select_one('script:-soup-contains("matchCentreData")')
    if not script:
        return None

    m = re.search(r"matchCentreData\s*:\s*(\{.*?\}),\n", script.text, re.DOTALL)
    if not m:
        return None

    return json.loads(m.group(1))


# ==============================
# JSON Structure Printer
# ==============================
def capture_structure(obj, indent=0):
    lines = []
    sp = " " * indent

    if isinstance(obj, dict):
        for k, v in obj.items():
            lines.append(f"{sp}{k} ({type(v).__name__})")
            if isinstance(v, (dict, list)):
                lines.extend(capture_structure(v, indent + 4))
    elif isinstance(obj, list) and obj:
        lines.append(f"{sp}[list:{len(obj)}]")
        lines.extend(capture_structure(obj[0], indent + 4))

    return lines


# ==============================
# Hybrid Schema Inserts
# ==============================

def _extract_start_datetime(data: Dict[str, Any]) -> Optional[str]:
    """
    Build a single 'YYYY-MM-DD HH:MM:SS' string for matches.start_date (DATETIME)
    from startTime or startDate in the JSON.
    """
    raw = data.get("startTime") or data.get("startDate")
    if not raw or "T" not in raw:
        return None
    date_part, time_part = raw.split("T", 1)
    # Ensure no extra junk
    time_part = time_part.strip()
    return f"{date_part} {time_part}"


def insert_match(cursor, conn, match_id, league_season_id, url, data):
    referee = data.get("referee", {}) or {}
    scores = data.get("scores", {}) or {}
    start_dt = _extract_start_datetime(data)

    sql = """
        INSERT INTO matches (
            match_id, league_season_id, match_url, json_data,
            attendance, venue, referee_name,
            start_date,
            home_team_id, away_team_id,
            halftime_score, fulltime_score
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
            json_data      = VALUES(json_data),
            attendance     = VALUES(attendance),
            venue          = VALUES(venue),
            referee_name   = VALUES(referee_name),
            start_date     = VALUES(start_date),
            home_team_id   = VALUES(home_team_id),
            away_team_id   = VALUES(away_team_id),
            halftime_score = VALUES(halftime_score),
            fulltime_score = VALUES(fulltime_score)
    """

    cursor.execute(sql, (
        match_id,
        league_season_id,
        url,
        json.dumps(data),
        data.get("attendance"),
        data.get("venueName"),
        referee.get("name"),
        start_dt,
        data.get("home", {}).get("teamId"),
        data.get("away", {}).get("teamId"),
        scores.get("halftime"),
        scores.get("fulltime"),
    ))
    conn.commit()


# --- Teams ---
def insert_teams(cursor, conn, data):
    for side in ["home", "away"]:
        t = data.get(side) or {}
        if not t:
            continue

        cursor.execute("""
            INSERT INTO teams (team_id, name, country)
            VALUES (%s,%s,%s)
            ON DUPLICATE KEY UPDATE name=VALUES(name), country=VALUES(country)
        """, (
            t.get("teamId"),
            t.get("name"),
            t.get("countryName"),
        ))
    conn.commit()


# --- Players & match_players ---
def insert_players(cursor, conn, match_id, data):
    for side in ["home", "away"]:
        team = data.get(side) or {}
        team_id = team.get("teamId")
        if team_id is None:
            continue

        for p in team.get("players", []):
            # Players table (basic info; many fields may be missing)
            cursor.execute("""
                INSERT INTO players (player_id, name, height, weight, age)
                VALUES (%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE name=VALUES(name)
            """, (
                p.get("playerId"),
                p.get("name"),
                p.get("height"),
                p.get("weight"),
                p.get("age"),
            ))

            # match_players row
            cursor.execute("""
                INSERT INTO match_players
                (match_id, team_id, player_id, shirt_no, position,
                 is_first_eleven, is_man_of_the_match, field)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                match_id,
                team_id,
                p.get("playerId"),
                p.get("shirtNo"),
                p.get("position") or p.get("positionName") or "Unknown",
                p.get("isFirstEleven", False),
                p.get("isManOfTheMatch", False),
                p.get("field"),
            ))
    conn.commit()


# --- Player Stats (per-player) ---
def insert_player_stats(cursor, conn, match_id, data):
    """
    Uses each player's own 'stats' dict, which looks like:
      stats -> {
         'ratings': { '0': 6.5, '15': 6.7, ... },
         'passesTotal': { '0': 3, '1': 5, ... },
         ...
      }
    We store:
        match_id, team_id, player_id, stat_category, minute_index, value
    """
    for side in ["home", "away"]:
        team = data.get(side) or {}
        team_id = team.get("teamId")
        if team_id is None:
            continue

        for p in team.get("players", []):
            player_id = p.get("playerId")
            stats = p.get("stats") or {}
            if not isinstance(stats, dict):
                continue

            for stat_cat, stat_dict in stats.items():
                if not isinstance(stat_dict, dict):
                    continue

                for minute_str, val in stat_dict.items():
                    try:
                        minute_index = int(minute_str)
                    except (TypeError, ValueError):
                        # skip weird keys
                        continue

                    try:
                        value = float(val)
                    except (TypeError, ValueError):
                        continue

                    cursor.execute("""
                        INSERT INTO player_stats
                        (match_id, team_id, player_id, stat_category, minute_index, value)
                        VALUES (%s,%s,%s,%s,%s,%s)
                    """, (
                        match_id,
                        team_id,
                        player_id,
                        stat_cat,
                        minute_index,
                        value,
                    ))
    conn.commit()


# --- Events ---
def insert_events(cursor, conn, match_id, data):
    for evt in data.get("events", []):
        period = evt.get("period") or {}
        etype = evt.get("type") or {}
        outcome = evt.get("outcomeType") or {}

        cursor.execute("""
            INSERT INTO events (
                match_id, event_id, minute, second, team_id, player_id,
                x, y, expanded_minute,
                period_value, period_name,
                type_value, type_name,
                outcome_value, outcome_name,
                is_touch
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            match_id,
            evt.get("eventId"),
            evt.get("minute"),
            evt.get("second"),
            evt.get("teamId"),
            evt.get("playerId"),
            evt.get("x"),
            evt.get("y"),
            evt.get("expandedMinute"),
            period.get("value"),
            period.get("displayName"),
            etype.get("value"),
            etype.get("displayName"),
            outcome.get("value"),
            outcome.get("displayName"),
            evt.get("isTouch"),
        ))

        row_id = cursor.lastrowid

        for q in evt.get("qualifiers", []):
            qtype = q.get("type") or {}
            cursor.execute("""
                INSERT INTO event_qualifiers
                (event_row_id, qualifier_type, qualifier_name, qualifier_value)
                VALUES (%s,%s,%s,%s)
            """, (
                row_id,
                qtype.get("value"),
                qtype.get("displayName"),
                q.get("value"),
            ))

    conn.commit()


# --- Formations ---
def insert_formations(cursor, conn, match_id, data):
    for side in ["home", "away"]:
        team = data.get(side) or {}
        team_id = team.get("teamId")
        if team_id is None:
            continue

        for f in team.get("formations", []):
            cursor.execute("""
                INSERT INTO formations
                (match_id, team_id, formation_id, formation_name,
                 captain_player_id, period, start_minute, end_minute)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                match_id,
                team_id,
                f.get("formationId"),
                f.get("formationName"),
                f.get("captainPlayerId"),
                f.get("period"),
                f.get("startMinuteExpanded"),
                f.get("endMinuteExpanded"),
            ))

            form_id = cursor.lastrowid

            for idx, pos in enumerate(f.get("formationPositions", [])):
                cursor.execute("""
                    INSERT INTO formation_positions
                    (formation_id, slot_index, vertical, horizontal)
                    VALUES (%s,%s,%s,%s)
                """, (
                    form_id,
                    idx,
                    pos.get("vertical"),
                    pos.get("horizontal"),
                ))

    conn.commit()


# --- Shot Zones ---
def insert_shot_zones(cursor, conn, match_id, data):
    for side in ["home", "away"]:
        team = data.get(side) or {}
        team_id = team.get("teamId")
        if team_id is None:
            continue

        zones = team.get("shotZones") or {}
        for zone_name, zdata in zones.items():
            stats = zdata.get("stats") or {}
            for pid, s in stats.items():
                cursor.execute("""
                    INSERT INTO shot_zones
                    (match_id, team_id, zone_name, player_id,
                     goal_count, shot_count)
                    VALUES (%s,%s,%s,%s,%s,%s)
                """, (
                    match_id,
                    team_id,
                    zone_name,
                    int(pid),
                    s.get("goalCount"),
                    s.get("count"),
                ))
    conn.commit()


# --- Expanded Minutes ---
def insert_expanded_minutes(cursor, conn, match_id, data):
    mins = data.get("expandedMinutes") or {}
    for period, minute_dict in mins.items():
        try:
            period_int = int(period)
        except (TypeError, ValueError):
            continue

        for m_index, val in minute_dict.items():
            try:
                mi_int = int(m_index)
            except (TypeError, ValueError):
                continue

            cursor.execute("""
                INSERT INTO expanded_minutes
                (match_id, period, minute_index, expanded_value)
                VALUES (%s,%s,%s,%s)
            """, (
                match_id,
                period_int,
                mi_int,
                val,
            ))
    conn.commit()


# ==============================
# Main
# ==============================
def main():
    conn, cursor = get_cursor()
    ensure_match_links_schema(cursor)
    conn.commit()

    # --------------------------------------------------
    # 1. Select league-season to scrape
    # --------------------------------------------------
    seasons = fetch_incomplete_seasons(cursor)
    if not seasons:
        print("No incomplete seasons.")
        return

    leagues: Dict[str, Dict[str, str]] = {}
    ids: Dict[tuple, int] = {}

    for r in seasons:
        leagues.setdefault(r["league_name"], {})[r["season_code"]] = r["url"]
        ids[(r["league_name"], r["season_code"])] = r["league_season_id"]

    league = inquirer.prompt([
        inquirer.List("lg", message="Select league", choices=list(leagues.keys()))
    ])["lg"]

    season = inquirer.prompt([
        inquirer.List(
            "ss",
            message=f"Select season for {league}",
            choices=list(leagues[league].keys())
        )
    ])["ss"]

    url = leagues[league][season]
    league_season_id = ids[(league, season)]

    # --------------------------------------------------
    # 2. Scrape all match links for that league-season
    # --------------------------------------------------
    print("\nScraping match links...")
    links = scrape_whoscored_matches(url)
    new_links = insert_new_links(cursor, conn, list(links), league_season_id)

    if not new_links:
        print("\nNo NEW match links found. Checking for unmatched JSON...")
    else:
        print(f"\nInserted {len(new_links)} NEW match links.")

    # --------------------------------------------------
    # 3. Fetch match links that STILL need JSON scraping
    # --------------------------------------------------
    cursor.execute("""
        SELECT ml.match_id, ml.url
        FROM match_links ml
        LEFT JOIN matches m ON m.match_id = ml.match_id
        WHERE ml.league_season_id = %s AND m.match_id IS NULL
        ORDER BY ml.match_id ASC
    """, (league_season_id,))
    pending = cursor.fetchall()

    if not pending:
        print("\nAll matches already scraped — no new matches to process.")
        return

    print(f"\nNeed to scrape JSON for {len(pending)} matches.\n")

    # --------------------------------------------------
    # 4. Scrape + Insert JSON for all remaining matches
    # --------------------------------------------------
    for row in pending:
        match_id = row["match_id"]
        match_url = row["url"]

        print(f"→ Scraping JSON for match_id={match_id} : {match_url}")

        data = scrape_match_json(match_url)
        if not data:
            print(f"!! JSON NOT FOUND for match_id={match_id} — skipping.\n")
            continue 

        # --------------------------------------------------
        # Insert all hybrid schema data
        # --------------------------------------------------
        try:
            insert_match(cursor, conn, match_id, league_season_id, match_url, data)
            insert_teams(cursor, conn, data)
            insert_players(cursor, conn, match_id, data)
            insert_player_stats(cursor, conn, match_id, data)
            insert_events(cursor, conn, match_id, data)
            insert_formations(cursor, conn, match_id, data)
            insert_shot_zones(cursor, conn, match_id, data)
            insert_expanded_minutes(cursor, conn, match_id, data)

            print(f"✓ Completed match_id={match_id}\n")

        except Exception as e:
            print(f"!! ERROR inserting match_id={match_id}: {e}\n")
            conn.rollback()
            continue

    print("\n=== ALL NEW MATCHES SUCCESSFULLY SCRAPED & INSERTED ===\n")

    cursor.close()
    conn.close()



if __name__ == "__main__":
    main()
