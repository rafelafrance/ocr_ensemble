# ocr_ensemble
OCR herbarium labels with an ensemble of image processing and OCR engines

I was getting some bad result using open source OCR engines to read text on herbarium sheets. So I came up with a scheme to use an ensemble of image processing techniques and OCR engines to see if I could improve the results. This sounds good in theory but how do you combine the results of the OCR texts into a single "best" result?

To combine the text results I borrowed a technique from bioinformatics, multiple sequence alignment. Obviously, I needed to switch from using evolutionary distance to visual distance for the substitution matrix.

...
