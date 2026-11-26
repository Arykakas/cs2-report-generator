import unittest
from pathlib import Path
from string import Formatter

from cs2_report.localization import (
    DEFAULT_LOCALE,
    SUPPORTED_LOCALES,
    load_catalog,
    localized_report_stem,
    translate,
    translate_archetype,
)


class LocalizationCatalogTests(unittest.TestCase):
    def test_catalogs_have_identical_message_keys(self):
        catalogs = {locale: load_catalog(locale) for locale in SUPPORTED_LOCALES}
        english_keys = set(catalogs[DEFAULT_LOCALE])

        for catalog in catalogs.values():
            self.assertEqual(set(catalog), english_keys)

    def test_catalog_placeholders_match_english(self):
        catalogs = {locale: load_catalog(locale) for locale in SUPPORTED_LOCALES}
        english = catalogs[DEFAULT_LOCALE]
        formatter = Formatter()

        def fields(template):
            return {name for _, name, _, _ in formatter.parse(template) if name}

        for locale, catalog in catalogs.items():
            for key, source in english.items():
                self.assertEqual(fields(catalog[key]), fields(source), (locale, key))

    def test_translations_interpolate_values(self):
        self.assertIn("12.3", translate("da-DK", "app.file_loaded", size=12.3))
        self.assertIn("12.3", translate("ru-RU", "app.file_loaded", size=12.3))

    def test_unknown_locale_uses_english_fallback(self):
        self.assertEqual(
            translate("unsupported", "app.language"),
            translate("en", "app.language"),
        )

    def test_archetype_labels_are_localized(self):
        self.assertNotEqual(
            translate_archetype("da-DK", "The High-Octane Rusher"),
            "The High-Octane Rusher",
        )
        self.assertNotEqual(
            translate_archetype("ru-RU", "The High-Octane Rusher"),
            "The High-Octane Rusher",
        )

    def test_english_report_filenames_remain_compatible(self):
        self.assertEqual(localized_report_stem("match", "1.0", "en"), "match_report")
        self.assertEqual(localized_report_stem("match", "2.0", "en"), "match_report_2.0")
        self.assertEqual(localized_report_stem("match", "2.0", "ru-RU"), "match_report_2.0_ru-RU")


if __name__ == "__main__":
    unittest.main()
