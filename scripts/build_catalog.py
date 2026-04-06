import argparse
import json
from pathlib import Path


DEFAULT_CATALOG_URL = (
    "https://raw.githubusercontent.com/undertaker33/"
    "astrbot-android-plugin-market/main/catalog.json"
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_plugin_entries(plugins_dir: Path) -> list[dict]:
    entries: list[dict] = []
    for path in sorted(plugins_dir.glob("*.json")):
        entry = load_json(path)
        if entry.get("pluginId") != path.stem:
            raise ValueError(
                f"Plugin entry filename mismatch: {path.name} does not match "
                f"pluginId {entry.get('pluginId')!r}"
            )
        entries.append(entry)
    return entries


def compute_updated_at(entries: list[dict]) -> int:
    timestamps = [
        version.get("publishedAt", 0)
        for entry in entries
        for version in entry.get("versions", [])
        if isinstance(version.get("publishedAt", 0), int)
    ]
    return max(timestamps, default=0)


def build_catalog(repo_root: Path) -> dict:
    metadata = load_json(repo_root / "catalog.metadata.json")
    entries = load_plugin_entries(repo_root / "plugins")
    return {
        "sourceId": metadata["sourceId"],
        "title": metadata["title"],
        "catalogUrl": metadata.get("catalogUrl", DEFAULT_CATALOG_URL),
        "updatedAt": compute_updated_at(entries),
        "plugins": entries,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output", default="catalog.json")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = repo_root / output_path

    catalog = build_catalog(repo_root)
    output_path.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
