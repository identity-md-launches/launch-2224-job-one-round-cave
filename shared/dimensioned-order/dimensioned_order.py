#!/usr/bin/env python3
"""Compare asserted time intervals with exact mixed-unit endpoints, offline."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import lens_engine as lens
import unit_engine as units

MAX_BYTES = 256 * 1024
TIME = (0, 0, 1, 0)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("nonfinite JSON number")


def analyze(request):
    if not isinstance(request, dict) or set(request) != {'origin', 'events'}:
        raise ValueError("request needs exactly origin and events")
    origin = request['origin']
    if not isinstance(origin, str) or not origin.strip() or len(origin) > 256:
        raise ValueError("origin must name a common asserted time origin (1..256 characters)")
    events = request['events']
    if not isinstance(events, list) or len(events) > lens.MAX_EVENTS:
        raise ValueError(f"events must be an array of at most {lens.MAX_EVENTS} items")
    converted = []
    seen = set()
    for event in events:
        if not isinstance(event, dict) or set(event) != {'id', 'start', 'end'}:
            raise ValueError("each event needs exactly id, start, end")
        name = event['id']
        if not isinstance(name, str) or not name or len(name) > 256 or name in seen:
            raise ValueError("event IDs must be unique nonempty strings of at most 256 characters")
        seen.add(name)
        endpoints = []
        for field in ('start', 'end'):
            expression = event[field]
            if not isinstance(expression, str):
                raise ValueError("endpoints must be dimensioned expression strings")
            quantity = units.Parser(expression).parse()
            quantity = units.Parser.bounded(quantity, 0)
            if quantity.dims != TIME:
                raise ValueError("every endpoint must have time dimensions, including zero")
            endpoints.append(quantity.value)
        if endpoints[1] < endpoints[0]:
            raise ValueError("event end must be at least its start")
        converted.append((name, *endpoints))
    # Lens uses comparisons only. A strictly increasing map to integer ranks
    # preserves <, ==, > exactly, even for fractions with recurring decimals.
    # These ranks are never interpreted as elapsed durations.
    ranks = {value: i for i, value in enumerate(sorted({v for _, a, b in converted for v in (a, b)}))}
    ordered = lens.analyze([{'id': name, 'start': ranks[a], 'end': ranks[b]}
                            for name, a, b in converted])
    return {'schema': 'dimensioned-order/v1', 'origin': origin,
            'semantics': 'nonzero [start,end); zero-width exact point; all endpoints relative to asserted common origin',
            'endpoints_seconds': [{'id': name, 'start': str(a), 'end': str(b)}
                                  for name, a, b in converted],
            'analysis': ordered,
            'limits': 'Checks supplied quantities and strict order only; origin alignment and clock bounds are assertions, not measurements or causality.'}


def review(raw):
    if len(raw) > MAX_BYTES:
        raise ValueError(f"input exceeds {MAX_BYTES} bytes")
    request = json.loads(raw.decode('utf-8'), object_pairs_hook=unique_object,
                         parse_constant=reject_constant)
    result = analyze(request)
    result['input_sha256'] = hashlib.sha256(raw).hexdigest()
    result['engines_sha256'] = {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                                for name in ('lens_engine.py', 'unit_engine.py')}
    return result


def example():
    return {'origin': 'synthetic common trigger', 'events': [
        {'id': 'point', 'start': '(1/3) * s', 'end': '(1/3) * s'},
        {'id': 'window', 'start': '(1000/3) * ms', 'end': '0.5 s'},
        {'id': 'later', 'start': '500 ms', 'end': '0.01 min'}]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('demo', 'review'))
    args = parser.parse_args()
    raw = (json.dumps(example(), ensure_ascii=True).encode() if args.command == 'demo'
           else sys.stdin.buffer.read(MAX_BYTES + 1))
    try:
        result = review(raw)
    except (ValueError, units.UnitError, RecursionError) as exc:
        print('dimensioned-order: ' + ascii(str(exc)), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=True, indent=2, allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
