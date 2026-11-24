# Task 1 Audit Findings - Report 2.0 Module 1

## Awpy Version and Schema Verification
- **Version**: 3.3.0 (Verified via `pip show awpy`)
- **Core Schemas Used**:
    - `demo.stats`: Contains `name`, `team`, `rounds_played`, `total_rounds`, `kills`, `deaths`, `adr`, `headshot_percentage`.
    - `demo.shots`: Contains `steamid`, `tick`, `x`, `y`, `z`, `yaw`, `pitch`, `weapon`.
    - `demo.kills`: Contains `attacker_steamid`, `victim_name`, `tick`, `victim_x`, `victim_y`, `victim_z`, `weapon`, `hitgroup`.
    - `demo.grenades`: Contains `thrower_steamid`, `type`, `entity_id`, `entity_serial`, `end_tick`.
    - `demo.blinds`: Contains `attacker_steamid`, `victim_steamid`, `tick`, `attacker_side`, `victim_side`.

## Reliable Fields for Context and Metrics
- **Team/Side**: `team` (from `stats`), `attacker_side`/`victim_side` (from `blinds`).
- **Round Participation**: `rounds_played` (from `stats`).
- **Opening Engagements**: Not directly in a single field; requires calculating first engagement tick from `shots` and comparing to round start.
- **Time to First Engagement**: Calculated by finding the first shot/kill tick relative to round start tick.

## Flash Blindness Duration
- **Availability**: The current `awpy` schema for `blinds` does not explicitly provide a "duration" field.
- **Workaround**: We are currently associating blinds with flash projectiles based on proximity in time (<= 2 ticks).
- **Limitation**: Precise duration data is unavailable; we must rely on the presence of a blind event within the window of a flash detonation.

## HE and Molotov/Incendiary Damage
- **Attribution**: `demo.damages` provides `attacker_steamid`, `victim_name`, `weapon`, and `damage`.
- **Double-Counting Prevention**: We must filter by `weapon` type (e.g., `weapon_hegrenade`) and ensure we only count damage from the specific utility event, not subsequent rifle damage in the same tick.

## Smoke Metrics
- **Current State**: No dedicated smoke "success" metric exists in the standard schema.
- **Measurable Data**: We can track smoke detonation (if available) or proximity of enemies to smoke coordinates over time.
- **Decision**: For now, we will focus on flash and utility damage as primary metrics until a reliable smoke-obscuration metric is verified.

## Data Gaps & Fallbacks
- **Missing Stats**: If `stats` for a player are missing, fallback to calculating basic K/D from the `kills` table.
- **Low Sample Size**: Players with <3 rounds or <10 shots will be excluded from teammate-relative ranking but included in the report as "Insufficient Data".
- **Flash Duration**: Fallback is binary (blinded vs not blinded) since duration is unavailable.
