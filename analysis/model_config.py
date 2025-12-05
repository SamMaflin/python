# MODEL CONFIGURATION – ALL ROLES STORED IN ONE STRUCTURED DICTIONARY

from .utils import safe_div


ROLE_CONFIG = {

    "__settings__": {
        "DEFAULT_PATH": "analysis/Final_Task_Data.csv",
        "DEFAULT_BUDGET": 10,
        "DEFAULT_MINUTES": 900,
    },

    # ================================================================
    # GOALKEEPER
    # ================================================================
    "goalkeeper": {
        "positions": {"Goalkeeper"},

        "baseline": {
            "Save Efficiency": lambda df: (
                df["Save_percentage"] - df["Xsave_percentage"]
            ),

            "Goals Prevented per Shot": lambda df: safe_div(
                df["Goals_saved_above_avg"], df["Shots_on_target_faced"]
            ),

            "Goals Prevented": lambda df: df["Goals_saved_above_avg"],

            "Passing Under Pressure": lambda df: (
                df["Passing_percentage_under_pressure"]
                * (df["Percentage_passes_under_pressure"] / 100)
            ),

            "Long Pass Accuracy": lambda df: (
                df["Long_ball_percentage"] * df["Successful_pass_length"]
            ),

            "Progressive Passing": lambda df: (
                df["Forward_pass_proportion"] * df["Successful_pass_length"]
            ),

            "Pass Accuracy": lambda df: df["Passing_percentage"],

            "Sweeper Range": lambda df: df["Gk_defesive_action_distance"],

            "Sweeper Actions": lambda df: df["Defensive_actions"],

            # renamed to match indices / invert / groups
            "Errors per 90": lambda df: safe_div(
                df.get("Errors", 0) + df.get("Turnovers", 0),
                df["Minutes"] / 90,
            ),
        },

        "indices": {
            "ShotStop_Index": {
                "Save Efficiency": 0.25,
                "Goals Prevented per Shot": 0.30,
                "Goals Prevented": 0.45,
            },
            "Distribution_Index": {
                "Passing Under Pressure": 0.20,
                "Long Pass Accuracy": 0.25,
                "Progressive Passing": 0.25,
                "Pass Accuracy": 0.30,
            },
            "Sweeper_Index": {
                "Sweeper Actions": 0.60,
                "Sweeper Range": 0.30,
                "Errors per 90": -0.10,
            },
        },

        "groups": {
            "Shot Stopping": [
                "Goals Prevented per Shot",
                "Save Efficiency",
                "Goals Prevented",
            ],
            "Distribution": [
                "Passing Under Pressure",
                "Long Pass Accuracy",
                "Progressive Passing",
                "Pass Accuracy",
            ],
            "Sweeping": [
                "Sweeper Actions",
                "Sweeper Range",
                "Errors per 90",
            ],
        },

        "weights": {
            "Shot Stopping": 0.55,
            "Distribution": 0.35,
            "Sweeping": 0.10,
        },

        "invert": {"Errors per 90"},

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

    # ================================================================
    # WINGER
    # ================================================================
    "winger": {
        "positions": {
            "Right Midfielder", "Right Winger", "Right Wing Back",
            "Left Midfielder", "Left Wing", "Left Wing Back", "Left Winger",
        },

        "baseline": {
            # BALL CARRIER
            # upgraded: net dribble performance (success – failures)
            "Dribble Success": lambda df: (
                df["Dribbles_successful_ctx"] - df["Failed_dribbles_ctx"]
            ),
            # combined carry volume * success * distance
            "Progressive Carries": lambda df: (
                df["Carries_ctx"]
                * (df["Successful_carries_percentage"] / 100)
                * df["Carry_length_ctx"]
            ),
            "Turnovers from Dribbles": lambda df: safe_div(
                df["Failed_dribbles_ctx"] + df["Dispossessed_ctx"],
                df["Minutes"] / 90
            ),

            # WIDE CREATOR
            "Open-Play Creativity": lambda df: (
                df["Op_xa_ctx"] + df["Op_key_passes_ctx"] * 0.1
            ),
            "Box Entry Passes": lambda df: (
                df["Op_passes_into_box_ctx"] + df["Passes_inside_box_ctx"]
            ),
            "Through Balls": lambda df: df["Through_balls_ctx"],
            "Crossing Impact": lambda df: (
                df["Crosses_completed_ctx"] * df["Crossing_percentage"]
            ),
            # new: xA – Assists → how much creativity isn't turning into assists
            "Expected Assist Differential": lambda df: (
                df["Op_xa_ctx"] - df["Assists_ctx"]
            ),

            # GOAL THREAT
            "Chance Quality": lambda df: df["Np_xg_per_shot"],
            "Shots": lambda df: df["Np_shots_ctx"],
            "Finishing Rate": lambda df: df["Goal_conversion"],
            "Touches in Box": lambda df: df["Touches_in_box_ctx"],
            "Finishing Efficiency": lambda df: (
                df["Np_goals_ctx"] - df["Np_xg_ctx"]
            ),

            # DEFENSIVE / PRESSING
            "Pressures": lambda df: df["Padj_pressures_ctx"],
            "Press Success": lambda df: safe_div(
                df["Successful_pressures_ctx"], df["Padj_pressures_ctx"]
            ),
            "Counterpresses": lambda df: df["Opp_half_counterpressures_ctx"],
            "Counterpress Success": lambda df: df["Successful_counterpressures_ctx"],
            "High Press Actions": lambda df: df["Opp_half_pressures_ctx"],
            "Dribbles Prevented": lambda df: df["Dribbles_faced_stopped_percentage"],
        },

        "indices": {
            "BallCarrier_Index": {
                # updated to use the upgraded dribble + carry metrics
                "Dribble Success": 0.40,
                "Progressive Carries": 0.40,
                "Turnovers from Dribbles": -0.20,
            },
            "WideCreator_Index": {
                "Open-Play Creativity": 0.30,
                "Box Entry Passes": 0.20,
                "Through Balls": 0.20,
                "Crossing Impact": 0.15,
                "Expected Assist Differential": 0.15,
            },
            "GoalThreat_Index": {
                "Chance Quality": 0.25,
                "Shots": 0.25,
                "Finishing Rate": 0.25,
                "Touches in Box": 0.15,
                "Finishing Efficiency": 0.10,
            },
            "DefensiveWinger_Index": {
                "Pressures": 0.25,
                "Press Success": 0.20,
                "Counterpresses": 0.20,
                "Counterpress Success": 0.15,
                "High Press Actions": 0.10,
                "Dribbles Prevented": 0.10,
            },
        },

        "groups": {
            "Ball Carrier": [
                "Dribble Success",
                "Progressive Carries",
                "Turnovers from Dribbles",
            ],
            "Wide Creator": [
                "Open-Play Creativity", "Box Entry Passes",
                "Through Balls", "Crossing Impact",
                "Expected Assist Differential",
            ],
            "Goal Threat": [
                "Chance Quality", "Shots", "Finishing Rate",
                "Touches in Box", "Finishing Efficiency",
            ],
            "Defensive Winger": [
                "Pressures", "Press Success",
                "Counterpresses", "Counterpress Success",
                "High Press Actions", "Dribbles Prevented",
            ],
        },

        "weights": {
            "Ball Carrier": 0.35,
            "Wide Creator": 0.25,
            "Goal Threat": 0.25,
            "Defensive Winger": 0.15,
        },

        "invert": {"Turnovers from Dribbles"},

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

    # ================================================================
    # CENTRAL MIDFIELDER
    # ================================================================
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
            "Tackle Success": lambda df: safe_div(
                df["Tackles_ctx"], df["Minutes"] / 90
            ),
            "Interceptions": lambda df: safe_div(
                df["Interceptions_ctx"], df["Minutes"] / 90
            ),
            "Adj Tackles": lambda df: df["Padj_tackles_ctx"],
            "Adj Interceptions": lambda df: df["Padj_interceptions_ctx"],
            "Dribbles Prevented": lambda df: df["Dribbles_faced_stopped_percentage"],
            "Recoveries": lambda df: df["Ball_recoveries_ctx"],

            # DEEP-LYING PLAYMAKER
            "Forward Passing": lambda df: (
                df["Forward_pass_proportion"] * df["Passing_percentage"]
            ),
            "Long Passing": lambda df: (
                df["Long_ball_percentage"] * df["Successful_pass_length"]
            ),
            "Build-Up Involvement": lambda df: df["Op_xgbuildup_ctx"],
            "xGChain Involvement": lambda df: df["Op_xgchain_ctx"],
            "Final Third Passes": lambda df: df["Op_last_3rd_passes_ctx"],

            # BOX TO BOX
            "Final Third Carries": lambda df: df["Pass_and_carry_last_3rd_ctx"],
            "Counterpresses": lambda df: df["Counterpressures_ctx"],
            "Carry Impact": lambda df: (
                df["Carries_ctx"] * df["Carry_length_ctx"]
            ),
            "Transition Defence": lambda df: df["Successful_counterpressures_ctx"],
            "Pressing Distance": lambda df: df["Pressing_distance"],

            # ATTACKING PLAYMAKER
            "Final Third Creativity": lambda df: (
                df["Op_key_passes_ctx"] + df["Op_xa_ctx"]
            ),
            "Through Balls": lambda df: df["Through_balls_ctx"],
            "Box Entry Passes": lambda df: (
                df["Op_passes_into_box_ctx"] + df["Passes_inside_box_ctx"]
            ),
            "Shot Assists": lambda df: df["Key_passes_ctx"],
            "Assists": lambda df: df["Assists_ctx"],
            # new: xA – Assists to capture under/over-assisting
            "Expected Assist Differential": lambda df: (
                df["Op_xa_ctx"] - df["Assists_ctx"]
            ),
        },

        "indices": {
            "BallWinner_Index": {
                "Tackle Success": 0.25,
                "Interceptions": 0.20,
                "Adj Tackles": 0.20,
                "Adj Interceptions": 0.15,
                "Recoveries": 0.10,
                "Dribbles Prevented": 0.10,
            },

            "DeepLyingPlaymaker_Index": {
                "Forward Passing": 0.25,
                "Long Passing": 0.20,
                "Build-Up Involvement": 0.25,
                "xGChain Involvement": 0.20,
                "Final Third Passes": 0.10,
            },

            "BoxToBox_Index": {
                "Final Third Carries": 0.25,
                "Counterpresses": 0.20,
                "Carry Impact": 0.20,
                "Transition Defence": 0.20,
                "Pressing Distance": 0.15,
            },

            "AttackingPlaymaker_Index": {
                "Final Third Creativity": 0.30,
                "Through Balls": 0.20,
                "Box Entry Passes": 0.20,
                "Shot Assists": 0.10,
                "Assists": 0.10,
                "Expected Assist Differential": 0.10,
            },
        },

        "groups": {
            "Ball Winner": [
                "Tackle Success", "Interceptions",
                "Adj Tackles", "Adj Interceptions",
                "Recoveries", "Dribbles Prevented",
            ],
            "Deep-Lying Playmaker": [
                "Forward Passing", "Long Passing",
                "Build-Up Involvement", "xGChain Involvement",
                "Final Third Passes",
            ],
            "Box-to-Box": [
                "Final Third Carries", "Counterpresses",
                "Carry Impact", "Transition Defence",
                "Pressing Distance",
            ],
            "Attacking Playmaker": [
                "Final Third Creativity", "Through Balls",
                "Box Entry Passes", "Shot Assists",
                "Assists", "Expected Assist Differential",
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

    # ================================================================
    # STRIKER
    # ================================================================
    "striker": {
        "positions": {
            "Centre Forward",
            "Left Centre Forward",
            "Right Centre Forward",
        },

        "baseline": {
            # FINISHER
            "Chance Quality": lambda df: df["Np_xg_per_shot"],
            "Shots": lambda df: df["Np_shots_ctx"],
            "Finishing Rate": lambda df: df["Goal_conversion"],
            "Finishing Efficiency": lambda df: (
                df["Np_goals_ctx"] - df["Np_xg_ctx"]
            ),
            "Shot Accuracy": lambda df: df["Shot_target_percentage"],

            # TARGET MAN
            "Aerial Success": lambda df: df["Aerial_percentage"],
            "Aerial Wins": lambda df: df["Aerial_won"],
            "Hold-Up Passing": lambda df: (
                df["Passing_percentage"] * df["Backward_pass_proportion"]
            ),
            "Touches in Box": lambda df: df["Touches_in_box_ctx"],
            "Layoffs": lambda df: df["Op_xgbuildup_per_possession_ctx"],

            # FALSE 9
            "Link-Up Play": lambda df: (
                df["Op_xa_ctx"] + df["Op_key_passes_ctx"] * 0.15
            ),
            "Through Balls": lambda df: df["Through_balls_ctx"],
            "Key Passes": lambda df: df["Key_passes_ctx"],
            "Box Entry Passes": lambda df: df["Op_passes_into_box_ctx"],
            "Set-Piece Key Passes": lambda df: df["Sp_key_passes"],
            # new: xA – Assists to capture creative under/overperformance
            "Expected Assist Differential": lambda df: (
                df["Op_xa_ctx"] - df["Assists_ctx"]
            ),

            # DEFENSIVE FORWARD
            "Pressures": lambda df: df["Padj_pressures_ctx"],
            "Press Success": lambda df: safe_div(
                df["Successful_pressures_ctx"], df["Padj_pressures_ctx"]
            ),
            "Counterpresses": lambda df: df["Counterpressures_ctx"],
            "High Press Actions": lambda df: df["Opp_half_pressures_ctx"],
            "Turnovers Won": lambda df: df["Turnovers_ctx"],
        },

        "indices": {
            "Finisher_Index": {
                "Chance Quality": 0.30,
                "Shots": 0.25,
                "Finishing Rate": 0.20,
                "Finishing Efficiency": 0.15,
                "Shot Accuracy": 0.10,
            },

            "TargetMan_Index": {
                "Aerial Success": 0.30,
                "Aerial Wins": 0.25,
                "Hold-Up Passing": 0.20,
                "Touches in Box": 0.15,
                "Layoffs": 0.10,
            },

            "False9_Index": {
                "Link-Up Play": 0.35,
                "Through Balls": 0.20,
                "Key Passes": 0.15,
                "Box Entry Passes": 0.15,
                "Set-Piece Key Passes": 0.05,
                "Expected Assist Differential": 0.10,
            },

            "DefensiveForward_Index": {
                "Pressures": 0.35,
                "Press Success": 0.25,
                "Counterpresses": 0.20,
                "High Press Actions": 0.15,
                "Turnovers Won": 0.05,
            },
        },

        "groups": {
            "Finisher": [
                "Chance Quality", "Shots", "Finishing Rate",
                "Finishing Efficiency", "Shot Accuracy",
            ],
            "Target Man": [
                "Aerial Success", "Aerial Wins",
                "Hold-Up Passing", "Touches in Box", "Layoffs",
            ],
            "False 9": [
                "Link-Up Play", "Through Balls",
                "Key Passes", "Box Entry Passes",
                "Set-Piece Key Passes", "Expected Assist Differential",
            ],
            "Defensive Forward": [
                "Pressures", "Press Success",
                "Counterpresses", "High Press Actions",
                "Turnovers Won",
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
