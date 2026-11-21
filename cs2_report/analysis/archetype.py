"""Deterministic player archetype scores and narrative templates."""


def analyze_archetype(
    hits_data: dict,
    aim_data: dict,
    flashes_data: dict,
    positioning_data: dict | None = None,
) -> dict:
    """Score four match traits and build a fixed-template coaching summary."""
    positioning_data = positioning_data or {}
    panic_count = len(aim_data.get("shots_before_crosshair_settles", []))
    average_deviation = aim_data.get("average_kill_deviation")
    norm_deviation = max(0.0, 1.0 - (float(average_deviation or 0) / 30.0))
    aggression = min(100.0, min(1.0, panic_count / 20.0) * 50 + norm_deviation * 50)

    headshot_percentage = max(0.0, min(100.0, float(hits_data.get("headshot_percentage", 0))))
    precision = headshot_percentage * 0.5 + norm_deviation * 50

    flash_success_rate = max(0.0, min(1.0, float(flashes_data.get("flashbang_success_rate", 0))))
    utility = flash_success_rate * 100

    rifle_moving_percentage = max(
        0.0, min(100.0, float(positioning_data.get("rifle_moving_percentage", 0)))
    )
    rounds_played = max(1, int(positioning_data.get("rounds_played", 1)))
    utility_deaths = max(0, int(positioning_data.get("utility_deaths", 0)))
    utility_death_rate = min(100.0, utility_deaths / rounds_played * 100)
    positioning = (100 - rifle_moving_percentage) * 0.6 + (100 - utility_death_rate) * 0.4

    if aggression >= 80 and precision < 65:
        archetype, primary_trait, opportunity = "The High-Octane Rusher", "Aggression", "Click Discipline"
        summary = (
            "You seek fights quickly and play with strong initiative. Your aim is less consistent during those fast engagements. "
            "Focus on click discipline: settle your crosshair before firing while keeping your proactive style."
        )
    elif precision >= 80 and aggression < 65:
        archetype, primary_trait, opportunity = "The Patient Marksman", "Precision", "Positioning Variety"
        summary = (
            "Your measured shots show strong precision. Look for chances to take space and create earlier openings "
            "without giving up that careful aim."
        )
    elif utility >= 70 and utility >= max(aggression, precision, positioning):
        archetype, primary_trait, opportunity = "The Tactical Anchor", "Utility", "Aggression Timing"
        summary = (
            "Your flashes are creating useful opportunities for the team. Pair that support with a clear plan "
            "for when to follow your utility into the fight."
        )
    elif positioning >= 80 and aggression < 65:
        archetype, primary_trait, opportunity = "The Disciplined Anchor", "Positioning", "Space Taking"
        summary = (
            "You show good movement discipline and avoid many utility deaths. Keep that consistency while looking "
            "for safe chances to take more space."
        )
    else:
        archetype, primary_trait, opportunity = "The Versatile All-Rounder", "Balance", "Specialization"
        summary = (
            "Your match shows a balanced mix of aim, movement, and utility. Pick the area with the clearest warning "
            "in this report and focus your next practice session there."
        )

    return {
        "archetype": archetype,
        "scores": {
            "aggression": round(aggression, 1),
            "precision": round(precision, 1),
            "utility": round(utility, 1),
            "positioning": round(positioning, 1),
        },
        "summary": summary,
        "primary_trait": primary_trait,
        "opportunity": opportunity,
        "score_basis": {
            "headshot_percentage": headshot_percentage,
            "flash_success_rate": flash_success_rate,
            "rifle_moving_percentage": rifle_moving_percentage,
            "utility_death_rate_per_round": utility_death_rate,
        },
    }
