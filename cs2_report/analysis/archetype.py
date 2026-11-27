"""Deterministic player archetype scores and narrative templates."""

PERFORMANCE_BANDS = {
    "kd": (1.0, 1.5),
    "adr": (60.0, 80.0),
}


# Performance thresholds for coaching-oriented feedback
PERFORMANCE_THRESHOLDS = {
    "The High-Octane Rusher": {"adr": 75.0, "kd_ratio": 1.0},
    "The Patient Marksman": {"headshot_percentage": 20.0, "adr": 70.0},
    "The Tactical Anchor": {"adr": 65.0},
}

# Narrative Library for the Component-Based Narrative Engine
NARRATIVE_LIBRARY = {
    "The High-Octane Rusher": {
        "praise": [
            "You seek fights quickly and play with incredible initiative.",
            "Your proactive style keeps the pressure on the enemy team at all times.",
            "You have a natural instinct for finding and forcing engagements."
        ],
        "pivot": [
            "However, your aim can sometimes struggle to keep up with your speed during these fast-paced moments.",
            "While your aggression is high, it occasionally leads to less consistent kill shots.",
            "Your proactive style is great, but it requires even sharper precision to be truly dominant."
        ],
        "goal": [
            "Focus on 'trigger discipline': try to settle your crosshair for a split second before firing while maintaining your aggressive pace.",
            "Work on stabilizing your aim during high-speed entries to ensure those proactive plays result in kills.",
            "Practice keeping your eyes on the target slightly longer before committing to the shot."
        ]
    },
    "The Patient Marksman": {
        "praise": [
            "Your measured shots show impressive precision and control.",
            "You have a disciplined approach to taking engagements, ensuring high-quality shots.",
            "Your ability to stay calm and aim accurately is a major asset."
        ],
        "pivot": [
            "At times, this caution can lead to missed opportunities to take space early in the round.",
            "While your precision is top-tier, you could be more proactive in creating openings for your team.",
            "Sometimes waiting for the perfect shot means giving up ground that could have been taken earlier."
        ],
        "goal": [
            "Look for chances to take space and create earlier openings without sacrificing your careful aim.",
            "Practice 'aggressive positioning'—finding ways to move forward while still maintaining your precision.",
            "Try to initiate engagements slightly more frequently to balance your high-precision style."
        ]
    },
    "The Aggressive Marksman": {
        "praise": [
            "You combine proactive engagements with precise shot-making."
        ],
        "pivot": [
            "The next step is to keep that accuracy while choosing rounds in which your aggression creates impact."
        ],
        "goal": [
            "Practice fast entries with a settled crosshair and commit to the engagements that give your team space."
        ]
    },
    "The Tactical Anchor": {
        "praise": [
            "You provide a rock-solid foundation for your team's defense.",
            "Your ability to hold ground and manage utility is exceptional.",
            "You excel at maintaining structure during high-pressure situations."
        ],
        "pivot": [
            "While your defensive play is strong, you could occasionally look for more proactive ways to impact the game.",
            "Sometimes staying in a defensive posture can allow the enemy too much freedom of movement.",
            "Your role is vital, but finding moments to transition into an offensive threat will elevate your impact."
        ],
        "goal": [
            "Work on identifying 'windows of opportunity' to push forward when the enemy is out of position.",
            "Practice proactive utility usage to disrupt enemy movements before they reach your defensive line.",
            "Try to balance your defensive positioning with small, calculated pushes to keep the pressure high."
        ]
    },
    "The Versatile All-Rounder": {
        "praise": [
            "You adapt seamlessly to different situations and roles on the team.",
            "Your balanced approach allows you to contribute effectively in almost any scenario.",
            "You have a great sense of game flow and know when to step up."
        ],
        "pivot": [
            "While your versatility is a strength, finding a specific area of mastery can help you stand out more.",
            "Sometimes being a generalist can make it harder to dominate a single aspect of the game.",
            "You have many skills; focusing on one primary role might yield even greater results."
        ],
        "goal": [
            "Identify which part of your game feels most natural and try to specialize in that area for a few matches.",
            "Work on refining one specific skill—like entry-fragging or utility management—to become a specialist.",
            "Try to pick a primary role for the next few games and see how much more impact you can have by focusing."
        ]
    }
}

def calculate_player_scores(hits_data: dict, aim_data: dict, flashes_data: dict, positioning_data: dict) -> dict:
    """Calculates normalized scores and raw components for aggression, precision, utility, and positioning based on Report 2.0 definitions."""
    positioning_data = positioning_data or {}

    # --- Aggression Score ---
    # Formula: (Opening Engagements / Rounds Played) * 100
    opening_engagements = positioning_data.get("opening_engagements", 0)
    rounds_played = max(1, int(positioning_data.get("rounds_played", 1)))
    aggression = min(100.0, (opening_engagements / rounds_played) * 100)

    # --- Precision Score ---
    # Formula: Headshot Percentage
    headshot_percentage = max(0.0, min(100.0, float(hits_data.get("headshot_percentage", 0))))
    precision = headshot_percentage
    # Sample Rule Check (20 shots)
    is_low_confidence = hits_data.get("count", 100) < 20

    # --- Utility Score ---
    # Formula: (Flash Success Rate * 0.6) + (Normalized Utility Damage * 0.4)
    flash_success_rate = max(0.0, min(1.0, float(flashes_data.get("flashbang_success_rate", 0))))
    # Normalized Utility Damage: we assume 'utility_damage' is pre-calculated in the pipeline
    utility_damage = positioning_data.get("utility_damage", 0) # Assume normalized to a max value
    utility = (flash_success_rate * 60.0) + (min(100.0, utility_damage) * 0.4)

    # --- Positioning Score ---
    # Formula: (100 - Rifle Moving Percentage) * 0.6 + (100 - Utility Death Rate) * 0.4
    rifle_moving_pct = max(0.0, min(100.0, float(positioning_data.get("rifle_moving_percentage", 0))))
    utility_death_rate = min(100.0, (max(0, int(positioning_data.get("utility_deaths", 0))) / rounds_played) * 100)
    positioning = ((100 - rifle_moving_pct) * 0.6) + ((100 - utility_death_rate) * 0.4)

    return {
        "aggression": round(aggression, 1),
        "precision": round(precision, 1),
        "utility": round(utility, 1),
        "positioning": round(positioning, 1),
        "headshot_percentage": headshot_percentage,
        "flash_success_rate": flash_success_rate,
        "rifle_moving_percentage": rifle_moving_pct,
        "utility_death_rate_per_round": utility_death_rate,
        "is_low_confidence": is_low_confidence
    }


def select_side_comparison(ct_values: list[float], t_values: list[float], minimum_side_samples: int = 3) -> dict:
    """Prefer sufficient CT/T samples; otherwise fall back to pooled match values."""
    ct_eligible = [value for value in ct_values if value is not None]
    t_eligible = [value for value in t_values if value is not None]
    side_eligible = (
        len(ct_eligible) >= minimum_side_samples
        and len(t_eligible) >= minimum_side_samples
    )
    if side_eligible:
        return {
            "mode": "side-aware",
            "ct": ct_eligible,
            "t": t_eligible,
            "pooled": ct_eligible + t_eligible,
        }
    return {
        "mode": "pooled",
        "ct": ct_eligible,
        "t": t_eligible,
        "pooled": ct_eligible + t_eligible,
    }


def calculate_tie_aware_ranks(values: list[float], higher_is_better: bool = True) -> dict:
    """Return dense ranks, relative scores, and leader flags without order-dependent ties."""
    eligible = [float(value) for value in values if value is not None]
    if not eligible:
        return {
            "ranks": {},
            "relative_scores": {},
            "leader_flags": {},
            "tied_leaders": set(),
        }

    unique_values = sorted(set(eligible), reverse=higher_is_better)
    rank_by_value = {
        value: index + 1
        for index, value in enumerate(unique_values)
    }
    ranks = rank_by_value
    leader_value = unique_values[0]
    leader_count = eligible.count(leader_value)

    if len(unique_values) == 1:
        relative_by_value = {leader_value: 100.0}
    else:
        relative_by_value = {
            value: 100.0 * (len(unique_values) - rank_by_value[value]) / (len(unique_values) - 1)
            for value in unique_values
        }

    return {
        "ranks": ranks,
        "relative_scores": relative_by_value,
        "leader_flags": {
            value: value == leader_value
            for value in unique_values
        },
        "tied_leaders": set(
            value for value in eligible if value == leader_value
        ) if leader_count > 1 else {leader_value},
    }


def select_archetype(scores: dict) -> dict:
    """Select an archetype from relative trait combinations and tied distinctions."""
    availability = scores.get("availability", {})
    if not availability.get("eligible", True):
        return {
            "archetype": "Insufficient Data",
            "primary_traits": [],
            "tied_distinctions": [],
        }

    aggression = float(scores.get("aggression", 0))
    precision = float(scores.get("precision", 0))
    utility = float(scores.get("utility", 0))
    positioning = float(scores.get("positioning", 0))

    tied_distinctions = []
    for trait, label in (
        ("aggression", "Aggression"),
        ("precision", "Precision"),
        ("utility", "Utility"),
        ("positioning", "Positioning"),
    ):
        if scores.get(f"{trait}_is_tied_leader"):
            tied_distinctions.append(label)

    if aggression >= 75 and precision >= 75:
        archetype = "The Aggressive Marksman"
    elif aggression >= 75:
        archetype = "The High-Octane Rusher"
    elif precision >= 75:
        archetype = "The Patient Marksman"
    elif utility >= 75 and positioning >= 75:
        archetype = "The Tactical Anchor"
    elif positioning >= 75:
        archetype = "The Disciplined Anchor"
    else:
        archetype = "The Versatile All-Rounder"

    return {
        "archetype": archetype,
        "primary_traits": tied_distinctions,
        "tied_distinctions": tied_distinctions,
    }


def normalize_narrative_stats(player_stats: dict) -> dict:
    """Derive required narrative inputs without defaulting missing values to zero."""
    if player_stats is None:
        raise ValueError("Player stats are required for narrative generation")

    required = ("kills", "deaths", "adr")
    missing = [key for key in required if key not in player_stats or player_stats[key] is None]
    if missing:
        return {
            "available": False,
            "missing": missing,
            "kd_ratio": None,
            "adr": None,
            "kd_band": "unavailable",
            "adr_band": "unavailable",
        }

    kills = float(player_stats["kills"])
    deaths = float(player_stats["deaths"])
    adr = float(player_stats["adr"])
    kd_ratio = kills / deaths if deaths else kills

    kd_band = "low" if kd_ratio < PERFORMANCE_BANDS["kd"][0] else (
        "steady" if kd_ratio <= PERFORMANCE_BANDS["kd"][1] else "high"
    )
    adr_band = "low" if adr < PERFORMANCE_BANDS["adr"][0] else (
        "steady" if adr <= PERFORMANCE_BANDS["adr"][1] else "high"
    )

    return {
        "available": True,
        "missing": [],
        "kd_ratio": kd_ratio,
        "adr": adr,
        "kd_band": kd_band,
        "adr_band": adr_band,
    }


def generate_narrative(archetype: str, scores: dict, player_stats: dict) -> str:
    """Assembles the narrative components into a cohesive coaching summary with performance-aware feedback."""
    if archetype == "Insufficient Data":
        return "The playstyle cannot be stated confidently because this player has insufficient rounds or shots. Collect more match data before assigning an archetype."

    normalized = normalize_narrative_stats(player_stats)
    if not normalized["available"]:
        missing = ", ".join(normalized["missing"])
        return f"Playstyle: {archetype}. Performance context is unavailable because required stats are missing: {missing}."

    library = NARRATIVE_LIBRARY.get(archetype, NARRATIVE_LIBRARY["The Versatile All-Rounder"])
    praise = library["praise"][0]
    pivot = library["pivot"][0]
    goal = library["goal"][0]

    kd_ratio = normalized["kd_ratio"]
    adr = normalized["adr"]
    kd_band = normalized["kd_band"]
    adr_band = normalized["adr_band"]

    if kd_band == "low" or adr_band == "low":
        performance = (
            f"Low impact needs direct correction: K/D is {kd_ratio:.2f} and ADR is {adr:.1f}. "
        )
        goal = f"Correct that result first: {goal}"
    elif kd_band == "high" and adr_band == "high":
        performance = (
            f"This playstyle delivered strong impact: K/D is {kd_ratio:.2f} and ADR is {adr:.1f}. "
        )
    else:
        performance = (
            f"This playstyle produced steady impact: K/D is {kd_ratio:.2f} and ADR is {adr:.1f}. "
        )

    return f"Playstyle: {archetype}. {praise} {performance}{pivot} {goal}"

def build_archetype_result(relative_scores: dict, player_stats: dict) -> dict:
    """Build the canonical Report 2.0 archetype and narrative result."""
    archetype_selection = select_archetype(relative_scores)
    archetype = archetype_selection["archetype"]

    if archetype == "The High-Octane Rusher":
        primary_trait = "Aggression"
        opportunity = "Trigger Discipline"
    elif archetype == "The Patient Marksman":
        primary_trait = "Precision"
        opportunity = "Positioning Variety"
    elif archetype == "The Tactical Anchor":
        primary_trait = "Utility"
        opportunity = "Aggression Timing"
    elif archetype == "The Disciplined Anchor":
        primary_trait = "Positioning"
        opportunity = "Space Taking"
    elif archetype == "The Aggressive Marksman":
        primary_trait = "Aggression + Precision"
        opportunity = "Round Impact"
    elif archetype == "Insufficient Data":
        primary_trait = "Insufficient Data"
        opportunity = "Collect more rounds and shots"
    else:
        primary_trait = "Balance"
        opportunity = "Specialization"

    primary_trait_key = {
        "Aggression": "aggression",
        "Precision": "precision",
        "Utility": "utility",
        "Positioning": "positioning",
        "Aggression + Precision": "aggression",
    }.get(primary_trait)
    is_primary = (
        primary_trait_key is not None
        and relative_scores.get(primary_trait_key, 0) >= 95
    )

    return {
        "archetype": archetype,
        "primary_traits": archetype_selection["primary_traits"],
        "tied_distinctions": archetype_selection["tied_distinctions"],
        "scores": relative_scores,
        "primary_trait": primary_trait,
        "is_primary": is_primary,
        "summary": generate_narrative(archetype, relative_scores, player_stats),
        "opportunity": opportunity,
    }


def analyze_archetype(
    hits_data: dict,
    aim_data: dict,
    flashes_data: dict,
    positioning_data: dict | None = None,
    player_stats: dict = None,
) -> dict:
    """Score four match traits and build a structured coaching summary."""
    positioning_data = positioning_data or {}
    scores = calculate_player_scores(hits_data, aim_data, flashes_data, positioning_data)

    aggression = scores["aggression"]
    precision = scores["precision"]
    utility = scores["utility"]
    positioning = scores["positioning"]

    # Archetype Selection Logic - Refined for better distribution
    if aggression >= 70 and precision < 80:
        archetype = "The High-Octane Rusher"
    elif precision >= 70 and aggression < 70:
        archetype = "The Patient Marksman"
    elif utility >= 80:
        # Prioritize Tactical Anchor if utility is high, even if positioning is also good
        archetype = "The Tactical Anchor"
    elif positioning >= 85 and aggression < 65:
        # Use Tactical Anchor for high positioning/low aggression as well
        archetype = "The Tactical Anchor"
    else:
        archetype = "The Versatile All-Rounder"

    # Use the new Narrative Engine
    summary = generate_narrative(archetype, scores, player_stats or {})

    return {
        "archetype": archetype,
        "scores": scores,
        "summary": summary,
        "primary_trait": "Aggression" if archetype == "The High-Octane Rusher" else \
                         "Precision" if archetype == "The Patient Marksman" else \
                         "Utility" if archetype == "The Tactical Anchor" else \
                         "Balance",
        "opportunity": "Click Discipline" if archetype == "The High-Octane Rusher" else \
                       "Positioning Variety" if archetype == "The Patient Marksman" else \
                       "Aggression Timing" if archetype == "The Tactical Anchor" else \
                       "Specialization",
        "score_basis": {
            "headshot_percentage": scores["headshot_percentage"],
            "flash_success_rate": scores["flash_success_rate"],
            "rifle_moving_percentage": scores["rifle_moving_percentage"],
            "utility_death_rate_per_round": scores["utility_death_rate_per_round"],
        },
    }
