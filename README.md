# hybrid_traiter

Parse technical text (treatments) using a hybrid of rule-based parsers and model-based parsers (ChatGPT4).

## General workflow
1. Have a set of OCRed labels or treatments in a directory, one text file per label or treatment.
2. **get_gpt_output.py**: Send each file from step 1 to the OpenAI server for parsing.
3. **clean_gpt_output.py**: Clean the ChatGPT output from step 2.
4. **format_gpt_output.py**: Validate and format the output from step 3.

## Hybrid model-based and rule-base parsing strategy (foreign model)
1. Send the text off to a model server and save the results in a file.
2. Clean the results so that they are machine parsable.
   1. For instance, if you ask for JSON format the returned data may not actually be real JSON.
3. Make sure that the returned data is not a confabulation/hallucination by checking it against the original text.
   1. The wrinkle here is that some fields, like dates, are almost always reformatted/normalized.
4. Run the returned text for a field against a rule-based parser. This will:
   1. Validate that the model parsed the correct text for the trait.
   2. Put the data into a usable form. Like converting numbers to floats etc.
   3. **Note** This should be analogous to how the unit tests work.
5. TBD Parse dynamic properties. (Other prompts? Another model?)
6. TBD Link traits to each other. (Another model?)
