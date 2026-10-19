#!/usr/bin/env python3
"""Review JavaScript-style Unicode escape candidates as inert UTF-8 bytes."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import stat
import sys
import unicodedata

MAX_BYTES = 2 * 1024 * 1024
HEX = b'0123456789abcdefABCDEF'
DEMO = br'const adm\u{456}n = "\uD83D\uDC38"; const direction = "\u202E"; const lone = "\uD800";'


def describe(value):
    char = chr(value)
    return {'codepoint': f'U+{value:04X}',
            'name': unicodedata.name(char, 'UNNAMED'),
            'category': unicodedata.category(char),
            'utf8_hex': None if 0xd800 <= value <= 0xdfff else char.encode('utf-8').hex()}


def escape(data, lo):
    """Parse one backslash-u; return exclusive end, value, form, issue."""
    i = lo + 2
    if i < len(data) and data[i] == 123:
        i += 1
        start = i
        value = 0
        # Saturation keeps arbitrarily many leading zeroes linear and bounded.
        while i < len(data) and data[i] in HEX:
            value = min(0x110000, value * 16 + int(chr(data[i]), 16))
            i += 1
        if i == start:
            if i < len(data) and data[i] == 125:
                i += 1
            return i, None, 'braced', 'empty-or-nonhex-brace'
        if i == len(data) or data[i] != 125:
            return i, None, 'braced', 'unterminated-or-nonhex-brace'
        i += 1
        return (i, None, 'braced', 'out-of-range') if value > 0x10ffff else (i, value, 'braced', None)
    start = i
    while i < len(data) and i - start < 4 and data[i] in HEX:
        i += 1
    if i - start != 4:
        return i, None, 'fixed', 'incomplete-hex-escape'
    return i, int(data[start:i], 16), 'fixed', None


def scan(data, max_details=100):
    if not isinstance(data, bytes) or len(data) > MAX_BYTES:
        raise ValueError('input must be bytes of at most 2 MiB')
    if type(max_details) is not int or not 0 <= max_details <= 1000:
        raise ValueError('max_details must be an integer from 0 to 1000')
    data.decode('utf-8', 'strict')
    counts, details = Counter(), []
    i, line, line_start, previous = 0, 1, 0, 0
    while i < len(data):
        lo = data.find(b'\\', i)
        if lo < 0 or lo + 1 == len(data):
            break
        i = lo + 2
        if data[lo + 1] != ord('u'):
            continue
        end, value, form, issue = escape(data, lo)
        parts = [[lo, end]]
        # Only adjacent fixed-width high/low code units form this view. A braced
        # surrogate remains a separate candidate, even next to a fixed one.
        if form == 'fixed' and value is not None and 0xd800 <= value <= 0xdbff and data[end:end+2] == b'\\u':
            end2, low, form2, issue2 = escape(data, end)
            if form2 == 'fixed' and issue2 is None and 0xdc00 <= low <= 0xdfff:
                parts.append([end, end2])
                value = 0x10000 + ((value - 0xd800) << 10) + low - 0xdc00
                end, form = end2, 'fixed-surrogate-pair'
        i = end
        line += data.count(b'\n', previous, lo)
        last_lf = data.rfind(b'\n', previous, lo)
        if last_lf >= 0:
            line_start = last_lf + 1
        previous = lo
        kind = ('malformed' if issue else 'surrogate-code-unit' if 0xd800 <= value <= 0xdfff
                else 'ascii' if 0x20 <= value <= 0x7e else 'non-ascii-or-control')
        counts[kind] += 1
        if len(details) < max_details:
            raw = data[lo:end]
            details.append({'source_byte_range': [lo, end], 'component_byte_ranges': parts,
                            'source_line': line, 'source_byte_column': lo - line_start + 1,
                            'source_escape_hex': raw.hex(), 'source_span_sha256': hashlib.sha256(raw).hexdigest(),
                            'form': form, 'kind': kind, 'issue': issue,
                            'decoded_codepoint': None if value is None else describe(value)})
    total = sum(counts.values())
    return {'schema_version': 1, 'tool': 'javascript-unicode/1',
            'source_sha256': hashlib.sha256(data).hexdigest(), 'source_bytes': len(data),
            'unicode_version': unicodedata.unidata_version, 'analysis_complete': True,
            'candidate_count': total, 'counts_by_kind': dict(sorted(counts.items())),
            'detail_cap': max_details, 'retained_details': len(details),
            'omitted_details': total - len(details), 'details': details,
            'limitations': [
                'Lexical candidates, not a JavaScript parser: comments, raw templates, regular expressions and non-JavaScript text are included.',
                'No claim that a runtime interprets a candidate or accepts it in an identifier. Grammar, string context, rendering and intent are outside scope.',
                'Only lowercase backslash-u, four-hex and braced-hex forms. Other backslash pairs are skipped, not decoded; decoded output is never rescanned.',
                'Only immediately adjacent fixed-width high/low surrogates combine. This is a UTF-16 evidence view, not identifier validity or language evaluation.',
                'Braced surrogates and lone fixed surrogates remain code units without UTF-8 encoding. Other literal characters and decoding layers need separate review.',
                'Malformed candidates stop before the first unexpected byte; later candidates remain visible. Braced hex accepts leading zeroes and checks numeric range.',
                'Ranges are zero-based half-open original UTF-8 bytes; line and byte column are one-based with LF-only line breaks.',
                'Counts cover all input; details may be omitted. Unicode names/categories depend on the reported runtime database version.',
                'ASCII JSON is suitable for terminal display, not HTML embedding. Hashes prove identity, not authenticity. No findings does not establish safety.'
            ]}


def read_selected(path):
    selected = Path(path).resolve(strict=True)
    if not selected.is_relative_to(Path.cwd().resolve()):
        raise ValueError('file must resolve within the current working directory')
    if not stat.S_ISREG(selected.stat().st_mode):
        raise ValueError('input must be a regular file')
    with selected.open('rb') as handle:
        data = handle.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError('input exceeds 2 MiB')
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--demo', action='store_true')
    group.add_argument('--file', type=Path)
    parser.add_argument('--max-details', type=int, default=100)
    args = parser.parse_args(argv)
    try:
        report = scan(DEMO if args.demo else read_selected(args.file), args.max_details)
    except (OSError, ValueError, RuntimeError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=True), file=sys.stderr)
        return 2
    report['source_kind'] = 'synthetic-demo' if args.demo else 'selected-file'
    print(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True))
    return 0 if args.demo or not report['candidate_count'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
