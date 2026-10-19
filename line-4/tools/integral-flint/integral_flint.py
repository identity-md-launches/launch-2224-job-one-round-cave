#!/usr/bin/env python3
"""Exact signed accumulation of a dimensioned piecewise-linear table."""
import argparse
import json
import sys

from engine import Parser, Quantity, UnitError, dimensions, exact_decimal

MAX_BYTES = 65536


def parse(text, target=False):
    if not isinstance(text, str):
        raise ValueError('quantities and units must be expression strings')
    return Parser(text, target=target).parse()


def bound(value, dims):
    return Parser.bounded(Quantity(value, dims), 0).value


def calculate(request):
    required = {'schema', 'points', 'start', 'end', 'to'}
    if (not isinstance(request, dict) or not required <= request.keys()
            or request.keys() - required - {'expect'}):
        raise ValueError('request requires schema, points, start, end, to; optional expect')
    if request['schema'] != 'integral-flint/1':
        raise ValueError('unsupported schema')
    points = request['points']
    if not isinstance(points, list) or not 2 <= len(points) <= 128:
        raise ValueError('points must contain 2..128 entries')
    parsed = []
    for point in points:
        if not isinstance(point, dict) or set(point) != {'x', 'y'}:
            raise ValueError('each point requires exactly x and y')
        x, y = parse(point['x']), parse(point['y'])
        if parsed:
            if x.dims != parsed[0][0].dims or y.dims != parsed[0][1].dims:
                raise ValueError('all x dimensions and all y dimensions must agree')
            if x.value <= parsed[-1][0].value:
                raise ValueError('x coordinates must be strictly increasing')
        parsed.append((x, y))
    xd, yd = parsed[0][0].dims, parsed[0][1].dims
    area_dims = tuple(a + b for a, b in zip(xd, yd))
    bound(parse('0').value, area_dims)
    start, end = parse(request['start']), parse(request['end'])
    if start.dims != xd or end.dims != xd:
        raise ValueError('start and end dimensions must match x')
    if start.value >= end.value:
        raise ValueError('start must be strictly less than end')
    if start.value < parsed[0][0].value or end.value > parsed[-1][0].value:
        raise ValueError('integration window must be inside table; extrapolation is unsupported')
    target = parse(request['to'], target=True)
    if target.dims != area_dims or target.value <= 0:
        raise ValueError('target must have x times y dimensions and positive scale')
    expected = parse(request['expect']) if 'expect' in request else None
    if expected is not None and expected.dims != area_dims:
        raise ValueError('expected dimensions must match x times y')

    total = parse('0').value
    segments = []
    for i, ((x0, y0), (x1, y1)) in enumerate(zip(parsed, parsed[1:])):
        left = max(start.value, x0.value)
        right = min(end.value, x1.value)
        if left >= right:
            continue
        dx = bound(x1.value - x0.value, xd)
        dy = bound(y1.value - y0.value, yd)

        def ordinate(at):
            offset = bound(at - x0.value, xd)
            weight = bound(offset / dx, (0, 0, 0, 0))
            increment = bound(weight * dy, yd)
            return bound(y0.value + increment, yd)

        yl, yr = ordinate(left), ordinate(right)
        width = bound(right - left, xd)
        mean = bound(bound(yl + yr, yd) / 2, yd)
        area = bound(width * mean, area_dims)
        total = bound(total + area, area_dims)
        segments.append({'left_index': i, 'right_index': i + 1,
                         'start_base_value': exact_decimal(left),
                         'end_base_value': exact_decimal(right),
                         'start_y_base_value': exact_decimal(yl),
                         'end_y_base_value': exact_decimal(yr),
                         'area_base_value': exact_decimal(area)})
    result = {'schema': 'integral-flint-result/1',
              'method': 'exact signed piecewise-linear integral',
              'start': request['start'], 'end': request['end'],
              'x_base_unit': dimensions(xd), 'y_base_unit': dimensions(yd),
              'segments': segments,
              'value': exact_decimal(bound(total / target.value, area_dims)),
              'unit': request['to'], 'base_value': exact_decimal(total),
              'base_unit': dimensions(area_dims), 'passes': True}
    if expected is not None:
        difference = bound(total - expected.value, area_dims)
        result['check'] = {'expression': request['expect'], 'matches': difference == 0,
                           'difference_base_value': exact_decimal(difference)}
        result['passes'] = difference == 0
    return result


def reject(value):
    raise ValueError('JSON numeric values are unsupported; use expression strings')


def unique(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError('duplicate JSON key: ' + key)
        obj[key] = value
    return obj


def load(raw):
    if len(raw) > MAX_BYTES:
        raise ValueError('input exceeds 65536 bytes')
    text = raw.decode('utf-8')
    depth = 0
    quoted = escaped = False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in '[{':
            depth += 1
            if depth > 4:
                raise ValueError('JSON nesting exceeds four levels')
        elif char in ']}':
            depth -= 1
    return json.loads(text, object_pairs_hook=unique, parse_int=reject,
                      parse_float=reject, parse_constant=reject)


def example():
    return {'schema': 'integral-flint/1',
            'points': [{'x': '0 s', 'y': '0 L/s'},
                       {'x': '2 s', 'y': '4 L/s'},
                       {'x': '5 s', 'y': '2 L/s'}],
            'start': '1 s', 'end': '4 s', 'to': 'L',
            'expect': '(29/3) * L'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['run', 'demo'])
    args = parser.parse_args(argv)
    try:
        request = example() if args.command == 'demo' else load(sys.stdin.buffer.read(MAX_BYTES + 1))
        result = calculate(request)
    except (ValueError, TypeError, UnicodeError, UnitError, OverflowError) as exc:
        print('integral-flint: ' + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0 if result['passes'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
