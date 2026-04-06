import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class BuildCatalogTest(unittest.TestCase):
    def test_builds_catalog_from_plugin_entry_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            plugins_dir = repo_root / "plugins"
            plugins_dir.mkdir(parents=True, exist_ok=True)
            (repo_root / "catalog.metadata.json").write_text(
                json.dumps(
                    {
                        "sourceId": "undertaker33.astrbot.android.plugin.market",
                        "title": "AstrBot Android Plugin Market",
                        "catalogUrl": "https://raw.githubusercontent.com/undertaker33/astrbot-android-plugin-market/main/catalog.json",
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            entry = {
                "pluginId": "cc.astrbot.android.plugin.demo",
                "title": "Demo Plugin",
                "author": "tester",
                "description": "A demo plugin entry.",
                "entrySummary": "Demo summary.",
                "repoUrl": "https://github.com/example/demo-plugin",
                "scenarios": ["demo"],
                "versions": [
                    {
                        "version": "1.0.0",
                        "packageUrl": "https://github.com/example/demo-plugin/releases/download/v1/demo.zip",
                        "publishedAt": 1776000000000,
                        "protocolVersion": 1,
                        "minHostVersion": "0.4.0",
                        "maxHostVersion": "",
                        "permissions": [],
                        "changelog": "Initial release."
                    }
                ]
            }

            (plugins_dir / "cc.astrbot.android.plugin.demo.json").write_text(
                json.dumps(entry, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            output_path = repo_root / "catalog.json"
            subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve().parents[1] / "scripts" / "build_catalog.py"),
                    "--repo-root",
                    str(repo_root),
                    "--output",
                    str(output_path),
                ],
                check=True,
            )

            built = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(
                built["catalogUrl"],
                "https://raw.githubusercontent.com/undertaker33/astrbot-android-plugin-market/main/catalog.json",
            )
            self.assertEqual(built["updatedAt"], 1776000000000)
            self.assertEqual(len(built["plugins"]), 1)
            self.assertEqual(built["plugins"][0]["pluginId"], "cc.astrbot.android.plugin.demo")


if __name__ == "__main__":
    unittest.main()
