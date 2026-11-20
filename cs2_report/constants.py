"""Shared weapon groups, labels, and analysis thresholds."""

UTILITY_WEAPONS = [
    "flashbang",
    "hegrenade",
    "smokegrenade",
    "molotov",
    "incendiarygrenade",
    "decoy",
]

RIFLE_WEAPONS = [
    "weapon_ak47",
    "weapon_m4a1",
    "weapon_m4a1_silencer",
    "weapon_galilar",
    "weapon_famas",
    "weapon_sg556",
    "weapon_aug",
]
SNIPER_WEAPONS = ["weapon_awp", "weapon_ssg08"]
SMG_WEAPONS = [
    "weapon_mac10",
    "weapon_mp7",
    "weapon_mp9",
    "weapon_mp5sd",
    "weapon_ump45",
    "weapon_p90",
    "weapon_bizon",
]
PISTOL_WEAPONS = [
    "weapon_glock",
    "weapon_usp_silencer",
    "weapon_hkp2000",
    "weapon_p250",
    "weapon_fiveseven",
    "weapon_tec9",
    "weapon_cz75a",
    "weapon_deagle",
    "weapon_elite",
    "weapon_revolver",
]
FIVESEVEN_TEC9 = ["weapon_fiveseven", "weapon_tec9"]
DEAGLE_USP = ["weapon_deagle", "weapon_usp_silencer", "weapon_hkp2000"]

ANGULAR_LOOKBACK_TICKS = 5
ANGULAR_VELOCITY_THRESHOLD_DPS = 300.0
MOVEMENT_VELOCITY_THRESHOLD = 75

HITGROUP_BY_ID = {
    1: "head",
    2: "chest",
    3: "stomach",
    4: "left_arm",
    5: "right_arm",
    6: "left_leg",
    7: "right_leg",
}
BODY_PARTS = ["head", "chest", "stomach", "left_leg", "right_leg", "left_arm", "right_arm"]

WEAPON_CATEGORIES = {
    **{weapon.removeprefix("weapon_"): "Rifle" for weapon in RIFLE_WEAPONS},
    **{weapon.removeprefix("weapon_"): "SMG" for weapon in SMG_WEAPONS},
    **{weapon.removeprefix("weapon_"): "Pistol" for weapon in PISTOL_WEAPONS},
    **{weapon.removeprefix("weapon_"): "Sniper" for weapon in SNIPER_WEAPONS},
}
WEAPON_LABELS = {
    "ak47": "AK-47",
    "m4a1": "M4A1",
    "m4a1_silencer": "M4A1-S",
    "galilar": "Galil AR",
    "famas": "FAMAS",
    "sg556": "SG 553",
    "aug": "AUG",
    "mac10": "MAC-10",
    "mp7": "MP7",
    "mp9": "MP9",
    "mp5sd": "MP5-SD",
    "ump45": "UMP-45",
    "p90": "P90",
    "bizon": "PP-Bizon",
    "glock": "Glock-18",
    "usp_silencer": "USP-S",
    "hkp2000": "P2000",
    "p250": "P250",
    "fiveseven": "Five-SeveN",
    "tec9": "Tec-9",
    "cz75a": "CZ75-Auto",
    "deagle": "Desert Eagle",
    "elite": "Dual Berettas",
    "revolver": "R8 Revolver",
    "awp": "AWP",
    "ssg08": "SSG 08",
}

BODY_ANCHORS = {
    "head": (512, 148, 24, 35),
    "chest": (512, 380, 82, 65),
    "stomach": (512, 555, 58, 38),
    "left_arm": (700, 465, 32, 125),
    "right_arm": (324, 465, 32, 125),
    "left_leg": (650, 1050, 35, 165),
    "right_leg": (374, 1050, 35, 165),
}
