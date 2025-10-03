from pathlib import Path
from datetime import datetime
import pandas as pd
from soccerdata import WhoScored

def fetch_whoscored_raw_to_csv(
    league: str, 
    season: str, 
    event_dir: str, 
    data_dir: str = "whoscored/data/whoscored"
) -> pd.DataFrame:
    """
    Fetch raw WhoScored events for a league/season, combine all matches, and save as a single CSV.

    Args:
        league (str): League code, e.g., "ENG-Premier League"
        season (str): Season string, e.g., "2023"
        event_dir (str): Directory to save CSV
        data_dir (str): Directory to store WhoScored raw data

    Returns:
        pd.DataFrame: Combined raw events for all matches
    """
    # Ensure directories exist
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    event_dir = Path(event_dir)
    event_dir.mkdir(parents=True, exist_ok=True)

    # Initialize WhoScored object
    ws = WhoScored(leagues=[league], seasons=[season], data_dir=data_dir)
    
    # Read schedule
    df_schedule = ws.read_schedule()
    df_schedule['game_id'] = df_schedule['game_id'].astype(str)

    # Convert start_time to datetime to allow .dt accessor
    df_schedule['start_time'] = pd.to_datetime(df_schedule['start_time'], errors='coerce')

    # Only fetch past games
    today_date = datetime.now().date()
    df_past = df_schedule[df_schedule['start_time'].dt.date <= today_date]
    game_ids = df_past['game_id'].astype(int).tolist()
    print(f"📅 Fetching raw events for {len(game_ids)} games...")

    if not game_ids:
        print("⚠️ No past games to fetch.")
        return pd.DataFrame()

    # Fetch raw events for all games
    try:
        api = ws.read_events(match_id=game_ids, output_fmt="loader")
    except ValueError as e:
        if "No games found with the given IDs" in str(e):
            print(f"⚠️ No events found for these games: {game_ids}")
            return pd.DataFrame()
        else:
            raise

    # Combine events for all games
    df_events = pd.DataFrame()
    for gid in game_ids:
        try:
            game_events = api.events(gid)
            if not game_events.empty:
                df_events = pd.concat([df_events, game_events], ignore_index=True)
        except Exception as e:
            print(f"⚠️ Skipping game {gid} due to error: {e}")

    if df_events.empty:
        print("⚠️ No events found.")
        return pd.DataFrame()

    # Convert dict/list columns to strings to avoid CSV issues
    for col in df_events.columns:
        if df_events[col].dtype == "object":
            df_events[col] = df_events[col].apply(lambda x: str(x) if isinstance(x, (dict, list)) else x)

    # Remove duplicates
    df_events.drop_duplicates(inplace=True)

    # Save combined CSV
    event_file = event_dir / f"{league}_{season}_all_matches.csv"
    df_events.to_csv(event_file, index=False)
    print(f"✅ Saved combined raw events to {event_file} ({len(df_events)} rows).")

    return df_events


# -------------------------------------------------------------------
# Compute possessions from a saved CSV
# -------------------------------------------------------------------

### def define_possessions(league: str, season: str, event_dir: str, possession_dir: str, team: str):
###     # ---------------------------
###     # Load events
###     # ---------------------------
###     event_dir_path = Path(event_dir)
###     possession_dir_path = Path(possession_dir)
###     events_df = pd.read_csv(event_dir_path / f"{league}_{season}.csv")
### 
###     possession_rows = []
###     possession_id = 0
###     current_team = None
###     possession_start_types = {}  # Track the starting type of each possession
### 
###     # ---------------------------
###     # Possession start conditions
###     # ---------------------------
###     def starts_possession(idx, row):
###         # Exclude interceptions and tackles from starting possession
###         if row["type_name"] in [
###             "pass", "dribble", 
###             "throw_in", "goalkick", "freekick_short", "corner_short"
###         ] and row["result_name"] == "success":
###             return True
### 
###         if row["type_name"] == "clearance" and row["result_name"] == "success":
###             nxt = events_df.iloc[idx + 1] if idx + 1 < len(events_df) else None
###             if nxt is not None:
###                 if (
###                     nxt["period_id"] == row["period_id"] and
###                     nxt["type_name"] != "throw_in" and
###                     nxt["team_id"] == row["team_id"] and
###                     nxt["result_name"] == "success"
###                 ):
###                     return True
###         return False
### 
###     # ---------------------------
###     # Possession end conditions
###     # ---------------------------
### 
###     def ends_possession(idx, row):
###         # Clearance ends possession if opponent regains
###         if row["type_name"] == "clearance":
###             nxt = events_df.iloc[idx + 1] if idx + 1 < len(events_df) else None
###             if nxt is not None and nxt["period_id"] == row["period_id"]:
###                 if nxt["team_id"] != row["team_id"]:
###                     return True
### 
###         # Failed or offside forward actions
###         if row["type_name"] in [
###             "pass", "cross", "take_on", "dribble", "throw_in",
###             "corner_crossed", "freekick_crossed", "goalkick", "bad_touch"
###         ] and row["result_name"] in ["fail", "offside"]:
###             return True
### 
###         # Shots and fouls always end possession
###         if row["type_name"] in ["shot", "shot_freekick", "foul"]:
###             return True
### 
###         # Successful defensive actions end opponent possession
###         if row["type_name"] in ["tackle", "interception"] and row["result_name"] == "success":
###             return True
### 
###         return False
### 
###     # ---------------------------
###     # Main loop through events
###     # ---------------------------
###     for idx, row in events_df.iterrows():
###         if current_team is None:
###             if starts_possession(idx, row):
###                 possession_id += 1
###                 current_team = row["team_name"]
###                 possession_start_types[possession_id] = row["type_name"]
### 
###                 if not (row["type_name"] == "clearance" and row["result_name"] == "success"):
###                     possession_rows.append({**row.to_dict(),
###                                             "possession_id": possession_id,
###                                             "possession_team": current_team})
###         else:
###             if row["team_name"] == current_team:
###                 if ends_possession(idx, row):
###                     current_team = None
###                 else:
###                     possession_rows.append({**row.to_dict(),
###                                             "possession_id": possession_id,
###                                             "possession_team": current_team})
###             else:
###                 current_team = None
### 
###     # ---------------------------
###     # Build DataFrame
###     # ---------------------------
###     possessions_df = pd.DataFrame(possession_rows) 
### 
###     # ---------------------------
###     # Remove possessions that started with interception or tackle
###     # ---------------------------
###     bad_start_possessions = [pid for pid, start_type in possession_start_types.items()
###                              if start_type in ["interception", "tackle"]]
###     possessions_df = possessions_df[~possessions_df["possession_id"].isin(bad_start_possessions)]
### 
###     # ---------------------------
###     # Rule out purely defensive stubs
###     # ---------------------------
###     constructive_types = {
###         "pass", "dribble", "cross", "shot",
###         "corner_short", "corner_crossed",
###         "freekick_short", "freekick_crossed",
###         "throw_in", "goalkick", "take_on"
###     }
### 
###     valid_possessions = (
###         possessions_df.groupby("possession_id")["type_name"]
###         .unique().apply(set)
###         .loc[lambda s: s.apply(lambda x: len(x & constructive_types) > 0)]
###         .index
###     )
### 
###     possessions_df = possessions_df[possessions_df["possession_id"].isin(valid_possessions)]
### 
###     # ---------------------------
###     # Remove single-action throw-in possessions
###     # ---------------------------
###     pos_counts = possessions_df.groupby("possession_id").size()
###     single_throw_in_ids = (
###         possessions_df.loc[
###             (possessions_df["type_name"] == "throw_in") &
###             (possessions_df["possession_id"].isin(pos_counts[pos_counts == 1].index))
###         ]["possession_id"]
###     )
###     possessions_df = possessions_df[~possessions_df["possession_id"].isin(single_throw_in_ids)]
### 
###     # ---------------------------
###     # Remove events with no movement
###     # ---------------------------
###     possessions_df = possessions_df[~((possessions_df["start_x"] == possessions_df["end_x"]) &
###                                       (possessions_df["start_y"] == possessions_df["end_y"]))]
###     
###     possessions_df["season"] = season
###     possessions_df["league"] = league  # optional, but useful for later joins
### 
###     # ---------------------------
###     # Save output
###     # ---------------------------
###     possession_dir_path.mkdir(parents=True, exist_ok=True)
###     out_path = possession_dir_path / f"{league}_{season}.csv"
### 
###     possessions_df[
###         [
###             "game_id", "possession_id", "match_min", "period_id", "time_seconds",
###             "start_x", "end_x", "start_y", "end_y",
###             "type_name", "result_name", "bodypart_name",
###             "team_name", "player_name", "xT_value"
###         ]
###     ].to_csv(out_path, index=False)
### 
###     print(f"Saved {len(possessions_df)} events across {possessions_df['possession_id'].nunique()} possessions to {out_path}")
### 
###     # filter by team, use prop input in function
###     if team:
###         # find unique game_id for team_name == name
###         team_game_ids = possessions_df.loc[possessions_df['team_name'] == team, 'game_id'].unique()
###         possessions_df = possessions_df[possessions_df['game_id'].isin(team_game_ids)]
### 
###     return possessions_df
###  
### 
### 
### 
### 
### 
### def define_transitions(league: str, season: str, event_dir: str, transitions_dir: str, team=None):
###     import pandas as pd
###     from pathlib import Path
### 
###     # --- Paths setup ---
###     event_dir_path = Path(event_dir)
###     transitions_dir_path = Path(transitions_dir)
###     transitions_dir_path.mkdir(parents=True, exist_ok=True)
### 
###     # --- Load events ---
###     events_df = pd.read_csv(event_dir_path / f"{league}_{season}.csv")
### 
###     # --- Define rules ---
###     fail_actions = {"pass", "cross", "take_on", "bad_touch"}
###     failed_results = {"fail", "offside"}
###     end_events = {
###         "foul", "throw_in", "goalkick",
###         "corner_cross", "corner_short",
###         "freekick_crossed", "freekick_short",
###         "shot_freekick", "shot_penalty",
###         "keeper_save", "keeper_pick_up", "shot"
###     }
###     defense_actions = {"interception", "tackle"}
### 
###     # --- Assign transition IDs ---
###     transition_id = 1
###     transition_ids = []
### 
###     for idx in range(len(events_df)):
###         row = events_df.iloc[idx]
###         next_row = events_df.iloc[idx + 1] if idx < len(events_df) - 1 else None
### 
###         # Increment transition ID if possession change or end/defense event occurs
###         if (
###             (row["type_name"] in fail_actions and row["result_name"] in failed_results
###              and next_row is not None and row["team_id"] != next_row["team_id"])
###             or (row["type_name"] in end_events)
###             or (row["type_name"] == "clearance" and next_row is not None
###                 and row["team_id"] != next_row["team_id"] and next_row["type_name"] not in end_events)
###             or (row["type_name"] in defense_actions)
###         ):
###             transition_id += 1
### 
###         transition_ids.append(transition_id)
### 
###     events_df["transition_id"] = transition_ids
### 
###     # --- Remove "bad" transitions ---
###     # 1. Transitions starting with end_events
###     first_rows = events_df.groupby("transition_id").head(1)
###     bad_transitions = first_rows.loc[first_rows["type_name"].isin(end_events), "transition_id"]
### 
###     # 2. Clearance → next row corner
###     clearance_corner_transitions = []
###     for tid, group in events_df.groupby("transition_id"):
###         first_row = group.iloc[0]
###         next_idx = first_row.name + 1
###         if first_row["type_name"] == "clearance" and next_idx < len(events_df):
###             next_row = events_df.iloc[next_idx]
###             if "corner" in str(next_row["type_name"]).lower():
###                 clearance_corner_transitions.append(tid)
### 
###     # 3. Any row contains 'corner'
###     corner_transitions_anywhere = events_df.loc[
###         events_df["type_name"].str.contains("corner", case=False, na=False), "transition_id"
###     ].unique()
### 
###     all_bad_transitions = set(bad_transitions) | set(clearance_corner_transitions) | set(corner_transitions_anywhere)
### 
###     # Drop all bad transitions
###     events_df = events_df[~events_df["transition_id"].isin(all_bad_transitions)].reset_index(drop=True)
### 
###     # --- Cleanup ---
###     # Remove failed interceptions
###     events_df = events_df[~((events_df["type_name"] == "interception") & (events_df["result_name"] == "fail"))]
### 
###     # Remove transitions with only one row
###     events_df = events_df[events_df["transition_id"].map(events_df["transition_id"].value_counts()) > 1]
### 
###     # --- Compute transitioning_team safely within same game ---
###     transitioning_team = []
###     for idx in range(len(events_df)):
###         row = events_df.iloc[idx]
###         next_row = events_df.iloc[idx + 1] if idx < len(events_df) - 1 else None
### 
###         # Only consider next_row if same game_id
###         if next_row is not None and next_row["game_id"] != row["game_id"]:
###             next_row = None
### 
###         if row["type_name"] in {"clearance", "tackle"}:
###             if next_row is not None and row["team_name"] == next_row["team_name"]:
###                 transitioning_team.append(row["team_name"])  # same team continues
###             elif next_row is not None:
###                 transitioning_team.append(next_row["team_name"])  # opponent takes over
###             else:
###                 transitioning_team.append(row["team_name"])  # last row fallback
###         elif row["type_name"] in fail_actions and row["result_name"] == "fail":
###             if next_row is not None:
###                 transitioning_team.append(next_row["team_name"])  # fail → opponent
###             else:
###                 transitioning_team.append(row["team_name"])  # last row fallback
###         else:
###             transitioning_team.append(row["team_name"])  # default: current team
### 
###     events_df["transitioning_team"] = transitioning_team
### 
### 
###     # --- Keep only relevant columns ---
###     columns_to_keep = [
###         "game_id", "transition_id", "match_min", "period_id", "time_seconds",
###         "start_x", "end_x", "start_y", "end_y",
###         "type_name", "result_name", "bodypart_name",
###         "team_name", "player_name", "xT_value", "transitioning_team"
###     ]
### 
###     transitions_df = events_df[columns_to_keep]
### 
###     # --- Save CSV ---
###     out_path = transitions_dir_path / f"{league}_{season}_transitions.csv"
###     transitions_df.to_csv(out_path, index=False)
###     print(f"⚡ Saved transitions → {out_path}")
### 
###     # --- Filter by team if requested ---
###     if team:
###         team_game_ids = transitions_df.loc[transitions_df['team_name'] == team, 'game_id'].unique()
###         transitions_df = transitions_df.loc[transitions_df['game_id'].isin(team_game_ids)]
### 
###     return transitions_df
### 
### 
### 
### def possession_threat_metric(poss_df):
###     """
###     Calculate Possession Threat (average xT per possession).
###     
###     Parameters:
###         poss_df (DataFrame): must include ['possession_id','team_name','xT_value']
###     
###     Returns:
###         Series: mean possession threat per team
###     """
###     poss_threat = poss_df.groupby(['possession_id','team_name'])['xT_value'].sum().reset_index()
###     return poss_threat.groupby('team_name')['xT_value'].mean()
### 
### 
### def deep_circulation_metric(poss_df):
###     """
###     Calculate Deep Circulation (patience in buildup) using raw measurement values.
###     """
###     goal_x, goal_y = 105, 32
### 
###     # Force a copy to avoid SettingWithCopyWarning
###     poss_df = poss_df.copy()
### 
###     # Movement vectors
###     poss_df.loc[:, 'dx'] = poss_df['end_x'] - poss_df['start_x']
###     poss_df.loc[:, 'dy'] = poss_df['end_y'] - poss_df['start_y']
### 
###     # Goal-oriented progress
###     poss_df.loc[:, 'to_goal_dx'] = goal_x - poss_df['start_x']
###     poss_df.loc[:, 'to_goal_dy'] = goal_y - poss_df['start_y']
###     poss_df.loc[:, 'goal_mag'] = np.sqrt(
###         poss_df['to_goal_dx']**2 + poss_df['to_goal_dy']**2
###     ).replace(0, np.nan)
###     poss_df.loc[:, 'direct_progress'] = (
###         (poss_df['dx'] * poss_df['to_goal_dx'] + poss_df['dy'] * poss_df['to_goal_dy'])
###         / poss_df['goal_mag']
###     )
### 
###     # Possession-level summary
###     possession_summary = poss_df.groupby('possession_id').agg(
###         team_name=('team_name', 'first'),
###         start_x=('start_x', 'first'),
###         end_x=('end_x', 'last'),
###         num_actions=('possession_id', 'count'),
###         total_direct_progress=('direct_progress', 'sum'),
###         start_time=('time_seconds', 'first'),
###         end_time=('time_seconds', 'last')
###     ).reset_index()
### 
###     # Ensure non-negative durations
###     possession_summary.loc[:, 'duration'] = (
###         possession_summary['end_time'] - possession_summary['start_time']
###     ).clip(lower=0)
### 
###     # Only possessions building from own third into final third
###     filt = (possession_summary['start_x'] <= 35) & (possession_summary['end_x'] >= 70)
###     first_third_poss = possession_summary.loc[filt].copy()
### 
###     # Raw deep circulation score
###     first_third_poss.loc[:, 'deep_circulation_raw'] = (
###         (first_third_poss['num_actions'] + 0.5 * first_third_poss['duration'])
###         / (first_third_poss['total_direct_progress'].abs() + 1)
###     )
### 
###     # Aggregate team-level mean (raw measurement)
###     team_scores = first_third_poss.groupby('team_name')['deep_circulation_raw'].mean()
### 
###     return team_scores.sort_values(ascending=False)
### 
### 
### 
### 
### def poss_playstyle(poss_df):
###     """
###     Compile all playstyle metrics into one team-level dataframe with raw measurement values.
###     """
###     circ = deep_circulation_metric(poss_df) 
###     threat = possession_threat_metric(poss_df)
### 
###     team_metrics = pd.concat([circ, threat], axis=1).reset_index()
###     team_metrics.columns = ['team_name', 'deep_circulation', 'possession_threat']
### 
###     return team_metrics.sort_values('deep_circulation', ascending=False)

