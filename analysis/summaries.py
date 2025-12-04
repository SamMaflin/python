from .utils import percentile_phrase

ORANGE = "#ffa500"   # consistent styling for percentile ranks


def generate_position_summary(
    row,
    role_label: str,
    components: list,
    overall_label: str,
    others=None,
):
    """
    Generic HTML summary for any position.

    components: list of tuples:
        [ ("Nice Label", "Percentile_Column_Name", "optional suffix"), ... ]

    Now updated to use:
        • Attribute percentile: component pct columns
        • Overall performance percentile: Overall_pct_global
        • BuyScore shown separately (value efficiency)
    """

    html = [
        "<div style='color:white;font-size:18px;line-height:1.55;margin-top:1em;'>",

        f"The most suitable match for the <b>{role_label}</b> role is Player "
        f"<b>{row['ID']}</b>, who played for <b>{row['Team']}</b> "
        f"in the <b>{row['League']}</b> last season.<br><br>",

        "<b>Profile:</b><br>"
        f"• Age: <b>{int(row['Age'])}</b><br>"
        f"• Club: <b>{row['Team']}</b><br>"
        f"• League: <b>{row['League']}</b><br>"
        f"• Market Value: <b>£{row['Value']}</b><br>"
        f"• BuyScore: <b>{float(row['BuyScore']):.2f}</b><br><br>",

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
    # GLOBAL OVERALL PERFORMANCE (NEW)
    # ----------------------------------------
    global_pct = float(row["Overall_pct_global"])
    global_rank = int(round(global_pct))

    html.append("<br>")
    html.append(
        f"<b>{overall_label}:</b> "
        f"Global Percentile Rank: "
        f"<span style='color:{ORANGE}'><b>{global_rank}</b></span> "
        f"(vs all {role_label.lower()}s in the dataset).<br><br>"
    )

    # ----------------------------------------
    # OTHER STRONG CANDIDATES (GLOBAL PERFORMANCE + BUYSCORE)
    # ----------------------------------------
    if others is not None and len(others) > 0:
        html.append("<b>Other Strong Candidates:</b><br></br>")

        for _, r in others.iterrows():

            g_pct = float(r["Overall_pct_global"])
            g_rank = int(round(g_pct))

            html.append(
                f"• <b>{r['ID']}</b> — {r['Team']} ({r['League']}), "
                f"Global Rank: <span style='color:{ORANGE}'><b>{g_rank}</b></span>, "
                f"BuyScore: {float(r['BuyScore']):.2f} "
                f"(Value: £{r['Value']})<br>"
            )

    html.append("</div>")
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
        overall_label="Overall GK Performance",
    )


# ---------------------------------------------------------
# WINGER SUMMARY
# ---------------------------------------------------------
def generate_winger_summary(row, others):
    components = [
        ("Carrying", "Carrier_pct", "(ball progression & dribbling)"),
        ("Creation", "Creator_pct", "(chance creation & final-third passing)"),
        ("Goal Threat", "GoalThreat_pct", "(shot quality & box presence)"),
        ("Pressing", "Presser_pct", "(defensive work rate)"),
    ]

    return generate_position_summary(
        row=row,
        others=others,
        role_label="Winger",
        components=components,
        overall_label="Overall Winger Performance",
    )


# ---------------------------------------------------------
# MIDFIELDER SUMMARY
# ---------------------------------------------------------
def generate_midfielder_summary(row, others):
    components = [
        ("Ball Winning", "BallWinner_pct", "(duels & recoveries)"),
        ("Playmaking", "Playmaker_pct", "(progression & buildup value)"),
        ("Box-to-Box", "BoxToBox_pct", "(transitions & work rate)"),
        ("Attacking Midfielder", "AttackingMid_pct", "(creativity & final-third play)"),
    ]

    return generate_position_summary(
        row=row,
        others=others,
        role_label="Central Midfielder",
        components=components,
        overall_label="Overall Midfielder Performance",
    )


# ---------------------------------------------------------
# STRIKER SUMMARY
# ---------------------------------------------------------
def generate_striker_summary(row, others):
    components = [
        ("Finishing", "Finisher_pct", "(shot quality & goals vs xG)"),
        ("Target Man", "TargetMan_pct", "(aerial duels & hold-up play)"),
        ("Creator Striker", "CreatorStriker_pct", "(link play & chance creation)"),
        ("Pressing", "PresserStriker_pct", "(defensive effort & work rate)"),
    ]

    return generate_position_summary(
        row=row,
        others=others,
        role_label="Striker",
        components=components,
        overall_label="Overall Striker Performance",
    )
