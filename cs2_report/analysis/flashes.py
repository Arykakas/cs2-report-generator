"""Flash throw and blindness summaries."""

import polars as pl


def analyze_flashes(demo, player_steamid: int) -> dict:
    """Associate blindness events with the player's flash projectiles."""
    flash_grenades = (
        demo.grenades.filter(
            (pl.col("thrower_steamid") == player_steamid)
            & (pl.col("type") == "flashbang")
        )
        .select("thrower_steamid", "entity_id", "entity_serial", "end_tick")
        .unique()
        .to_dicts()
    )
    player_blinds = demo.blinds.filter(
        pl.col("attacker_steamid") == player_steamid
    ).to_dicts()
    blind_victims_by_flash = {
        (grenade["entity_id"], grenade["entity_serial"]): []
        for grenade in flash_grenades
    }
    for blind in player_blinds:
        nearest_flash = min(
            flash_grenades,
            key=lambda grenade: abs(blind["tick"] - grenade["end_tick"]),
            default=None,
        )
        if nearest_flash and abs(blind["tick"] - nearest_flash["end_tick"]) <= 2:
            blind_victims_by_flash[
                (nearest_flash["entity_id"], nearest_flash["entity_serial"])
            ].append(blind)

    flash_count = len(flash_grenades)
    enemy_blinds = sum(
        blind["attacker_side"] != blind["victim_side"] for blind in player_blinds
    )
    teammate_blinds = sum(
        blind["attacker_side"] == blind["victim_side"]
        and blind["victim_steamid"] != player_steamid
        for blind in player_blinds
    )
    self_blinds = sum(
        blind["victim_steamid"] == player_steamid for blind in player_blinds
    )
    teammate_only_flashes = sum(
        any(
            victim["victim_steamid"] != player_steamid
            and victim["attacker_side"] == victim["victim_side"]
            for victim in victims
        )
        and not any(victim["attacker_side"] != victim["victim_side"] for victim in victims)
        for victims in blind_victims_by_flash.values()
    )
    flashes_blinding_no_one = sum(not victims for victims in blind_victims_by_flash.values())
    flash_teammate_or_self_count = sum(
        any(
            victim["victim_steamid"] == player_steamid
            or victim["attacker_side"] == victim["victim_side"]
            for victim in victims
        )
        for victims in blind_victims_by_flash.values()
    )

    flash_details = []
    for grenade in flash_grenades:
        victims = blind_victims_by_flash[
            (grenade["entity_id"], grenade["entity_serial"])
        ]
        enemies = sum(v["attacker_side"] != v["victim_side"] for v in victims)
        teammates = sum(
            v["attacker_side"] == v["victim_side"]
            and v["victim_steamid"] != player_steamid
            for v in victims
        )
        self_count = sum(v["victim_steamid"] == player_steamid for v in victims)
        if not victims:
            result = "blinded no one"
        elif not enemies and teammates:
            result = "teammates only"
        elif enemies:
            result = "enemy blinded"
        else:
            result = "self-blind only"
        flash_details.append(
            {
                "detonation_tick": grenade["end_tick"],
                "enemies": enemies,
                "teammates": teammates,
                "self": self_count,
                "result": result,
            }
        )

    return {
        "flash_grenades": flash_grenades,
        "player_blinds": player_blinds,
        "flash_count": flash_count,
        "enemy_blinds": enemy_blinds,
        "teammate_blinds": teammate_blinds,
        "self_blinds": self_blinds,
        "teammate_only_flashes": teammate_only_flashes,
        "flashes_blinding_no_one": flashes_blinding_no_one,
        "flash_teammate_or_self_count": flash_teammate_or_self_count,
        "flash_details": flash_details,
    }
