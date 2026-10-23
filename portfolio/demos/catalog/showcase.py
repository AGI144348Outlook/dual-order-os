"""Synthetic, offline demonstration of the existing CatalogBox component."""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libraries"))
from catalog_box import CatalogBox


def main():
    with tempfile.TemporaryDirectory(prefix="catalog-showcase-") as directory:
        path = Path(directory) / "catalog.sqlite"
        with CatalogBox(path) as box:
            box.put_card("review-checklist", "Review checklist",
                         {"steps": ["Check source", "Approve draft"]})
            box.put_template("review-template", "Review workspace",
                             {"columns": ["source", "draft"]},
                             [{"id": "review-checklist"}])
            box.instantiate("review-template", "project-a")
            box.instantiate("review-template", "project-b")
            box.save_configuration("project-a",
                                   {"columns": ["source", "draft", "approval"]},
                                   expected_revision=1)
            box.put_card("review-checklist", "Updated review checklist",
                         {"steps": ["Check source", "Approve draft", "Record decision"]},
                         expected_revision=1)

        with CatalogBox(path) as box:
            first = box.get("configurations", "project-a")
            second = box.get("configurations", "project-b")
            pinned = box.resolve_cards("configurations", "project-a")[0]
            summary = {
                "synthetic_data": True,
                "project_a_columns": first["configuration"]["columns"],
                "project_b_columns": second["configuration"]["columns"],
                "project_a_original_columns": box.get("configurations", "project-a", 1)["configuration"]["columns"],
                "latest_checklist_revision": box.get("cards", "review-checklist")["revision"],
                "saved_project_checklist_revision": pinned["revision"],
                "reopened_from_disk": True,
                "model_calls": 0,
            }
            assert summary["project_a_columns"] == ["source", "draft", "approval"]
            assert summary["project_b_columns"] == ["source", "draft"]
            assert summary["project_a_original_columns"] == ["source", "draft"]
            assert summary["latest_checklist_revision"] == 2
            assert summary["saved_project_checklist_revision"] == 1
            print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
