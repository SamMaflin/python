from .utils import percentile_phrase

ORANGE = "#ffa500"   # consistent styling for percentile ranks


def team_style_description(row, league_df=None):
    """
    Describe team style relative to league averages AND include league rankings.

    Parameters
    ----------
    row : pandas Series
        A single player's row.
    league_df : DataFrame or None
        Must be the FULL dataset (not role-filtered),
        so we can compute league rankings for team-level metrics.

    Returns
    -------
    HTML string describing team style.
    """

    league = row["League"]
    team = row["Team"]

    # -------------------------------------------
    # 1. Extract team context values
    # -------------------------------------------
    poss  = row["Team_Possession"]
    press = row["Team_PressIntensity"]
    tempo = row["Team_Tempo"]
    att_xg = row["Team_Att_xg_per90"]
    xgd = row["Team_xGD_proxy"]

    lg_poss  = row["Lg_Team_Possession"]
    lg_press = row["Lg_Team_PressIntensity"]
    lg_tempo = row["Lg_Team_Tempo"]
    lg_att_xg = row["Lg_Team_Att_xg"]
    lg_xgd = row["Lg_Team_xGD"]

    # League-relative ratios
    poss_ratio  = poss  / lg_poss
    press_ratio = press / lg_press
    tempo_ratio = tempo / lg_tempo
    att_ratio   = att_xg / lg_att_xg
    def_ratio   = xgd / lg_xgd if lg_xgd != 0 else 1.0

    # -------------------------------------------
    # 2. Compute league rankings (if full league df provided)
    # -------------------------------------------
    if league_df is not None:
        lg = league_df[league_df["League"] == league].copy()

        def rank_in_league(series, value, ascending=False):
            """
            Returns the rank (1 = best). ascending=False means higher=better.
            """
            if ascending:
                return int((series.rank(method="min", ascending=True) == series.where(series == value)).idxmax() + 1)
            else:
                return int((series.rank(method="min", ascending=False) == series.where(series == value)).idxmax() + 1)

        # Group team averages for league-level ranking
        team_group = lg.groupby("Team").agg({
            "Team_Possession": "mean",
            "Team_PressIntensity": "mean",
            "Team_Tempo": "mean",
            "Team_Att_xg_per90": "mean",
            "Team_xGD_proxy": "mean",
        }).reset_index()

        # Extract rankings
        poss_rank  = int(team_group["Team_Possession"].rank(ascending=False).loc[team_group["Team"] == team])
        press_rank = int(team_group["Team_PressIntensity"].rank(ascending=False).loc[team_group["Team"] == team])
        tempo_rank = int(team_group["Team_Tempo"].rank(ascending=False).loc[team_group["Team"] == team])
        att_rank   = int(team_group["Team_Att_xg_per90"].rank(ascending=False).loc[team_group["Team"] == team]) 

        num_teams = len(team_group)
    else:
        poss_rank = press_rank = tempo_rank = att_rank = def_rank = None
        num_teams = None

    # -------------------------------------------
    # 3. Convert ratios → descriptive tiers
    # -------------------------------------------
    def tier(r):
        if r >= 1.30: 
            return "relatively very strong"
        if r >= 1.10: 
            return "relatively strong"
        if r <= 0.75: 
            return "very weak"
        if r <= 0.90: 
            return "relatively weak"
        return "relatively moderate"


    poss_t  = tier(poss_ratio)
    press_t = tier(press_ratio)
    tempo_t = tier(tempo_ratio)
    att_t   = tier(att_ratio)
    def_t   = tier(def_ratio)

    # -------------------------------------------
    # 4. Build readable main sentence
    # -------------------------------------------
    identity = (
        f"<b>{poss_t}</b> possession, "
        f"<b>{press_t}</b> pressing intensity, "
        f"<b>{tempo_t}</b> tempo, "
        f"<b>{att_t}</b> attacking prowess in the attacking third." 
    )

    # -------------------------------------------
    # 5. Add ranking sentence if available
    # -------------------------------------------
    if num_teams:
        ranking_text = (
            f"They ranked <b>{poss_rank}/{num_teams}</b> in possession, "
            f"<b>{press_rank}/{num_teams}</b> in pressing intensity, "
            f"<b>{tempo_rank}/{num_teams}</b> in tempo, "
            f"<b>{att_rank}/{num_teams}</b> in attacking xG, and "
            f"<b>{def_rank}/{num_teams}</b> in defensive xG difference."
        )
    else:
        ranking_text = ""

    # -------------------------------------------
    # 6. Final assembled paragraph
    # -------------------------------------------
    return (
        f"<br><b>Team Style (Within the {league}):</b><br></br>"
        f"Having spent last season at <b>{team}</b>, he's used to playing in a side defined by {identity}.<br>"
        f"{ranking_text}<br><br>"
    )




def generate_position_summary(
    row,
    role_label: str,
    components: list,
    overall_label: str,   # now unused but kept for compatibility
    others=None,
):
    """
    Generic HTML summary for any position.

    Updates requested:
      - Remove global percentile rank section entirely
      - Show BuyScore in orange instead of global rank
      - Add a paragraph after attribute breakdown describing the player's team style
    """

    html = [
        "<div style='color:white;font-size:18px;line-height:1.55;margin-top:1em;'>",

        f"The most suitable match for the <b>{role_label}</b> role is Player "
        f"<b>{row['ID']}</b>, who played for <b>{row['Team']}</b> "
        f"in the <b>{row['League']}</b> last season.<br><br>",

        "<b>Profile:</b><br>",
        f"• Age: <b>{int(row['Age'])}</b><br>"
        f"• Club: <b>{row['Team']}</b><br>"
        f"• League: <b>{row['League']}</b><br>"
        f"• Market Value: <b>£{row['Value']}</b><br>"
        f"• BuyScore: <span style='color:{ORANGE}'><b>{float(row['BuyScore']):.2f}</b></span><br><br>",

        "<b>Attribute Breakdown:</b><br></br>",
    ]

    # ----------------------------------------
    # ATTRIBUTE PERCENTILES (ORANGE)
    # ----------------------------------------
    for label, col, extra in components:
        pct = float(row[col])
        rank = int(round(pct))
        desc = percentile_phrase(pct)
        suffix = f" {extra}" if extra else ""

        html.append(
            f"• <b>{label}</b>: "
            f"Percentile Rank: <span style='color:{ORANGE}'><b>{rank}</b></span> — "
            f"{desc}{suffix}.<br>"
        )

    # ----------------------------------------
    # TEAM CONTEXT SUMMARY (NEW)
    # ----------------------------------------
    html.append(team_style_description(row))

    # ----------------------------------------
    # OTHER STRONG CANDIDATES
    # ----------------------------------------
    if others is not None and len(others) > 0:
        html.append("<b>Other Strong Candidates:</b><br></br>")

        for _, r in others.iterrows():
            bs = float(r["BuyScore"])
            html.append(
                f"• <b>{r['ID']}</b> — {r['Team']} ({r['League']}), "
                f"BuyScore: <span style='color:{ORANGE}'><b>{bs:.2f}</b></span> "
                f"(Value: £{r['Value']})<br>"
            )

    html.append("</div><br></br>")
    return "".join(html)


# ---------------------------------------------------------
# GK SUMMARY
# ---------------------------------------------------------
def generate_gk_summary(row, others):
    components = [
        ("Shot Stopping", "ShotStop_pct", ""),
        ("Distribution", "Distribution_pct", ""),
        ("Sweeping", "Sweeper_pct", ""),
    ]

    return generate_position_summary(
        row=row,
        others=others,
        role_label="Goalkeeper",
        components=components,
        overall_label="",  # not used anymore
    )


# ---------------------------------------------------------
# WINGER SUMMARY
# ---------------------------------------------------------
def generate_winger_summary(row, others):
    components = [
        ("Carrying", "BallCarrier_pct", "(ball progression & dribbling)"),
        ("Creation", "WideCreator_pct", "(chance creation & final-third passing)"),
        ("Goal Threat", "GoalThreat_pct", "(shot quality & box presence)"),
        ("Defensive Winger", "DefensiveWinger_pct", "(defensive work rate)"),
    ]

    return generate_position_summary(
        row=row,
        others=others,
        role_label="Winger",
        components=components,
        overall_label="",
    )


# ---------------------------------------------------------
# MIDFIELDER SUMMARY
# ---------------------------------------------------------
def generate_midfielder_summary(row, others):
    components = [
        ("Ball Winning", "BallWinner_pct", "(duels & recoveries)"),
        ("Deep-Lying Playmaking", "DeepLyingPlaymaker_pct", "(progression & buildup value)"),
        ("Box-to-Box", "BoxToBox_pct", "(transitions & work rate)"),
        ("Attacking Playmaker", "AttackingPlaymaker_pct", "(creativity & final-third play)"),
    ]

    return generate_position_summary(
        row=row,
        others=others,
        role_label="Central Midfielder",
        components=components,
        overall_label="",
    )


# ---------------------------------------------------------
# STRIKER SUMMARY
# ---------------------------------------------------------
def generate_striker_summary(row, others):
    components = [
        ("Finishing", "Finisher_pct", "(shot quality & goals vs xG)"),
        ("Target Man", "TargetMan_pct", "(aerial duels & hold-up play)"),
        ("False 9", "False9_pct", "(link play & chance creation)"),
        ("Defensive Forward", "DefensiveForward_pct", "(defensive effort & work rate)"),
    ]

    return generate_position_summary(
        row=row,
        others=others,
        role_label="Striker",
        components=components,
        overall_label="",
    )
