import argparse
import itertools
import warnings

import torch
from PIL import Image
from tqdm import tqdm

from ensemble import box_calc

from ..db import db
from .ensemble import Ensemble


async def ocr_labels(args: argparse.Namespace) -> None:
    ensemble = Ensemble(**vars(args))

    with db.connect(args.database) as cxn:
        run_id = db.insert_run(cxn, args)

        db.canned_delete(cxn, "ocr_texts", ocr_set=args.ocr_set)

        sheets = get_sheet_labels(
            cxn, args.classes, args.label_set, args.label_conf, args.limit
        )

        with warnings.catch_warnings():  # Turn off EXIF warnings
            warnings.filterwarnings("ignore", category=UserWarning)

            for path, labels in tqdm(sheets.items()):
                sheet = Image.open(path)
                batch: list[dict] = []

                for lb in labels:
                    label = sheet.crop(
                        (
                            lb["label_left"],
                            lb["label_top"],
                            lb["label_right"],
                            lb["label_bottom"],
                        )
                    )

                    text = await ensemble.run(label)
                    batch.append(
                        {
                            "label_id": lb["label_id"],
                            "ocr_set": args.ocr_set,
                            "pipeline": ensemble.pipeline,
                            "ocr_text": text,
                        }
                    )
                db.canned_insert(cxn, "ocr_texts", batch)

            db.update_run_finished(cxn, run_id)


def get_sheet_labels(cxn, classes, label_set, label_conf, limit):
    sheets = {}
    labels = db.canned_select(
        cxn, "labels", label_set=label_set, label_conf=label_conf, limit=limit
    )
    labels = sorted(labels, key=lambda lb: lb["path"])
    grouped = itertools.groupby(labels, lambda lb: lb["path"])

    for path, labels in grouped:
        labels = list(labels)

        if classes:
            labels = [lb for lb in labels if lb["class"] in classes]

        labels = remove_overlapping_labels(labels)

        if labels:
            sheets[path] = labels

    return sheets


def remove_overlapping_labels(labels):
    boxes = [
        [lb["label_left"], lb["label_top"], lb["label_right"], lb["label_bottom"]]
        for lb in labels
    ]
    boxes = torch.tensor(boxes)
    boxes = box_calc.small_box_suppression(boxes, threshold=0.4)
    return [lb for i, lb in enumerate(labels) if i in boxes]
