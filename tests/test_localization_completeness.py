import unittest
from string import Formatter

from cs2_report.localization import DEFAULT_LOCALE, SUPPORTED_LOCALES, load_catalog


class TestLocalizationCompleteness(unittest.TestCase):
    def test_catalogs_contain_all_keys(self):
        english = load_catalog(DEFAULT_LOCALE)
        for locale in SUPPORTED_LOCALES:
            with self.subTest(locale=locale):
                catalog = load_catalog(locale)
                self.assertEqual(catalog.keys(), english.keys())
                self.assertFalse([key for key, value in catalog.items() if not value.strip()])

    def test_interpolation_placeholders(self):
        def fields(template):
            return sorted(
                (name, format_spec, conversion or "")
                for _, name, format_spec, conversion in Formatter().parse(template)
                if name is not None
            )

        english = load_catalog(DEFAULT_LOCALE)
        for locale in SUPPORTED_LOCALES:
            if locale == DEFAULT_LOCALE:
                continue
            catalog = load_catalog(locale)
            for key, template in english.items():
                with self.subTest(locale=locale, key=key):
                    self.assertEqual(fields(catalog[key]), fields(template))


if __name__ == "__main__":
    unittest.main()
