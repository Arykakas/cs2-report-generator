import unittest
import json
import sys
import re
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(".").resolve()))

try:
    from cs2_report.localization import SUPPORTED_LOCALES
except ImportError:
    # Fallback if the package structure isn't recognized in this environment
    SUPPORTED_LOCALES = ("en", "da-DK", "ru-RU")

class TestLocalizationCompleteness(unittest.TestCase):
    def setUp(self):
        self.locales_dir = Path("cs2_report/locales")
        self.base_path = self.locales_dir / "en.json"
        with open(self.base_path, 'r', encoding='utf-8') as f:
            self.base_cat = json.load(f)

    def test_catalogs_contain_all_keys(self):
        """Verify that all keys in the English catalog exist in other supported locales."""
        for locale in SUPPORTED_LOCALES:
            if locale == "en":
                continue
            
            path = self.locales_dir / f"{locale}.json"
            with open(path, 'r', encoding='utf-8') as f:
                target_cat = json.load(f)
            
            for key in self.base_cat:
                with self.subTest(locale=locale, key=key):
                    self.assertIn(key, target_cat, f"Key '{key}' is missing from {locale} catalog.")

    def test_interpolation_placeholders(self):
        """Verify that placeholders in English are consistently present in other locales."""
        for locale in SUPPORTED_LOCALES:
            if locale == "en":
                continue
            
            path = self.locales_dir / f"{locale}.json"
            with open(path, 'r', encoding='utf-8') as f:
                target_cat = json.load(f)
            
            for key, en_value in self.base_cat.items():
                if key in target_cat:
                    en_ph = set(re.findall(r'\{(\w+)\}', en_value))
                    ru_ph = set(re.findall(r'\{(\w+)\}', target_cat[key]))
                    self.assertEqual(en_ph, ru_ph, f"Placeholder mismatch for key '{key}' in {locale}.")

if __name__ == "__main__":
    unittest.main()
