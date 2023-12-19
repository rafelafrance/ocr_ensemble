# reconcile_traits ![Python application](https://github.com/rafelafrance/reconcile_traits/workflows/CI/badge.svg)

Reconcile traits from different sources: Traiter (FloraTraiter, etc.) and ChatGPT4.

## General workflow
1. Have a set of OCRed labels or treatments in a directory, one text file per label or treatment.
2. Have a set of traits gotten from ChatGPT.
3. Have a set of traits gotten from FloraTraiter.
4. **reconcile_traits.py**: Perform the reconciliation of the output from steps 1 - 3.
