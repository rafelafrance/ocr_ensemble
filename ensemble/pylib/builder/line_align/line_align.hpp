#pragma once

/**
 * Naive implementations of string algorithms based on Gusfield, 1997.
 * I.e. There's _plenty_ of room for improvement.
 *
 * NOTE: The functions are geared towards OCR errors and not human
 *       errors. OCR engines will often mistake one letter for another
 *       or drop/add a character (particularly from the ends) but
 *       will seldom transpose characters, which humans do often.
 * Therefore: I do not consider transpositions in the Levenshtein or
 *       Needleman Wunsch distances, substitutions are based
 *       on visual similarity, etc.
 */

#include <string>
#include <tuple>
#include <unordered_map>
#include <vector>

/**
 * The character used to represent gaps in alignment output.
 */
const char32_t gap_char = U'⋄';

const std::unordered_map<std::u32string, float> noSubs = {};

// The only reason for the struct is so that I can setup the substitution matrix once
// at the start of the program.
struct LineAlign {
    /** Constructor.
     * @param substitutions The substitution matrix given as a map, with the key as
     * a two character string representing the two character being substituted.
     * Symmetry is assumed so you only need to give the lexically first of a pair,
     * i.e. for "ab" and "ba" you only need to send in "ab". The value of the map is
     * the cost of substituting the two characters.
     * @param gap The gap open penalty for alignments. This is typically negative.
     * @param skew The gap extension penalty for the alignments. Also negative.
    */
    LineAlign(
        const std::unordered_map<std::u32string, float>& substitutions = noSubs,
        float gap = -3.0,
        float skew = -0.5
    );

    /**
     * Compute the Levenshtein distance for 2 strings.
     *
     * @param str1 Is a string to compare.
     * @param str2 The other string to compare.
     * @return The Levenshtein distance is an integer. The lower the number the more
     * similar the strings.
     */
    long levenshtein(const std::u32string &str1, const std::u32string &str2) const;

    /**
     * Compute a Levenshtein distance for every pair of strings in list.
     *
     * @param strings A list of strings to compare.
     * @return A sorted list of tuples. The tuple contains:
     *     - The Levenshtein distance of the pair of strings.
     *     - The index of the first string compared.
     *     - The index of the second string compared.
     * The tuples are sorted by distance.
     */
    std::vector<std::tuple<long, long, long>>
    levenshtein_all(const std::vector<std::u32string> &strings) const;

    /**
     * Create a multiple sequence alignment of a set of similar short text fragments.
     * That is if I am given a set of strings like:
     *
     *     MOJAVE DESERT, PROVIDENCE MTS.: canyon above
     *     E. MOJAVE DESERT , PROVIDENCE MTS . : canyon above
     *     E MOJAVE DESERT PROVTDENCE MTS. # canyon above
     *     Be ‘MOJAVE DESERT, PROVIDENCE canyon “above
     *
     * I should get back something similar to the following. The exact return value
     * will depend on the substitution matrix, gap, and skew penalties passed to the
     * function.
     *
     *     ⋄⋄⋄⋄MOJAVE DESERT⋄, PROVIDENCE MTS.⋄⋄: canyon ⋄above
     *     E⋄. MOJAVE DESERT , PROVIDENCE MTS . : canyon ⋄above
     *     E⋄⋄ MOJAVE DESERT ⋄⋄PROVTDENCE MTS. #⋄ canyon ⋄above
     *     Be ‘MOJAVE DESERT⋄, PROVIDENCE ⋄⋄⋄⋄⋄⋄⋄⋄canyon “above
     *
     * Where "⋄" characters are used to represent gaps in the alignments.
     *
     * @param strings A list of strings to align.
     */
    std::vector<std::u32string> align(const std::vector<std::u32string> &strings) const;

private:
    std::unordered_map<std::u32string, float> substitutions;
    float gap;
    float skew;
};
