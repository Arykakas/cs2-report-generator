import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


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