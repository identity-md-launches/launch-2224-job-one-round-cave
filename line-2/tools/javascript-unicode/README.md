# JavaScript Unicode

Expose Unicode hidden in JavaScript-style `\uXXXX` and `\u{...}` escape
candidates without running the supplied text. Adjacent fixed-width UTF-16
high/low surrogates receive one combined scalar view, with separate byte
ranges for both original escapes. This helps reviewers inspect identifiers
and strings before trusting copied source. Python 3.10+; standard library
only; this folder works by itself, offline.

Run from the repository root:

```sh
python3 -B line-2/tools/javascript-unicode/javascript_unicode.py --demo
```

The synthetic demo reports four candidates: U+0456 (an escaped Cyrillic letter
in `admin`), U+1F438 (two surrogate escapes combined), U+202E (a direction
control), and a lone U+D800 code unit. The latter has no UTF-8 encoding.
All 15 local tests passed, including 1,200 seeded fixed-escape/surrogate-pair
comparisons with Python's independent JSON decoder and a complete 2 MiB dense
input. Real gathering-report bytes yielded zero candidates. Scans of the
engine and its tests find deliberate lexical examples; those are not attack
claims. Round 40's evidence records exact counts and source hashes.

Review a selected UTF-8 file, read-only:

```sh
python3 -B line-2/tools/javascript-unicode/javascript_unicode.py --file line-2/tools/javascript-unicode/javascript_unicode.py --max-details 10
```

Exit status is 0 for an empty scan or the demo, 1 for candidates in a selected
file, and 2 for invalid input/options. JSON output is ASCII, including errors.
Each retained candidate cites its original half-open UTF-8 byte range, escape
hex, span SHA-256, one-based LF line/byte column, scalar name/category and UTF-8
bytes where defined. The report includes the whole-input hash, runtime Unicode
version and complete counts. `--max-details` (0–1000; default 100) caps only
retained evidence; omitted details are counted. Input is bounded to 2 MiB,
strict UTF-8, and a selected regular file resolving within the current working
directory. There are no writes, network calls, environment reads, external
dependencies, JavaScript execution or recursive decoding. Path containment is
not a sandbox against concurrent filesystem changes.

This is a lexical evidence tool, **not a JavaScript parser or security
verdict**. It includes comments, raw templates, regular expressions and other
text. It does not determine whether a runtime consumes an escape, whether an
identifier is legal, or whether a font confuses two characters. Other
backslash pairs are skipped once; odd/even backslash parity is respected.
Braced hex accepts arbitrarily many leading zeroes within the input bound and
rejects values above U+10FFFF. Malformed candidates stop before unexpected
bytes so later escapes stay visible. Only adjacent **fixed-width** high/low
surrogates combine: braced surrogates, lone units, reversed pairs and separated
pairs remain separate. This combined view describes UTF-16 evidence; it does
not assert identifier validity. Literal Unicode, other escape syntaxes and
other decoding layers require separate review. Empty results cannot establish
safety. Hashes establish byte identity, not authenticity. Terminal-safe JSON
is not HTML-safe embedding.

Reproduce checks:

```sh
python3 -B -m unittest discover -s line-2/tools/javascript-unicode -p 'test_*.py' -v
```
