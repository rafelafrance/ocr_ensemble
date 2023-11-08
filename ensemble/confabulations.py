#!/usr/bin/env python3
import argparse
import json
import logging
import textwrap
from pathlib import Path

from pylib import log


def main():
    log.started()
    args = parse_args()

    total_errors = 0

    i = 0
    paths = get_paths(args.text_dir, args.clean_dir)
    for text_path, json_path in paths.items():
        i += 1
        with open(text_path) as f:
            text = f.read()

        with open(json_path) as f:
            data = json.load(f)

        data = flatten_json(data)

        print("-" * 80)
        logging.info(Path(text_path).stem)
        print()
        print(text)
        print()

        # text = text.lower()
        errors = 0
        for key, value in data.items():
            errors += check_value(text, key, value)

        logging.info(f"Confabulations: {errors}")

        total_errors += errors

        if i == 11:
            break

    logging.info(f"Total confabulations: {total_errors}")
    log.finished()


def check_value(text, key, value) -> int:
    if key.endswith("eventDate"):
        return 0

    match value:
        case str():
            pass
            # value = value.lower()
        case int() | float():
            value = str(value)

    if value not in text:
        print(key)
        print(value)
        print()
        return 1
    return 0


def flatten_json(obj):
    out = {}

    def flatten(item, name=""):
        match item:
            case dict():
                for k, v in item.items():
                    flatten(v, f"{name}.{k}")
            case list():
                for i, v in enumerate(item):
                    flatten(v, f"{name}.{i}")
            case _:
                out[name[1:]] = item

    flatten(obj)

    return out


def get_paths(text_dir, clean_dir):
    paths = {}
    text_paths = sorted(text_dir.glob("*"))
    for text_path in text_paths:
        json_path = clean_dir / f"{text_path.stem}.json"
        if json_path.exists():
            paths[str(text_path)] = str(json_path)
    return paths


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        fromfile_prefix_chars="@",
        description=textwrap.dedent(
            """Look for confabulations in ChatGPT trait extractions."""
        ),
    )

    arg_parser.add_argument(
        "--text-dir",
        metavar="PATH",
        type=Path,
        required=True,
        help="""Directory containing the original text files for comparison.""",
    )

    arg_parser.add_argument(
        "--clean-dir",
        metavar="PATH",
        type=Path,
        required=True,
        help="""Get cleaned ChatGPT JSON files from this directory.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main()
