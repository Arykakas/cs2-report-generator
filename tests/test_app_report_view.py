import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import streamlit as st
from streamlit.testing.v1 import AppTest

from cs2_report.localization import SUPPORTED_LOCALES, localized_report_stem, translate


class InlineReportViewTests(unittest.TestCase):
    def setUp(self):
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        self.app = AppTest.from_file(str(app_path), default_timeout=20)
        self.app.session_state["report_result"] = {
            "html_reports": {
                "1.0": "<html><body>Report 1.0</body></html>",
                "2.0": "<html><body>Report 2.0</body></html>",
            },
            "file_names": {
                "1.0": "match_report.html",
                "2.0": "match_report_2.0.html",
            },
            "player_name": "khorosiya",
            "demo_name": "test.dem",
        }
        self.app.run()

    def test_report_2_is_inline_by_default_with_one_download_action(self):
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.segmented_control[0].value, "2.0")
        self.assertEqual(len(self.app.get("iframe")), 1)
        self.assertEqual(
            [button.label for button in self.app.get("download_button")],
            ["Download report"],
        )

    def test_language_change_localizes_labels_and_clears_stale_report(self):
        self.app.session_state["player_options"] = {"123": "Player"}
        self.app.selectbox(key="report_locale").select("da-DK").run()

        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.session_state["report_locale"], "da-DK")
        self.assertEqual(self.app.session_state["player_options"], {"123": "Player"})
        self.assertFalse(self.app.get("iframe"))
        self.assertEqual(
            self.app.button(key="generate_report").label,
            translate("da-DK", "app.button.generate"),
        )
        self.app.run()
        self.assertEqual(self.app.selectbox(key="report_locale").value, "da-DK")

    def test_uploaded_demo_shows_localized_player_heading(self):
        self.app.session_state["player_options"] = {"123": "Player"}
        upload = SimpleNamespace(name="test.dem", size=1024)
        with patch("streamlit.file_uploader", return_value=upload):
            for locale in ("en", "da-DK", "ru-RU"):
                with self.subTest(locale=locale):
                    self.app.selectbox(key="report_locale").select(locale).run()
                    self.assertFalse(self.app.exception)
                    self.assertEqual(self.app.selectbox(key="selected_player").value, "123")
                    self.assertIn(
                        f'<p class="upload-step">{translate(locale, "app.step_player")}</p>',
                        [element.value for element in self.app.markdown],
                    )

    def test_preview_and_download_share_localized_report(self):
        for locale in SUPPORTED_LOCALES:
            self.app.selectbox(key="report_locale").select(locale).run()
            html_reports = {
                version: f'<html lang="{locale}"><body>Report {version}</body></html>'
                for version in ("1.0", "2.0")
            }
            filenames = {
                version: f"{localized_report_stem('match', version, locale)}.html"
                for version in html_reports
            }
            self.app.session_state["report_result"] = {
                "html_reports": html_reports,
                "file_names": filenames,
                "player_name": "Player",
                "demo_name": "match.dem",
            }
            self.app.run()
            for version in html_reports:
                with self.subTest(locale=locale, version=version):
                    with (
                        patch("streamlit.iframe", wraps=st.iframe) as preview,
                        patch("streamlit.download_button", wraps=st.download_button) as download,
                    ):
                        self.app.segmented_control[0].set_value(version).run()
                    self.assertFalse(self.app.exception)
                    preview.assert_called_once()
                    download.assert_called_once()
                    self.assertEqual(preview.call_args.args[0], html_reports[version])
                    self.assertEqual(download.call_args.kwargs["data"], html_reports[version])
                    self.assertEqual(download.call_args.kwargs["file_name"], filenames[version])
                    self.assertEqual(
                        download.call_args.args[0], translate(locale, "app.report.download")
                    )

    def test_version_switch_keeps_report_and_download_available(self):
        self.app.segmented_control[0].set_value("1.0").run()

        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.segmented_control[0].value, "1.0")
        self.assertEqual(len(self.app.get("iframe")), 1)
        self.assertEqual(
            [button.label for button in self.app.get("download_button")],
            ["Download report"],
        )


if __name__ == "__main__":
    unittest.main()