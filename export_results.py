"""Write the reproducible Project 2 visible-output JSON artifact."""

import json
from pathlib import Path

from project_results import build_final_output

OUTPUT_FILE = Path(__file__).resolve().parent / "docs" / "visible-output.json"


def main():
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(build_final_output(), indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
