from collections import Counter
from src.config import *
import argparse
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def get_ollama_endpoint():
    """
    Automatically detects the Ollama endpoint based on the environment.
    """
    env_url = os.getenv("OLLAMA_HOST")
    if env_url:
        return env_url

    if os.path.exists('/.dockerenv'):
        return "http://ollama:11434"

    return "http://localhost:11434"


def get_data_path(filename):
    """Grants correct data path."""
    return os.path.join(DATA_DIR, filename)


def concat_json_databases(filenames, output_filename):
    """Concatenates multiple JSON databases with id reindexing."""
    merged_data = []

    for fn in filenames:
        path = get_data_path(fn)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                merged_data.extend(json.load(f))
        else:
            print(f"[!] Warning: File {fn} not found in {DATA_DIR}")

    # Reindexing
    for i, item in enumerate(merged_data, 1):
        item["id"] = i

    output_path = get_data_path(output_filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=4, ensure_ascii=False)
    print(f"[+] Concatenated {len(merged_data)} items into {output_filename}")


def labels_distribution(database):
    """Calculates label distribution in database."""
    if isinstance(database, str):
        with open(get_data_path(database), 'r', encoding='utf-8') as f:
            database = json.load(f)

    intent_counts = Counter()
    case_counts = Counter()
    mistake_counts = Counter()

    for chat in database:
        meta = chat.get("metadata", {})

        intent_counts[meta.get("intent")] += 1
        case_type = meta.get("case_type")
        case_counts[case_type] += 1

        if case_type == "agent_mistake":
            mistake_counts[meta.get("mistake")] += 1

    return {
        "intents": {i: intent_counts[i] for i in INTENTS},
        "case_types": {c: case_counts[c] for c in CASE_TYPES},
        "mistakes": {m: mistake_counts[m] for m in AGENT_MISTAKES},
        "totals": {
            "intents": len(database),
            "mistakes": sum(mistake_counts.values())
        }
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Utility tools for dataset management")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Example: python utils.py merge --inputs a.json b.json --output combined.json
    merge_parser = subparsers.add_parser("merge", help="Merge multiple JSON files")
    merge_parser.add_argument("--inputs", nargs="+", required=True, help="List of files to merge")
    merge_parser.add_argument("--output", default="merged_dataset.json", help="Output filename")

    # Example: python utils.py stats --input dataset.json
    stats_parser = subparsers.add_parser("stats", help="Show dataset distribution statistics")
    stats_parser.add_argument("--input", required=True, help="Database filename to analyze")

    args = parser.parse_args()

    if args.command == "merge":
        concat_json_databases(args.inputs, args.output)

    elif args.command == "stats":
        results = labels_distribution(args.input)
        if results:
            print(json.dumps(results, indent=4))


