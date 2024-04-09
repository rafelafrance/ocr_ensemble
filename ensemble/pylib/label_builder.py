import collections
import unicodedata

import regex as re
from line_align.pylib.levenshtein import levenshtein_all

MIN_LEN = 2

# When there is no clear "winner" for a character in the multiple alignment of
# a set of strings I sort the characters by unicode category as a tiebreaker
CATEGORY = {
    "Lu": 20,
    "Ll": 20,
    "Lt": 20,
    "Lm": 20,
    "Lo": 20,
    "Nd": 30,
    "Nl": 60,
    "No": 60,
    "Pc": 70,
    "Pd": 40,
    "Ps": 50,
    "Pe": 50,
    "Pi": 50,
    "Pf": 50,
    "Po": 10,
    "Sm": 99,
    "Sc": 90,
    "So": 90,
    "Zs": 80,
}

# As, above, but if a character has a category of "punctuation other" then I
# sort by the weight for the character itself
PO = {
    ".": 1,
    ",": 2,
    ":": 2,
    ";": 2,
    "!": 5,
    '"': 5,
    "'": 5,
    "*": 5,
    "/": 5,
    "%": 6,
    "&": 6,
}

# Substitutions performed on a consensus sequence
SUBSTITUTIONS = [
    # Remove gaps
    ("⋄", ""),
    # Replace underscores with spaces
    ("_", " "),
    # Replace ™ trademark with a double quote
    ("™", '"'),
    # Remove space before some punctuation: x . -> x.
    (r"(\S)\s+([;:.,°\)\]\}])", r"\1\2"),
    # Compress spaces
    (r"\s\s+", " "),
    # Convert single capital letter, punctuation to capital dot: L' -> L.
    (r"(\p{L}\s\p{Lu})\p{Po}", r"\1."),
    # Add spaces around an ampersand &
    (r"(\w)&", r"\1 &"),
    (r"&(\w)", r"& \1"),
    # Handle multiple dots ..
    (r"\.\.+", r"\."),
    # Confusion between dots . and colons :
    (r"::", r"\.:"),
    # Double single quotes '' should be a double quote "
    (r"['`]['`]", r"\""),
    # Replace @ and 0
    (r"(?<=\d)@(?=\d)", "0"),
    # October spelled with a zero
    ("0ct", "Oct"),
]


def filter_lines(lines: list[str], threshold=128) -> list[str]:
    """Sort the lines by Levenshtein distance and filter out the outliers."""
    if len(lines) <= MIN_LEN:
        return lines

    # levenshtein_all() returns a sorted array of Distance named tuples/objects
    distances = levenshtein_all(lines)

    threshold += distances[0].dist  # Score cannot be more than best score + threshold

    order = {}  # Dicts preserve insertion order, sets do not
    for score, i, j in distances:
        if score > threshold:
            break
        order[i] = 1
        order[j] = 1

    ordered = [lines[k] for k in order]
    return ordered


def _char_key(char):
    """Get the character sort order."""
    order = CATEGORY.get(unicodedata.category(char), 100)
    order = PO.get(char, order)
    return order, char


def consensus(aligned: list[str]) -> str:
    """
    Build a consensus string from the aligned copies.

    Look at all characters of the multiple alignment and choose the most common one,
    using heuristics as a tiebreaker.
    """
    cons = []
    for i in range(len(aligned[0])):
        counts = collections.Counter(s[i] for s in aligned).most_common()
        top = counts[0][1]
        chars = [c[0] for c in counts if c[1] == top]
        chars = sorted(chars, key=_char_key)
        cons.append(chars[0])
    return "".join(cons)


def substitute(line: str) -> str:
    """Perform simple substitutions on a consensus string."""
    for old, new in SUBSTITUTIONS:
        line = re.sub(old, new, line)
    return line


def add_spaces(line, spell_well, vocab_len=3):
    """
    Add spaces between words.

    OCR engines will remove spaces between words. This function looks for a non-word
    and sees if adding a space will create 2 (or 1) word.
    For example: "SouthFlorida" becomes "South Florida".
    """
    tokens = spell_well.tokenize(line)

    new = []
    for token in tokens:
        if token.isspace() or spell_well.is_word(token) or len(token) < vocab_len:
            new.append(token)
        else:
            candidates = []
            for i in range(1, len(token) - 1):
                freq1 = spell_well.freq(token[:i])
                freq2 = spell_well.freq(token[i:])
                if freq1 or freq2:
                    sum_ = freq1 + freq2
                    count = int(freq1 > 0) + int(freq2 > 0)
                    candidates.append((count, sum_, i))
            if candidates:
                i = sorted(candidates, reverse=True)[0][2]
                new.append(token[:i])
                new.append(" ")
                new.append(token[i:])
            else:
                new.append(token)

    return line


def remove_spaces(line, spell_well):
    """
    Remove extra spaces in words.

    OCR engines will put spaces where there shouldn't be any. This is a simple
    scanner that looks for 2 non-words that make a new word when a space is removed.
    For example: "w est" becomes "west".
    """
    tokens = spell_well.tokenize(line)

    if len(tokens) <= MIN_LEN:
        return line

    new = tokens[:2]

    for i in range(2, len(tokens)):
        prev = tokens[i - 2]
        between = tokens[i - 1]
        curr = tokens[i]

        if (
            between.isspace()
            and spell_well.is_word(prev + curr)
            and not (spell_well.is_word(prev) or spell_well.is_word(curr))
        ):
            new.pop()  # Remove between
            new.pop()  # Remove prev
            new.append(prev + curr)
        else:
            new.append(tokens[i])

    return "".join(new)


def spell_correct(line, spell_well):
    new = []
    for token in spell_well.tokenize(line):
        if spell_well.is_letters(token):
            token = spell_well.correct(token)
        new.append(token)
    return "".join(new)


def post_process_text(text, spell_well):
    text = substitute(text)
    text = add_spaces(text, spell_well)
    text = remove_spaces(text, spell_well)
    text = spell_correct(text, spell_well)
    return text
