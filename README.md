# reconcile_traits

Reconcile traits from different sources: Traiter (FloraTraiter, etc.) and ChatGPT4.

## General workflow
1. Have a set of OCRed labels or treatments in a directory, one text file per label or treatment.
2. **get_gpt_output.py**: Send each file from step 1 to the OpenAI server for parsing.
3. **clean_gpt_output.py**: Clean the ChatGPT output from step 2.
4. **reconcile_traits.py**: Perform the reconciliation the output from step 3 and a Traiter run.
