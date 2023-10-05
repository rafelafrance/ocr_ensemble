# ocr_ensemble![CI](https://github.com/rafelafrance/ocr_ensemble/workflows/CI/badge.svg)

OCR herbarium labels with an ensemble of image processing techniques and OCR engines.

I was getting some bad results using open source OCR engines to read text on herbarium sheets,
so I came up with a scheme to use an ensemble of image processing techniques and OCR engines to see if I could improve the results. This sounds easy in theory but how do you combine the results of the OCR texts into a single "best" result?

To combine the text results I borrowed a technique from bioinformatics, multiple sequence alignment. Obviously, I needed to switch from using evolutionary distance to visual distance for the substitution matrix...

...
