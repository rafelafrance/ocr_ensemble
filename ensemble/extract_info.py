#!/usr/bin/env python3
import argparse
import json
import textwrap
from pathlib import Path

import openai
from pylib import log


def main():
    log.started()
    args = parse_args()

    with open(args.key_file) as f:
        keys = json.load(f)
    openai.api_key = keys["key"]

    labels = get_labels(args.text_dir, args.limit, args.offset)

    for stem, text in labels.items():
        prompt = f'{args.prompt} "{text}"'
        info = openai.Completion.create(model=args.model, prompt=prompt)

        path = args.openai_dir / f"{stem}.json"
        with open(path, "w") as f:
            f.write(info)

    log.finished()


def get_labels(text_dir, limit, offset) -> dict[str, str]:
    labels = {}

    paths = sorted(text_dir.glob("*"))

    if limit:
        paths = paths[offset : limit + offset]

    for path in paths:
        with open(path) as f:
            labels[path.stem] = f.read()

    return labels


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        fromfile_prefix_chars="@",
        description=textwrap.dedent(
            """Use ChatGPT to extract trait information from museum label text."""
        ),
    )

    arg_parser.add_argument(
        "--text-dir",
        metavar="PATH",
        type=Path,
        required=True,
        help="""Directory containing the input text files.""",
    )

    arg_parser.add_argument(
        "--openai-dir",
        metavar="PATH",
        type=Path,
        required=True,
        help="""Output JSON files holding traits, one for each input text file, in this
            directory.""",
    )

    arg_parser.add_argument(
        "--key-file",
        metavar="PATH",
        type=Path,
        required=True,
        help="""This JSON file contains the OpenAI key.""",
    )

    arg_parser.add_argument(
        "--prompt",
        metavar="PROMPT",
        default=(
            "You  are an expert botanist, please extract all information from "
            "the herbarium label text, "
        ),
        help="""Prompt for ChatGPT. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--model",
        metavar="MODEL",
        default="gpt-4",
        help="""Which ChatGPT model to use. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--limit",
        type=int,
        help="""Read this many labels for input.""",
    )

    arg_parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="""Offset for splitting data.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main()
