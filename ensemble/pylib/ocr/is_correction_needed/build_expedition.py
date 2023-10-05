import csv
import json
import logging
import os
import warnings
from argparse import Namespace
from pathlib import Path
from textwrap import wrap

import matplotlib.pyplot as plt
import regex as re
from PIL import Image
from tqdm import tqdm
from traiter.pylib.spell_well import SpellWell

from ... import db


def build_3_files(args: Namespace) -> None:
    os.makedirs(args.expedition_dir, exist_ok=True)

    csv_path = args.expedition_dir / "manifest.csv"
    with db.connect(args.database) as cxn, open(csv_path, "w") as csv_file:
        run_id = db.insert_run(cxn, args)

        writer = csv.writer(csv_file)
        writer.writerow(
            "ocr_id image_file text_file json_file ocr_set database".split()
        )

        recs = db.canned_select(cxn, "ocr_texts", ocr_set=args.ocr_set)
        recs = recs[: args.limit] if args.limit else recs

        for rec in tqdm(recs):
            image = get_label(rec)

            image_path = Path(args.expedition_dir) / f"ocr_id_{rec['ocr_id']:04d}.jpg"
            image.save(str(image_path))

            text_path = image_path.with_suffix(".txt")
            with open(text_path, "w") as out_file:
                out_file.write(rec["ocr_text"])

            json_path = image_path.with_suffix(".json")
            with open(json_path, "w") as out_file:
                out_file.write(
                    json.dumps(
                        {
                            "ocr_id": rec["ocr_id"],
                            "image_file": image_path.name,
                            "ocr_set": rec["ocr_set"],
                            "database": str(args.database),
                            "text": rec["ocr_text"],
                        }
                    )
                )

            writer.writerow(
                [
                    rec["ocr_id"],
                    image_path.name,
                    text_path.name,
                    json_path.name,
                    rec["ocr_set"],
                    str(args.database).replace(".", "_").replace("/", "_"),
                ]
            )

        db.update_run_finished(cxn, run_id)


def build_2_files(args: Namespace) -> None:
    os.makedirs(args.expedition_dir, exist_ok=True)

    kept = 0

    spell_well = SpellWell()
    words = {w.lower() for w in spell_well.vocab_to_set()}

    csv_path = args.expedition_dir / "manifest.csv"
    with db.connect(args.database) as cxn, open(csv_path, "w") as csv_file:
        run_id = db.insert_run(cxn, args)

        writer = csv.writer(csv_file)
        writer.writerow("ocr_id image_file text_file ocr_set database".split())

        recs = db.canned_select(cxn, "ocr_texts", ocr_set=args.ocr_set)

        for rec in tqdm(recs):
            word_count, spell_count, ratio = get_counts(rec, words)

            if word_count < args.length_cutoff:
                continue

            if ratio < args.score_cutoff:
                continue

            kept += 1

            image = get_label(rec)

            image_path = Path(args.expedition_dir) / f"ocr_id_{rec['ocr_id']:04d}.jpg"
            image.save(str(image_path))

            text_path = image_path.with_suffix(".txt")
            with open(text_path, "w") as out_file:
                out_file.write(rec["ocr_text"])

            writer.writerow(
                [
                    rec["ocr_id"],
                    image_path.name,
                    text_path.name,
                    rec["ocr_set"],
                    str(args.database).replace(".", "_").replace("/", "_"),
                ]
            )

        db.update_run_finished(cxn, run_id)
        logging.info(f"Kept {kept} of {len(recs)} records")


def get_counts(label: dict, words):
    tokens = [t for t in re.split(r"[^\p{L}]+", label["ocr_text"].lower()) if t]
    total = len(tokens)

    count = sum(1 for w in tokens if w in words)

    ratio = 0.0 if total == 0 else round(count / total, 2)
    return total, count, ratio


def get_label(rec):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)  # No EXIF warnings
        image = Image.open(rec["path"]).convert("RGB")
        image = image.crop(
            (
                rec["label_left"],
                rec["label_top"],
                rec["label_right"],
                rec["label_bottom"],
            )
        )
    return image


def build_side_by_side(args: Namespace) -> None:
    os.makedirs(args.expedition_dir, exist_ok=True)
    csv_path = args.expedition_dir / "manifest.csv"

    with db.connect(args.database) as cxn, open(csv_path, "w") as csv_file:
        run_id = db.insert_run(cxn, args)

        writer = csv.writer(csv_file)
        writer.writerow("ocr_id image_file ocr_set database".split())

        recs = db.canned_select(cxn, "ocr_texts", ocr_set=args.ocr_set)

        with warnings.catch_warnings():  # Turn off EXIF warnings
            warnings.filterwarnings("ignore", category=UserWarning)
            for rec in tqdm(recs):
                words = rec["ocr_text"].split()

                if len(words) < args.min_words:
                    continue

                with Image.open(rec["path"]) as sheet:
                    label = sheet.crop(
                        (
                            rec["label_left"],
                            rec["label_top"],
                            rec["label_right"],
                            rec["label_bottom"],
                        )
                    )

                    text = ["\n".join(wrap(ln)) for ln in rec["ocr_text"].splitlines()]
                    text = "\n".join(text)

                    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 10))
                    fig.set_facecolor("white")

                    ax1.axis("off")
                    ax1.set_anchor("NE")
                    ax1.imshow(label)

                    ax2.axis("off")
                    ax1.set_anchor("NW")
                    ax2.text(
                        0.0,
                        1.0,
                        text,
                        verticalalignment="top",
                        color="black",
                        fontsize=16,
                    )
                    out_path = args.expedition_dir / str(rec["label_id"])
                    plt.savefig(out_path)
                    plt.close(fig)

                    writer.writerow(
                        [
                            rec["ocr_id"],
                            out_path.name,
                            rec["ocr_set"],
                            str(args.database).replace(".", "_").replace("/", "_"),
                        ]
                    )

        db.update_run_finished(cxn, run_id)
