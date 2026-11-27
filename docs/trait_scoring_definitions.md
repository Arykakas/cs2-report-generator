# Trait Scoring Definitions - Report 2.0 Module 1

This document defines the canonical scoring formulas, units, and rules for the four primary player traits used in Report 2.0.

## General Rules
- **Comparison Group:** Teammates only (side-aware: CT vs CT, T vs T).
- **Sample Requirements:** Players must have >=3 rounds and >=10 shots to be included in rankings.
- **Missing Data:** Missing data should not result in a zero score; it should be flagged as "Insufficient Data" or "Neutral".

## 1. Aggression
**Definition**: Measures how quickly and frequently a player initiates fights.
- **Source Data**: `demo.shots`, `demo.kills`.
- **Formula**: `(Opening Engagements / Rounds Played) * 100`
    - An "Opening Engagement" is defined as the first shot or kill recorded for a player in any given round.
- **Early Engagement Flag**: An engagement is "early" if $TTE < 30$ seconds OR $TTE < \text{Average Teammate TTE}$.
- **Sample Rule**: Minimum of 5 rounds played to produce a valid score.
- **Missing Data Fallback**: If no shots are recorded, score = "Neutral".
- **Unit**: Percentage (0-100).

## 2. Precision
**Definition**: Measures demonstrated accuracy and aim quality.
- **Source Data**: `demo.stats` (headshot_percentage), fallback to `demo.kills` (hitgroup).
- **Formula**: `Headshot Percentage`
    - Calculated as: `(Total Headshots / Total Shots) * 100`.
- **Sample Rule**: Minimum of 20 shots required for a high-confidence score. If < 20, the score is flagged as "Low Confidence".
- **Missing Data Fallback**: If no shots are recorded, score = "Neutral".
- **Unit**: Percentage (0-100).

## 3. Utility
**Definition**: Measures effective use of utility (Flashes, HE, Molotovs/Incendiaries).
- **Source Data**: `demo.grenades`, `demo.blinds`, `demo.damages`.
- **Formula**: `(Flash Success Rate * 0.6) + (Normalized Utility Damage * 0.4)`
    - **Flash Success Rate**: `(Flashes blinding at least one enemy / Total Flash Throws)`.
        - Correlation: Match `demo.blinds` with `demo.grenades` within a $\le$2 tick window.
    - **Normalized Utility Damage**: `(Total HE/Molotov Damage / Max Possible Damage per round)`.
        - Filter `demo.damages` for weapon types: `weapon_hegrenade`, `weapon_molotov`, `weapon_incendiary`.
- **Sample Rule**: Minimum of 2 utility throws required.
- **Missing Data Fallback**: If no utility is thrown, score = "Neutral".
- **Unit**: Percentage (0-100).

## 4. Positioning
**Definition**: Measures movement discipline and spatial awareness.
- **Source Data**: `demo.shots`, `demo.kills`.
- **Formula**: `(100 - Rifle Moving Percentage) * 0.6 + (100 - Utility Death Rate) * 0.4`
    - **Rifle Moving Percentage**: Percentage of shots fired while the player's velocity exceeds a specific threshold (e.g., > 500 units/tick).
    - **Utility Death Rate**: `(Deaths while holding utility / Rounds Played) * 100`.
- **Sample Rule**: Minimum of 3 rounds played.
- **Missing Data Fallback**: If no shots are recorded, score = "Neutral".
- **Unit**: Percentage (0-100).

## Scoring Summary Table

| Trait | Primary Metric | Weighting | Min Sample | Fallback |
|-------|----------------|-----------|-----------|----------|
| Aggression | Opening Engagements | 100% | 5 Rounds | Neutral |
| Precision | Headshot % | 100% | 20 Shots | Neutral |
| Utility | Flash + Damage | 60/40 | 2 Throws | Neutral |
| Positioning | Movement + Deaths | 60/40 | 3 Rounds | Neutral |
