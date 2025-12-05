 # MODEL CONFIGURATION – ALL ROLES STORED IN ONE STRUCTURED DICTIONARY 

from .utils import safe_div


ROLE_CONFIG = {

    "__settings__": {
        "DEFAULT_PATH": "analysis/Final_Task_Data.csv",
        "DEFAULT_BUDGET": 10,
        "DEFAULT_MINUTES": 900,
    },

    
    # GOALKEEPER
    "goalkeeper": {
        "positions": {"Goalkeeper"},

        "baseline": {
            "Save Efficiency Above Expected (%)": lambda df: (
                df["Save_percentage"] - df["Xsave_percentage"]
            ),

            "Goals Saved Above Expected per Shot": lambda df: safe_div(
                df["Goals_saved_above_avg"], df["Shots_on_target_faced"]
            ),

            "Goals Saved Above Expected": lambda df: df["Goals_saved_above_avg"],

            "Pressured Pass Efficiency": lambda df: (
                df["Passing_percentage_under_pressure"]
                * (df["Percentage_passes_under_pressure"] / 100)
            ),

            "Long Pass Efficiency": lambda df: (
                df["Long_ball_percentage"] * df["Successful_pass_length"]
            ),

            "Pass Progression Efficiency": lambda df: (
                df["Forward_pass_proportion"] * df["Successful_pass_length"]
            ),

            "Pass Completion": lambda df: df["Passing_percentage"],

            "Sweeper Action Distance": lambda df: df["Gk_defesive_action_distance"],

            "Sweeper Actions": lambda df: df["Defensive_actions"],

            "Error Rate": lambda df: safe_div(
                df.get("Errors", 0) + df.get("Turnovers", 0),
                df["Minutes"] / 90,
            ),
        },

        "indices": {
            "ShotStop_Index": {
                "Save Efficiency Above Expected (%)": 0.25,
                "Goals Saved Above Expected per Shot": 0.30,
                "Goals Saved Above Expected": 0.45,
            },
            "Distribution_Index": {
                "Pressured Pass Efficiency": 0.20,
                "Long Pass Efficiency": 0.25,
                "Pass Progression Efficiency": 0.25,
                "Pass Completion": 0.30,
            },
            "Sweeper_Index": {
                "Sweeper Actions": 0.60,
                "Sweeper Action Distance": 0.30,
                "Error Rate": -0.10,
            },
        },

        "groups": {
            "Shot Stopping": [
                "Goals Saved Above Expected per Shot",
                "Save Efficiency Above Expected (%)",
                "Goals Saved Above Expected",
            ],
            "Distribution": [
                "Pressured Pass Efficiency",
                "Long Pass Efficiency",
                "Pass Progression Efficiency",
                "Pass Completion",
            ],
            "Sweeping": [
                "Sweeper Actions",
                "Sweeper Action Distance",
                "Error Rate",
            ],
        },

        "weights": {
            "Shot Stopping": 0.55,
            "Distribution": 0.35,
            "Sweeping": 0.10,
        },

        "invert": {"Error Rate"},

        "sliders": [
            ("Shot Stopper", "Shot Stopping"),
            ("Distributor", "Distribution"),
            ("Sweeper", "Sweeping"),
        ],

        "columns": [
            "ID", "Team", "League",
            "ShotStop_Index", "Distribution_Index", "Sweeper_Index",
            "ShotStop_pct", "Distribution_pct", "Sweeper_pct",
            "Overall_pct", "BuyScore",
            "Age", "Value",
        ],

        "text": """
        Where better to start than with the <i>last line of defence</i> — the <b>Goalkeeper</b>.<br></br>
        ● The <b>Shot-Stopper</b> — excels in save efficiency, reflexes, and high-quality shot prevention.<br>
        ● The <b>Sweeper</b> — dominates space behind the defence, anticipates danger, and enables a higher line.<br>
        ● The <b>Distributor</b> — initiates build-up play with clean short passing and accurate long distribution.<br></br>
        Adjust the priority sliders to pinpoint the profile that best fits your recruitment criteria...<br>
        """,
    },

    
    # WINGER
    
    "winger": {
        "positions": {
            "Right Midfielder", "Right Winger", "Right Wing Back",
            "Left Midfielder", "Left Wing", "Left Wing Back", "Left Winger",
        },

        "baseline": {
            # CARRIERS
            "Dribble Efficiency": lambda df: safe_div(
                df["Dribbles_successful_ctx"], df["Dribbles_attempts_ctx"]
            ),
            "Carry Efficiency": lambda df: df["Successful_carries_percentage"],
            "Carrier Risk": lambda df: safe_div(
                df["Failed_dribbles_ctx"] + df["Dispossessed_ctx"],
                df["Minutes"] / 90
            ),
            "Dangerous Carries": lambda df: (
                df["Carries_ctx"] * df["Carry_length_ctx"]
            ),

            # CREATORS
            "Open Play Creativity": lambda df: (
                df["Op_xa_ctx"] + df["Op_key_passes_ctx"] * 0.1
            ),
            "Box Entry Passing": lambda df: (
                df["Op_passes_into_box_ctx"] + df["Passes_inside_box_ctx"]
            ),
            "Through Ball Value": lambda df: df["Through_balls_ctx"],
            "Crossing Value": lambda df: (
                df["Crosses_completed_ctx"] * df["Crossing_percentage"]
            ),

            # GOAL THREAT
            "Shot Quality": lambda df: df["Np_xg_per_shot"],
            "Shot Volume": lambda df: df["Np_shots_ctx"],
            "Finishing Efficiency": lambda df: df["Goal_conversion"],
            "Box Presence": lambda df: df["Touches_in_box_ctx"],
            "Actual vs Expected Goals": lambda df: (
                df["Np_goals_ctx"] - df["Np_xg_ctx"]
            ),

            # PRESSING
            "Pressing Volume": lambda df: df["Padj_pressures_ctx"],
            "Pressing Efficiency": lambda df: safe_div(
                df["Successful_pressures_ctx"], df["Padj_pressures_ctx"]
            ),
            "Counterpress Intensity": lambda df: df["Opp_half_counterpressures_ctx"],
            "Counterpress Success": lambda df: df["Successful_counterpressures_ctx"],
            "High Press Zone Actions": lambda df: df["Opp_half_pressures_ctx"],
            "Dribble Stop Rate": lambda df: df["Dribbles_faced_stopped_percentage"],
        },

        "indices": {
            "BallCarrier_Index": {
                "Dribble Efficiency": 0.35,
                "Dangerous Carries": 0.30,
                "Carry Efficiency": 0.20,
                "Carrier Risk": -0.15,
            },
            "WideCreator_Index": {
                "Open Play Creativity": 0.40,
                "Box Entry Passing": 0.25,
                "Through Ball Value": 0.20,
                "Crossing Value": 0.15,
            },
            "GoalThreat_Index": {
                "Shot Quality": 0.25,
                "Shot Volume": 0.25,
                "Finishing Efficiency": 0.25,
                "Box Presence": 0.15,
                "Actual vs Expected Goals": 0.10,
            },
            "DefensiveWinger_Index": {
                "Pressing Volume": 0.25,
                "Pressing Efficiency": 0.20,
                "Counterpress Intensity": 0.20,
                "Counterpress Success": 0.15,
                "High Press Zone Actions": 0.10,
                "Dribble Stop Rate": 0.10,
            },
        },

        "groups": {
            "Ball Carrier": [
                "Dribble Efficiency", "Carry Efficiency",
                "Dangerous Carries", "Carrier Risk",
            ],
            "Wide Creator": [
                "Open Play Creativity", "Box Entry Passing",
                "Through Ball Value", "Crossing Value",
            ],
            "Goal Threat": [
                "Shot Quality", "Shot Volume", "Finishing Efficiency",
                "Box Presence", "Actual vs Expected Goals",
            ],
            "Defensive Winger": [
                "Pressing Volume", "Pressing Efficiency",
                "Counterpress Intensity", "Counterpress Success",
                "High Press Zone Actions", "Dribble Stop Rate",
            ],
        },

        "weights": {
            "Ball Carrier": 0.35,
            "Wide Creator": 0.25,
            "Goal Threat": 0.25,
            "Defensive Winger": 0.15,
        },

        "invert": {"Carrier Risk"},

        "sliders": [
            ("Ball Carrier", "Ball Carrier"),
            ("Wide Creator", "Wide Creator"),
            ("Goal Threat", "Goal Threat"),
            ("Defensive Winger", "Defensive Winger"),
        ],

        "columns": [
            "ID", "Team", "League",
            "BallCarrier_Index", "WideCreator_Index", "GoalThreat_Index", "DefensiveWinger_Index",
            "BallCarrier_pct", "WideCreator_pct", "GoalThreat_pct", "DefensiveWinger_pct",
            "Overall_pct", "BuyScore",
            "Age", "Value",
        ],

        "text": """
        Next we turn to the wide players who inject pace, creativity, and decisive output — the <b>Wingers</b>.<br></br>
        ● The <b>Ball Carrier</b> — drives progression through ball-carrying and dribbling.<br>
        ● The <b>Wide Creator</b> — supplies incisive passing and final-third delivery.<br>
        ● The <b>Goal Threat</b> — provides high-quality shooting and penalty-box actions.<br>
        ● The <b>Defensive Winger</b> — leads high pressing and counterpressing intensity.<br></br>
        """,
    },

    
    # CENTRAL MIDFIELDER
    
    "midfielder": {
        "positions": {
            "Central Midfielder", "Centre Midfielder",
            "Right Centre Midfielder", "Left Centre Midfielder",
            "Defensive Midfielder", "Centre Defensive Midfielder",
            "Right Defensive Midfielder", "Left Defensive Midfielder",
            "Attacking Midfielder", "Centre Attacking Midfielder",
            "Right Attacking Midfielder", "Left Attacking Midfielder",
        },

        "baseline": {
            # BALL WINNER
            "Tackle Win Rate": lambda df: safe_div(
                df["Tackles_ctx"], df["Minutes"] / 90
            ),
            "Interception Volume": lambda df: safe_div(
                df["Interceptions_ctx"], df["Minutes"] / 90
            ),
            "Padj Tackle Impact": lambda df: df["Padj_tackles_ctx"],
            "Padj Interception Impact": lambda df: df["Padj_interceptions_ctx"],
            "Dribble Stop Rate": lambda df: df["Dribbles_faced_stopped_percentage"],
            "Ball Recoveries": lambda df: df["Ball_recoveries_ctx"],

            # PLAYMAKER
            "Forward Pass Value": lambda df: (
                df["Forward_pass_proportion"] * df["Passing_percentage"]
            ),
            "Long Pass Quality": lambda df: (
                df["Long_ball_percentage"] * df["Successful_pass_length"]
            ),
            "Build-Up Contribution": lambda df: df["Op_xgbuildup_ctx"],
            "XGChain Influence": lambda df: df["Op_xgchain_ctx"],
            "Progressive Third Passes": lambda df: df["Op_last_3rd_passes_ctx"],

            # BOX TO BOX
            "Carries Into Final Third": lambda df: df["Pass_and_carry_last_3rd_ctx"],
            "Counterpressing": lambda df: df["Counterpressures_ctx"],
            "Ball Carry Value": lambda df: (
                df["Carries_ctx"] * df["Carry_length_ctx"]
            ),
            "Transition Defensive Work": lambda df: df["Successful_counterpressures_ctx"],
            "Distance Pressing": lambda df: df["Pressing_distance"],

            # ATTACKING MID
            "Final Third Creativity": lambda df: (
                df["Op_key_passes_ctx"] + df["Op_xa_ctx"]
            ),
            "Through Ball Quality": lambda df: df["Through_balls_ctx"],
            "Box Entry Deliveries": lambda df: (
                df["Op_passes_into_box_ctx"] + df["Passes_inside_box_ctx"]
            ),
            "Shot Assist Impact": lambda df: df["Key_passes_ctx"],
            "Chance Conversion Influence": lambda df: df["Assists_ctx"],
        },

        "indices": {
            "BallWinner_Index": {
                "Tackle Win Rate": 0.25,
                "Interception Volume": 0.20,
                "Padj Tackle Impact": 0.20,
                "Padj Interception Impact": 0.15,
                "Ball Recoveries": 0.10,
                "Dribble Stop Rate": 0.10,
            },

            "DeepLyingPlaymaker_Index": {
                "Forward Pass Value": 0.25,
                "Long Pass Quality": 0.20,
                "Build-Up Contribution": 0.25,
                "XGChain Influence": 0.20,
                "Progressive Third Passes": 0.10,
            },

            "BoxToBox_Index": {
                "Carries Into Final Third": 0.25,
                "Counterpressing": 0.20,
                "Ball Carry Value": 0.20,
                "Transition Defensive Work": 0.20,
                "Distance Pressing": 0.15,
            },

            "AttackingPlaymaker_Index": {
                "Final Third Creativity": 0.35,
                "Through Ball Quality": 0.20,
                "Box Entry Deliveries": 0.20,
                "Shot Assist Impact": 0.15,
                "Chance Conversion Influence": 0.10,
            },
        },

        "groups": {
            "Ball Winner": [
                "Tackle Win Rate", "Interception Volume",
                "Padj Tackle Impact", "Padj Interception Impact",
                "Ball Recoveries", "Dribble Stop Rate",
            ],
            "Deep-Lying Playmaker": [
                "Forward Pass Value", "Long Pass Quality",
                "Build-Up Contribution", "XGChain Influence",
                "Progressive Third Passes",
            ],
            "Box-to-Box": [
                "Carries Into Final Third", "Counterpressing",
                "Ball Carry Value", "Transition Defensive Work",
                "Distance Pressing",
            ],
            "Attacking Playmaker": [
                "Final Third Creativity", "Through Ball Quality",
                "Box Entry Deliveries", "Shot Assist Impact",
                "Chance Conversion Influence",
            ],
        },

        "weights": {
            "Ball Winner": 0.25,
            "Deep-Lying Playmaker": 0.25,
            "Box-to-Box": 0.25,
            "Attacking Playmaker": 0.25,
        },

        "invert": set(),

        "sliders": [
            ("Ball Winner", "Ball Winner"),
            ("Deep-Lying Playmaker", "Deep-Lying Playmaker"),
            ("Box-to-Box", "Box-to-Box"),
            ("Attacking Playmaker", "Attacking Playmaker"),
        ],

        "columns": [
            "ID", "Team", "League",
            "BallWinner_Index", "DeepLyingPlaymaker_Index",
            "BoxToBox_Index", "AttackingPlaymaker_Index",
            "BallWinner_pct", "DeepLyingPlaymaker_pct",
            "BoxToBox_pct", "AttackingPlaymaker_pct",
            "Overall_pct", "BuyScore",
            "Age", "Value",
        ],

        "text": """
        We now arrive in the engine room — the <b>Central Midfielder</b>.<br></br>
        ● The <b>Ball-Winner</b> — disrupts opponents and dominates duels.<br>
        ● The <b>Deep-Lying Playmaker</b> — dictates tempo and drives buildup.<br>
        ● The <b>Box-to-Box</b> — covers ground and impacts transitions.<br>
        ● The <b>Attacking Playmaker</b> — unlocks defences with creativity and incisive passing.<br></br>
        """,
    },

    
    # STRIKER 
    "striker": {
        "positions": {
            "Centre Forward",
            "Left Centre Forward",
            "Right Centre Forward",
        },

        "baseline": {
            # FINISHER
            "Shot Quality": lambda df: df["Np_xg_per_shot"],
            "Shot Volume": lambda df: df["Np_shots_ctx"],
            "Finishing Efficiency": lambda df: df["Goal_conversion"],
            "Actual vs Expected Goals": lambda df: (
                df["Np_goals_ctx"] - df["Np_xg_ctx"]
            ),
            "Shot on Target %": lambda df: df["Shot_target_percentage"],

            # TARGET MAN
            "Aerial Win Rate": lambda df: df["Aerial_percentage"],
            "Aerial Duels Won": lambda df: df["Aerial_won"],
            "Hold-Up Passing": lambda df: (
                df["Passing_percentage"] * df["Backward_pass_proportion"]
            ),
            "Box Presence": lambda df: df["Touches_in_box_ctx"],
            "Layoff Value": lambda df: df["Op_xgbuildup_per_possession_ctx"],

            # False 9
            "Link-Up Pass Value": lambda df: (
                df["Op_xa_ctx"] + df["Op_key_passes_ctx"] * 0.15
            ),
            "Through Ball Creation": lambda df: df["Through_balls_ctx"],
            "Chance Creation Volume": lambda df: df["Key_passes_ctx"],
            "Box Entry Passing": lambda df: df["Op_passes_into_box_ctx"],
            "Set Play Chance Creation": lambda df: df["Sp_key_passes"],

            # PRESSER
            "Pressures Applied": lambda df: df["Padj_pressures_ctx"],
            "Pressing Efficiency": lambda df: safe_div(
                df["Successful_pressures_ctx"], df["Padj_pressures_ctx"]
            ),
            "Counterpressing": lambda df: df["Counterpressures_ctx"],
            "High Press Work Rate": lambda df: df["Opp_half_pressures_ctx"],
            "Turnovers Forced": lambda df: df["Turnovers_ctx"],
        },

        "indices": {
            "Finisher_Index": {
                "Shot Quality": 0.30,
                "Shot Volume": 0.25,
                "Finishing Efficiency": 0.20,
                "Actual vs Expected Goals": 0.15,
                "Shot on Target %": 0.10,
            },

            "TargetMan_Index": {
                "Aerial Win Rate": 0.30,
                "Aerial Duels Won": 0.25,
                "Hold-Up Passing": 0.20,
                "Box Presence": 0.15,
                "Layoff Value": 0.10,
            },

            "False9_Index": {
                "Link-Up Pass Value": 0.40,
                "Through Ball Creation": 0.20,
                "Chance Creation Volume": 0.20,
                "Box Entry Passing": 0.15,
                "Set Play Chance Creation": 0.05,
            },

            "DefensiveForward_Index": {
                "Pressures Applied": 0.35,
                "Pressing Efficiency": 0.25,
                "Counterpressing": 0.20,
                "High Press Work Rate": 0.15,
                "Turnovers Forced": 0.05,
            },
        },

        "groups": {
            "Finisher": [
                "Shot Quality", "Shot Volume", "Finishing Efficiency",
                "Actual vs Expected Goals", "Shot on Target %",
            ],
            "Target Man": [
                "Aerial Win Rate", "Aerial Duels Won",
                "Hold-Up Passing", "Box Presence", "Layoff Value",
            ],
            "False 9": [
                "Link-Up Pass Value", "Through Ball Creation",
                "Chance Creation Volume", "Box Entry Passing",
                "Set Play Chance Creation",
            ],
            "Defensive Forward": [
                "Pressures Applied", "Pressing Efficiency",
                "Counterpressing", "High Press Work Rate",
                "Turnovers Forced",
            ],
        },

        "weights": {
            "Finisher": 0.25,
            "Target Man": 0.25,
            "False 9": 0.25,
            "Defensive Forward": 0.25,
        },

        "invert": set(),

        "sliders": [
            ("Finisher", "Finisher"),
            ("Target Man", "Target Man"),
            ("False 9", "False 9"),
            ("Defensive Forward", "Defensive Forward"),
        ],

        "columns": [
            "ID", "Team", "League",
            "Finisher_Index", "TargetMan_Index",
            "False9_Index", "DefensiveForward_Index",
            "Finisher_pct", "TargetMan_pct",
            "False9_pct", "DefensiveForward_pct",
            "Overall_pct", "BuyScore",
            "Age", "Value",
        ],

        "text": """
        Finally, the spearhead of the attack — the <b>Striker</b>.<br></br>
        ● The <b>Finisher</b> — clinical, efficient, and deadly inside the box.<br>
        ● The <b>Target Man</b> — aerially dominant and strong in hold-up play.<br>
        ● The <b>False 9</b> — links play, assists, and combines intelligently.<br>
        ● The <b>Defensive Forward</b> — sets the tone defensively and disrupts buildup.<br></br>
        """,
    },
}
