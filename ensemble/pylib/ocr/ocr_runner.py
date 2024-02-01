from dataclasses import dataclass, field

import easyocr
import numpy as np
import pytesseract

from ensemble.pylib.builder import label_builder


@dataclass
class Line:
    """Holds data for building one line of OCR text."""

    boxes: list[dict] = field(default_factory=list)


class EngineConfig:
    easy_ocr = easyocr.Reader(["en"], gpu=True)

    char_blacklist = "¥€£¢$«»®©™§{}|~”"
    tess_lang = "eng"
    tess_config = " ".join(
        [
            f"-l {tess_lang}",
            f"-c tessedit_char_blacklist='{char_blacklist}'",
        ]
    )


async def tesseract_engine(image) -> list[dict]:
    df = pytesseract.image_to_data(
        image, config=EngineConfig.tess_config, output_type="data.frame"
    )

    df = df.loc[df.conf > 0]

    if df.shape[0] > 0:
        df.text = df.text.astype(str)
        df.text = df.text.str.strip()
        df.conf /= 100.0
        df["right"] = df.left + df.width
        df["bottom"] = df.top + df.height
    else:
        df["right"] = None
        df["bottom"] = None

    df = df.loc[:, ["conf", "left", "top", "right", "bottom", "text"]]

    df = df.rename(
        columns={
            "left": "ocr_left",
            "top": "ocr_top",
            "right": "ocr_right",
            "bottom": "ocr_bottom",
            "text": "ocr_text",
        }
    )

    results = df.to_dict("records")
    return results


async def easyocr_engine(image) -> list[dict]:
    results = []
    image = np.asarray(image)
    raw = EngineConfig.easy_ocr.readtext(image, blocklist=EngineConfig.char_blacklist)
    for item in raw:
        pos = item[0]
        results.append(
            {
                "conf": item[2],
                "ocr_left": int(pos[0][0]),
                "ocr_top": int(pos[0][1]),
                "ocr_right": int(pos[1][0]),
                "ocr_bottom": int(pos[2][1]),
                "ocr_text": item[1],
            }
        )
    return results


async def easy_text(image, pre_process=True) -> str:  # noqa: FBT002
    ocr_boxes = await easyocr_engine(image)
    return build_text(ocr_boxes, pre_process=pre_process)


async def tess_text(image, pre_process=True) -> str:  # noqa: FBT002
    ocr_boxes = await tesseract_engine(image)
    return build_text(ocr_boxes, pre_process=pre_process)


def build_text(ocr_boxes, pre_process=True):  # noqa: FBT002
    lines = get_lines(ocr_boxes)

    text = []
    for ln in lines:
        line = " ".join([b["ocr_text"] for b in ln.boxes])
        if pre_process:
            line = line.strip()
            line = label_builder.substitute(line)
        text.append(line)

    text = "\n".join(text)
    return text


def get_lines(ocr_boxes, vert_overlap=0.3):
    """Find lines of text from an OCR bounding boxes."""
    boxes = sorted(ocr_boxes, key=lambda b: b["ocr_left"])
    lines: list[Line] = []

    for box in boxes:
        overlap = [(find_overlap(line, box), line) for line in lines]
        overlap = sorted(overlap, key=lambda o: -o[0])

        if overlap and overlap[0][0] > vert_overlap:
            line = overlap[0][1]
            line.boxes.append(box)
        else:
            line = Line()
            line.boxes.append(box)
            lines.append(line)

    lines = sorted(lines, key=lambda r: r.boxes[0]["ocr_top"])
    return lines


def find_overlap(line: Line, ocr_box, eps=1e-6):
    """
    Find the vertical overlap between a line and an OCR bounding box.

    This is expressed as a fraction of the smallest height of the line
    & OCR bounding box.
    """
    last = line.boxes[-1]
    min_height = min(
        last["ocr_bottom"] - last["ocr_top"],
        ocr_box["ocr_bottom"] - ocr_box["ocr_top"],
    )
    y_min = max(last["ocr_top"], ocr_box["ocr_top"])
    y_max = min(last["ocr_bottom"], ocr_box["ocr_bottom"])
    inter = max(0, y_max - y_min)
    return inter / (min_height + eps)
