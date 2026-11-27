import json
from cs2_report.analysis.archetype import analyze_archetype

def test_narrative():
    test_cases = [
        {
            "name": "High-Octane Rusher - Underperforming",
            "stats": {"kills": 8, "deaths": 10, "adr": 60.0, "headshot_percentage": 30.0, "rounds_played": 10},
            "hits": {"hit_model_data": {}, "headshot_percentage": 30.0},
            "aim": {"shots_before_crosshair_settles": [1]*16, "average_kill_deviation": 5.0},
            "flashes": {"flashbang_success_rate": 0.1}, # Low utility to avoid Tactical Anchor
            "positioning": {"rifle_moving_percentage": 30.0, "utility_deaths": 2, "rounds_played": 10}
        },
        {
            "name": "Patient Marksman - Underperforming",
            "stats": {"kills": 10, "deaths": 10, "adr": 60.0, "headshot_percentage": 15.0, "rounds_played": 10},
            "hits": {"hit_model_data": {}, "headshot_percentage": 15.0},
            "aim": {"shots_before_crosshair_settles": [1]*2, "average_kill_deviation": 2.0},
            "flashes": {"flashbang_success_rate": 0.1}, # Low utility to avoid Tactical Anchor
            "positioning": {"rifle_moving_percentage": 30.0, "utility_deaths": 2, "rounds_played": 10}
        },
        {
            "name": "Tactical Anchor - Underperforming",
            "stats": {"kills": 10, "deaths": 10, "adr": 50.0, "headshot_percentage": 20.0, "rounds_played": 10},
            "hits": {"hit_model_data": {}, "headshot_percentage": 20.0},
            "aim": {"shots_before_crosshair_settles": [1]*5, "average_kill_deviation": 15.0},
            "flashes": {"flashbang_success_rate": 0.95}, # High utility to ensure Tactical Anchor
            "positioning": {"rifle_moving_percentage": 30.0, "utility_deaths": 2, "rounds_played": 10}
        }
    ]

    for case in test_cases:
        print(f"--- Testing: {case['name']} ---")
        result = analyze_archetype(
            case["hits"],
            case["aim"],
            case["flashes"],
            positioning_data=case["positioning"],
            player_stats=case["stats"]
        )
        print(f"Archetype: {result['archetype']}")
        print(f"Summary: {result['summary']}")
        print("-" * 30)

if __name__ == "__main__":
    test_narrative()
