from .utils import percentile_phrase
import numpy as np
import pandas as pd

ORANGE = "#ffa500"   # consistent styling for percentile ranks


def _safe_get(row, primary, fallback=None, default=np.nan):
    """
    Helper to safely get a value from a row with an optional fallback key.
    """
    if primary in row:
        return row[primary]
    if fallback is not None and fallback in row:
        return row[fallback]
    return default


def team_style_description(row: pd.Series, league_df: pd.DataFrame | None = None) -> str:
    """
    Describe team style relative to league averages AND (optionally) include league rankings.

    Parameters
    ----------
    row : pandas.Series
        A single player's row (after modelling).
    league_df : pandas.DataFrame or None, optional
        The FULL dataset (not role-filtered). If provided, we compute
        league rankings for team-level style metrics. If None, only
        relative tiers are shown.

    Returns
    -------
    str
        HTML string describing team style.
    """

    league = row.get("League", "the league")
    team = row.get("Team", "their team")

    # -------------------------------------------------
    # 1. Extract team context values (with fallbacks)
    #    New engine uses *Proxy names; old code used
    #    Team_Possession / Team_Tempo etc.
    # -------------------------------------------------
    poss = _safe_get(row, "Team_PossessionProxy", "Team_Possession")
    press = _safe_get(row, "Team_PressIntensity")
    tempo = _safe_get(row, "Team_TempoProxy", "Team_Tempo")
    att_xg = _safe_get(row, "Team_Att_xg_per90")
    xgd = _safe_get(row, "Team_xGD_proxy")

    # League means – use *_Proxy if present, else legacy names
    lg_poss = _safe_get(row, "Lg_Team_PossessionProxy", "Lg_Team_Possession", default=np.nan)
    lg_press = _safe_get(row, "Lg_Team_PressIntensity", default=np.nan)
    lg_tempo = _safe_get(row, "Lg_Team_TempoProxy", "Lg_Team_Tempo", default=np.nan)
    lg_att_xg = _safe_get(row, "Lg_Team_Att_xg", default=np.nan)
    lg_xgd = _safe_get(row, "Lg_Team_xGD", default=np.nan)

    # -------------------------------------------------
    # 2. League-relative ratios (team vs league avg)
    # -------------------------------------------------
    def safe_ratio(num, den):
        if pd.isna(num) or pd.isna(den) or den == 0:
            return 1.0
        return float(num) / float(den)

    poss_ratio = safe_ratio(poss, lg_poss)
    press_ratio = safe_ratio(press, lg_press)
    tempo_ratio = safe_ratio(tempo, lg_tempo)
    att_ratio = safe_ratio(att_xg, lg_att_xg)
    def_ratio = safe_ratio(xgd, lg_xgd)

    # -------------------------------------------------
    # 3. Compute league rankings (if full league df provided)
    # -------------------------------------------------
    poss_rank = press_rank = tempo_rank = att_rank = def_rank = None
    num_teams = None

    if league_df is not None and "Team" in league_df.columns and "League" in league_df.columns:
        lg = league_df[league_df["League"] == league].copy()

        if not lg.empty:
            # Match engine naming for team-level columns
            team_group_cols = {
                "Team_PossessionProxy": "Team_PossessionProxy",
                "Team_PressIntensity": "Team_PressIntensity",
                "Team_TempoProxy": "Team_TempoProxy",
                "Team_Att_xg_per90": "Team_Att_xg_per90",
                "Team_xGD_proxy": "Team_xGD_proxy",
            }

            # Only keep columns that actually exist
            agg_dict = {v: "mean" for v in team_group_cols.values() if v in lg.columns}

            if agg_dict:
                team_group = lg.groupby("Team", as_index=False).agg(agg_dict)
                num_teams = len(team_group)

                def _rank_metric(col_name: str) -> int | None:
                    if col_name not in team_group.columns or num_teams is None:
                        return None
                    # Rank higher values as better (ascending=False)
                    ranks = team_group[col_name].rank(
                        method="min", ascending=False
                    )
                    # Team row
                    mask = team_group["Team"] == team
                    if not mask.any():
                        return None
                    return int(ranks[mask].iloc[0])

                poss_rank = _rank_metric("Team_PossessionProxy")
                press_rank = _rank_metric("Team_PressIntensity")
                tempo_rank = _rank_metric("Team_TempoProxy")
                att_rank = _rank_metric("Team_Att_xg_per90")
                def_rank = _rank_metric("Team_xGD_proxy")

    # -------------------------------------------------
    # 4. Convert ratios → descriptive tiers
    # -------------------------------------------------
    def tier(r: float) -> str:
        if r >= 1.30:
            return "relatively very strong"
        if r >= 1.10:
            return "relatively strong"
        if r <= 0.75:
            return "very weak"
        if r <= 0.90:
            return "relatively weak"
        return "relatively moderate"

    poss_t = tier(poss_ratio)
    press_t = tier(press_ratio)
    tempo_t = tier(tempo_ratio)
    att_t = tier(att_ratio)
    def_t = tier(def_ratio)

    # -------------------------------------------------
    # 5. Build readable identity sentence
    # -------------------------------------------------
    identity = (
        f"<b>{poss_t}</b> possession, "
        f"<b>{press_t}</b> pressing intensity, "
        f"<b>{tempo_t}</b> tempo, "
        f"<b>{att_t}</b> attacking output, and "
        f"<b>{def_t}</b> defensive xG difference"
    )

    # -------------------------------------------------
    # 6. Add ranking sentence if available
    # -------------------------------------------------
    if num_teams and num_teams > 0:
        ranking_bits = []

        if poss_rank is not None:
            ranking_bits.append(f"possession: <b>{poss_rank}/{num_teams}</b>")
        if press_rank is not None:
            ranking_bits.append(f"pressing intensity: <b>{press_rank}/{num_teams}</b>")
        if tempo_rank is not None:
            ranking_bits.append(f"tempo: <b>{tempo_rank}/{num_teams}</b>")
        if att_rank is not None:
            ranking_bits.append(f"attacking xG: <b>{att_rank}/{num_teams}</b>")
        if def_rank is not None:
            ranking_bits.append(f"defensive xG difference: <b>{def_rank}/{num_teams}</b>")

        if ranking_bits:
            ranking_text = "They ranked " + ", ".join(ranking_bits) + " within the league."
        else:
            ranking_text = ""
    else:
        ranking_text = ""

    # -------------------------------------------------
    # 7. Final assembled paragraph
    # -------------------------------------------------
    return (
        f"<br><b>Team Style (within the {league}):</b><br></br>"
        f"Having spent last season at <b>{team}</b>, he's used to playing in a side defined by {identity}.<br>"
        f"{ranking_text}<br><br>"
    )


def generate_position_summary(
    row: pd.Series,
    role_label: str,
    components: list,
    overall_label: str,   # kept for compatibility, but unused
    others: pd.DataFrame | None = None,
    league_df: pd.DataFrame | None = None,
) -> str:
    """
    Generic HTML summary for any position.

    Behaviour:
      - No global percentile rank section anymore.
      - Shows BuyScore in orange instead of global rank.
      - Includes a paragraph describing the player's team style.
    """

    player_id = row.get("ID", "N/A")
    age = row.get("Age", np.nan)
    team = row.get("Team", "Unknown club")
    league = row.get("League", "Unknown league")
    value = row.get("Value", "N/A")
    buyscore = float(row.get("BuyScore", 0.0))

    html = [
        "<div style='color:white;font-size:18px;line-height:1.55;margin-top:1em;'>",
        f"The most suitable match for the <b>{role_label}</b> role is Player "
        f"<b>{player_id}</b>, who played for <b>{team}</b> "
        f"in the <b>{league}</b> last season.<br><br>",

        "<b>Profile:</b><br>",
        f"• Age: <b>{int(age) if not pd.isna(age) else 'N/A'}</b><br>"
        f"• Club: <b>{team}</b><br>"
        f"• League: <b>{league}</b><br>"
        f"• Market Value: <b>£{value}</b><br>"
        f"• BuyScore: <span style='color:{ORANGE}'><b>{buyscore:.2f}</b></span><br><br>",

        "<b>Attribute Breakdown:</b><br></br>",
    ]

    # -------------------------------------------------
    # ATTRIBUTE PERCENTILES (ORANGE)
    # -------------------------------------------------
    for label, col, extra in components:
        pct = float(row.get(col, 0.0))
        rank = int(round(pct))
        desc = percentile_phrase(pct)
        suffix = f" {extra}" if extra else ""

        html.append(
            f"• <b>{label}</b>: "
            f"Percentile Rank: <span style='color:{ORANGE}'><b>{rank}</b></span> — "
            f"{desc}{suffix}.<br>"
        )

    # -------------------------------------------------
    # TEAM CONTEXT SUMMARY
    # -------------------------------------------------
    html.append(team_style_description(row, league_df=league_df))

    # -------------------------------------------------
    # OTHER STRONG CANDIDATES
    # -------------------------------------------------
    if others is not None and len(others) > 0:
        html.append("<b>Other Strong Candidates:</b><br></br>")

        for _, r in others.iterrows():
            bs = float(r.get("BuyScore", 0.0))
            html.append(
                f"• <b>{r.get('ID', 'N/A')}</b> — {r.get('Team', 'Unknown club')} "
                f"({r.get('League', 'Unknown league')}), "
                f"BuyScore: <span style='color:{ORANGE}'><b>{bs:.2f}</b></span> "
                f"(Value: £{r.get('Value', 'N/A')})<br>"
            )

    html.append("</div><br></br>")
    return "".join(html)


# ---------------------------------------------------------
# GK SUMMARY
# ---------------------------------------------------------
def generate_gk_summary(row: pd.Series, others: pd.DataFrame | None, league_df: pd.DataFrame | None = None) -> str:
    components = [
        ("Shot Stopping", "ShotStop_pct", ""),
        ("Distribution", "Distribution_pct", ""),
        ("Sweeping", "Sweeper_pct", ""),
    ]

    return generate_position_summary(
        row=row,
        others=others,
        league_df=league_df,
        role_label="Goalkeeper",
        components=components,
        overall_label="",  # not used anymore
    )


# ---------------------------------------------------------
# WINGER SUMMARY
# ---------------------------------------------------------
def generate_winger_summary(row: pd.Series, others: pd.DataFrame | None, league_df: pd.DataFrame | None = None) -> str:
    components = [
        ("Carrying", "BallCarrier_pct", "(ball progression & dribbling)"),
        ("Creation", "WideCreator_pct", "(chance creation & final-third passing)"),
        ("Goal Threat", "GoalThreat_pct", "(shot quality & box presence)"),
        ("Defensive Winger", "DefensiveWinger_pct", "(defensive work rate)"),
    ]

    return generate_position_summary(
        row=row,
        others=others,
        league_df=league_df,
        role_label="Winger",
        components=components,
        overall_label="",
    )


# ---------------------------------------------------------
# MIDFIELDER SUMMARY
# ---------------------------------------------------------
def generate_midfielder_summary(row: pd.Series, others: pd.DataFrame | None, league_df: pd.DataFrame | None = None) -> str:
    components = [
        ("Ball Winning", "BallWinner_pct", "(duels & recoveries)"),
        ("Deep-Lying Playmaking", "DeepLyingPlaymaker_pct", "(progression & buildup value)"),
        ("Box-to-Box", "BoxToBox_pct", "(transitions & work rate)"),
        ("Attacking Playmaker", "AttackingPlaymaker_pct", "(creativity & final-third play)"),
    ]

    return generate_position_summary(
        row=row,
        others=others,
        league_df=league_df,
        role_label="Central Midfielder",
        components=components,
        overall_label="",
    )


# ---------------------------------------------------------
# STRIKER SUMMARY
# ---------------------------------------------------------
def generate_striker_summary(row: pd.Series, others: pd.DataFrame | None, league_df: pd.DataFrame | None = None) -> str:
    components = [
        ("Finishing", "Finisher_pct", "(shot quality & goals vs xG)"),
        ("Target Man", "TargetMan_pct", "(aerial duels & hold-up play)"),
        ("False 9", "False9_pct", "(link play & chance creation)"),
        ("Defensive Forward", "DefensiveForward_pct", "(defensive effort & work rate)"),
    ]

    return generate_position_summary(
        row=row,
        others=others,
        league_df=league_df,
        role_label="Striker",
        components=components,
        overall_label="",
    )
