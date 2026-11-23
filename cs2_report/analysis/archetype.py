"""Deterministic player archetype scores and narrative templates."""
import random

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
    """Calculates normalized scores and raw components for aggression, precision, utility, and positioning."""
    positioning_data = positioning_data or {}
    panic_count = len(aim_data.get("shots_before_crosshair_settles", []))
    average_deviation = aim_data.get("average_kill_deviation")
    norm_deviation = max(0.0, 1.0 - (float(average_deviation or 0) / 30.0))
    aggression = min(100.0, (panic_count / 15.0) * 80 + norm_deviation * 20)

    headshot_percentage = max(0.0, min(100.0, float(hits_data.get("headshot_percentage", 0))))
    precision = min(100.0, headshot_percentage + (norm_deviation * 60))

    flash_success_rate = max(0.0, min(1.0, float(flashes_data.get("flashbang_success_rate", 0))))
    utility = flash_success_rate * 100

    rifle_moving_percentage = max(
        0.0, min(100.0, float(positioning_data.get("rifle_moving_percentage", 0)))
    )
    rounds_played = max(1, int(positioning_data.get("rounds_played", 1)))
    val = positioning_data.get("utility_deaths", 0)
    utility_deaths = max(0, int(val))
    utility_death_rate = min(100.0, utility_deaths / rounds_played * 100)
    positioning = (100 - rifle_moving_percentage) * 0.6 + (100 - utility_death_rate) * 0.4

    return {
        "aggression": round(aggression, 1),
        "precision": round(precision, 1),
        "utility": round(utility, 1),
        "positioning": round(positioning, 1),
        "headshot_percentage": headshot_percentage,
        "flash_success_rate": flash_success_rate,
        "rifle_moving_percentage": rifle_moving_percentage,
        "utility_death_rate_per_round": utility_death_rate,
    }


def generate_narrative(archetype: str, scores: dict, player_stats: dict) -> str:
    """Assembles the narrative components into a cohesive coaching summary with performance-aware feedback."""
    library = NARRATIVE_LIBRARY.get(archetype, NARRATIVE_LIBRARY["The Versatile All-Rounder"])

    # Check for performance gaps based on archetype thresholds
    performance_feedback = ""
    if archetype in PERFORMANCE_THRESHOLDS:
        thresholds = PERFORMANCE_THRESHOLDS[archetype]
        for metric, target in thresholds.items():
            actual = float(player_stats.get(metric, 0))
            if actual < target:
                performance_feedback = f"To truly excel as {archetype}, focus on improving your {metric} (Current: {actual:.1f}, Target: {target}). "
                break

    praise = random.choice(library["praise"])
    pivot = random.choice(library["pivot"])
    goal = random.choice(library["goal"])

    # Prepend performance feedback if it exists
    narrative_prefix = f"{performance_feedback}" if performance_feedback else ""
    return f"{narrative_prefix}{praise} {pivot} {goal}"

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
