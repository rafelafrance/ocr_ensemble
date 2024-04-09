from typing import ClassVar

from line_align.pylib import char_sub_matrix
from line_align.pylib.align import LineAlign
from spell_well.pylib.spell_well import SpellWell

from ensemble.pylib import label_builder, ocr_runner
from ensemble.pylib import label_transformer as lt


class Ensemble:
    all_pipes: ClassVar[dict[str, str]] = {
        "none_easyocr": "[,easyocr]",
        "none_tesseract": "[,tesseract]",
        "deskew_easyocr": "[deskew,easyocr]",
        "deskew_tesseract": "[deskew,tesseract]",
        "binarize_easyocr": "[binarize,easyocr]",
        "binarize_tesseract": "[binarize,tesseract]",
        "denoise_easyocr": "[denoise,easyocr]",
        "denoise_tesseract": "[denoise,tesseract]",
        "pre_process": "[pre_process]",
        "post_process": "[post_process]",
    }

    def __init__(self, **kwargs):
        self.pipes = {k for k in self.all_pipes if kwargs.get(k, False)}
        if not self.pipes:
            msg = "No pipes given"
            raise ValueError(msg)

        matrix = char_sub_matrix.get(char_set="default")
        self.aligner = LineAlign(matrix)
        self.spell_well = SpellWell()

    @property
    def needs_deskew(self):
        deskew = any(1 for p in self.pipes if p.startswith("deskew"))
        return deskew or self.needs_binarize or self.needs_denoise

    @property
    def needs_denoise(self):
        return any(1 for p in self.pipes if p.startswith("denoise"))

    @property
    def needs_binarize(self):
        binarize = any(1 for p in self.pipes if p.startswith("binarize"))
        return binarize or self.needs_denoise

    @property
    def pipeline(self):
        pipes = [v for k, v in self.all_pipes.items() if k in self.pipes]
        return ",".join(pipes)

    async def run(self, image):
        lines = list(await self.ocr(image))
        lines = label_builder.filter_lines(lines)
        text = self.aligner.align(lines)
        text = label_builder.consensus(text)
        if "post_process" in self.pipes:
            text = label_builder.post_process_text(text, self.spell_well)
        return text

    async def ocr(self, image):
        deskew = lt.transform_label("deskew", image) if self.needs_deskew else None
        binary = lt.transform_label("binarize", deskew) if self.needs_binarize else None
        denoise = lt.transform_label("denoise", binary) if self.needs_denoise else None

        deskew = lt.array_to_image(deskew) if deskew is not None else None
        binary = lt.array_to_image(binary) if binary is not None else None
        denoise = lt.array_to_image(denoise) if denoise is not None else None

        pre_process = "preprocess" in self.pipes

        lines = []
        if "none_easyocr" in self.pipes:
            lines.append(await ocr_runner.easy_text(image, pre_process=pre_process))
        if "none_tesseract" in self.pipes:
            lines.append(await ocr_runner.tess_text(image, pre_process=pre_process))
        if "deskew_easyocr" in self.pipes:
            lines.append(await ocr_runner.easy_text(deskew, pre_process=pre_process))
        if "deskew_tesseract" in self.pipes:
            lines.append(await ocr_runner.tess_text(deskew, pre_process=pre_process))
        if "binarize_easyocr" in self.pipes:
            lines.append(await ocr_runner.easy_text(binary, pre_process=pre_process))
        if "binarize_tesseract" in self.pipes:
            lines.append(await ocr_runner.tess_text(binary, pre_process=pre_process))
        if "denoise_easyocr" in self.pipes:
            lines.append(await ocr_runner.easy_text(denoise, pre_process=pre_process))
        if "denoise_tesseract" in self.pipes:
            lines.append(await ocr_runner.tess_text(denoise, pre_process=pre_process))
        return lines
