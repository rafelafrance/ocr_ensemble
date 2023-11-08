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

    bad_json, missing = 0, 0

    in_paths = sorted(args.openai_dir.glob("*"))
    for in_path in in_paths:
        with open(in_path) as f:
            lines = f.readlines()

        # Find the JSON buried in the text
        beg, end = -1, -1
        for i, ln in enumerate(lines):
            if beg < 0 and ln.lstrip().startswith("{"):
                beg = i
            elif ln.lstrip().startswith("}"):
                end = i

        # Missing JSON
        if beg == -1 or end == -1:
            missing += 1
            logging.error(f"Missing JSON: {in_path.name}")

            if args.show_missing_json:
                print("".join(lines))
                print()

            lines = ["{\n", "}\n"]
            beg, end = 0, 1

        # Rebuild the file with only the JSON
        lines = "".join(lines[beg : end + 1])

        # Validate the JSON
        try:
            json.loads(lines)

        # Bad JSON
        except json.JSONDecodeError as err:
            bad_json += 1
            logging.error(f"Bad     JSON: {in_path.name}")

            if args.show_bad_json:
                print(err)
                print("".join(lines))
                print()

        # Output what we can
        out_path = args.clean_dir / in_path.name
        with open(out_path, "w") as f:
            f.write(lines)

    logging.info(
        f"Count: {len(in_paths)}, Bad JSON: {bad_json}, "
        f"Missing JSON: {missing}, Total errors: {bad_json + missing}"
    )

    log.finished()


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        fromfile_prefix_chars="@",
        description=textwrap.dedent(
            """Clean up the output from ChatGPT trait extractions."""
        ),
    )

    arg_parser.add_argument(
        "--openai-dir",
        metavar="PATH",
        type=Path,
        required=True,
        help="""Directory holding the openai output files with dirty JSON.""",
    )

    arg_parser.add_argument(
        "--clean-dir",
        metavar="PATH",
        type=Path,
        required=True,
        help="""Output cleaned JSON files to this directory.""",
    )

    arg_parser.add_argument(
        "--show-bad-json",
        action="store_true",
        help="""Print files that have incorrect JSON to the screen.""",
    )

    arg_parser.add_argument(
        "--show-missing-json",
        action="store_true",
        help="""Print files that are missing JSON to the screen.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main()
