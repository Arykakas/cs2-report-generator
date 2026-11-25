"""Locale catalogs and shared helpers for localized app/report output."""

from functools import lru_cache
import json
from pathlib import Path

DEFAULT_LOCALE = "en"
SUPPORTED_LOCALES = ("en", "da-DK", "ru-RU")
LOCALE_NAMES = {
    "en": "English",
    "da-DK": "Dansk",
    "ru-RU": "Русский",
}

_ARCHETYPE_KEYS = {
    "The High-Octane Rusher": "archetype.rusher",
    "The Patient Marksman": "archetype.patient_marksman",
    "The Aggressive Marksman": "archetype.aggressive_marksman",
    "The Tactical Anchor": "archetype.tactical_anchor",
    "The Disciplined Anchor": "archetype.disciplined_anchor",
    "The Versatile All-Rounder": "archetype.all_rounder",
    "Insufficient Data": "archetype.insufficient_data",
}


@lru_cache(maxsize=len(SUPPORTED_LOCALES))
def load_catalog(locale: str) -> dict[str, str]:
    """Load one flat UTF-8 JSON message catalog."""
    if locale not in SUPPORTED_LOCALES:
        raise ValueError(f"Unsupported locale: {locale}")
    path = Path(__file__).with_name("locales") / f"{locale}.json"
    with path.open(encoding="utf-8") as catalog_file:
        catalog = json.load(catalog_file)
    if not isinstance(catalog, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in catalog.items()
    ):
        raise ValueError(f"Invalid localization catalog: {path.name}")
    return catalog


def translate(locale: str, key: str, **values) -> str:
    """Translate a message, falling back to English for missing catalog keys."""
    if locale not in SUPPORTED_LOCALES:
        locale = DEFAULT_LOCALE
    english = load_catalog(DEFAULT_LOCALE)
    template = load_catalog(locale).get(key, english.get(key))
    if template is None:
        raise KeyError(f"Missing English localization key: {key}")
    return template.format_map(values) if values else template


def translate_archetype(locale: str, archetype: str) -> str:
    """Return the localized display label for a canonical English archetype."""
    key = _ARCHETYPE_KEYS.get(archetype)
    return translate(locale, key) if key else archetype


def localized_report_stem(demo_stem: str, version: str, locale: str) -> str:
    """Return the legacy English report stem or a locale-suffixed report stem."""
    if version not in {"1.0", "2.0"}:
        raise ValueError(f"Unsupported report version: {version}")
    version_suffix = "" if version == "1.0" else "_2.0"
    locale_suffix = "" if locale == DEFAULT_LOCALE else f"_{locale}"
    return f"{demo_stem}_report{version_suffix}{locale_suffix}"


def report_output_paths(demo_path: Path, version: str, locale: str) -> tuple[Path, Path]:
    """Return text and HTML output paths, preserving English filenames."""
    stem = localized_report_stem(demo_path.stem, version, locale)
    return (
        demo_path.with_name(f"{stem}.txt"),
        demo_path.with_name(f"{stem}.html"),
    )
