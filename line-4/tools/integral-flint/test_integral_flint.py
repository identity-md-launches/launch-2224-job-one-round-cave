"""Independent exact oracles, dimensional boundaries, and CLI contract checks."""
from fractions import Fraction as F
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest

import integral_flint as tool


class IntegralTests(unittest.TestCase):
    def request(self, **changes):
        request = tool.example()
        request.update(changes)
        return request

    def test_demo_and_clipped_contributions(self):
        result = tool.calculate(tool.example())
        self.assertTrue(result['passes'])
        self.assertEqual(F(result['value']), F(29, 3))
        self.assertEqual([F(s['area_base_value']) for s in result['segments']],
                         [F(3, 1000), F(1, 150)])

    def test_whole_domain_and_knot_selection(self):
        result = tool.calculate(self.request(start='0 s', end='5 s', expect='13 L'))
        self.assertTrue(result['passes'])
        for start, end, value, index in [('0 s', '2 s', '4 L', 0),
                                          ('2 s', '5 s', '9 L', 1)]:
            result = tool.calculate(self.request(start=start, end=end, expect=value))
            self.assertTrue(result['passes'])
            self.assertEqual(len(result['segments']), 1)
            self.assertEqual(result['segments'][0]['left_index'], index)

    def test_mixed_units(self):
        result = tool.calculate(self.request(
            points=[{'x': '0 min', 'y': '60 L/min'},
                    {'x': '2000 ms', 'y': '3000 mL/s'}],
            start='500 ms', end='(1/40) * min', to='mL', expect='2 L'))
        self.assertTrue(result['passes'])
        self.assertEqual(result['value'], '2000')

    def test_force_distance_energy(self):
        result = tool.calculate(self.request(points=[{'x': '0 m', 'y': '1 N'},
                                                     {'x': '2 m', 'y': '3 N'}],
                                             start='0 m', end='2 m', to='J', expect='4 J'))
        self.assertTrue(result['passes'])

    def test_signed_cancellation_and_dimensioned_zero(self):
        result = tool.calculate(self.request(points=[{'x': '-1 s', 'y': '-2 m/s'},
                                                     {'x': '1 s', 'y': '2 m/s'}],
                                             start='-1 s', end='1 s', to='m', expect='0 m'))
        self.assertTrue(result['passes'])
        self.assertEqual(result['value'], '0')
        with self.assertRaises(ValueError):
            tool.calculate(self.request(expect='0 s'))

    def test_nonuniform_segments_independent_oracle(self):
        rng = random.Random(38001)
        for _ in range(300):
            xs = [F(rng.randint(-10, 0))]
            for i in range(rng.randint(1, 8)):
                xs.append(xs[-1] + F(rng.randint(1, 20), rng.randint(1, 9)))
            ys = [F(rng.randint(-30, 30), rng.randint(1, 9)) for x in xs]
            start = xs[0] + (xs[-1] - xs[0]) / 7
            end = xs[-1] - (xs[-1] - xs[0]) / 5
            # Integrate the affine antiderivative, independently of trapezoid code.
            expected = F(0)
            for i in range(len(xs) - 1):
                a, b = max(start, xs[i]), min(end, xs[i+1])
                if a >= b:
                    continue
                slope = (ys[i+1] - ys[i]) / (xs[i+1] - xs[i])
                intercept = ys[i] - slope * xs[i]
                expected += slope * (b*b - a*a) / 2 + intercept * (b-a)
            expr = lambda q, unit: f'({q.numerator}/{q.denominator}) * {unit}'
            request = self.request(points=[{'x': expr(x, 's'), 'y': expr(y, 'm/s')}
                                            for x, y in zip(xs, ys)],
                                   start=expr(start, 's'), end=expr(end, 's'),
                                   to='m', expect=expr(expected, 'm'))
            result = tool.calculate(request)
            self.assertTrue(result['passes'])
            self.assertEqual(F(result['value']), expected)

    def test_partition_and_collinear_invariance(self):
        request = self.request(points=[{'x': '0 s', 'y': '1 m/s'},
                                       {'x': '4 s', 'y': '5 m/s'}],
                               start='0 s', end='4 s', to='m', expect='12 m')
        whole = tool.calculate(request)
        left = tool.calculate(dict(request, end='1 s', expect='1.5 m'))
        right = tool.calculate(dict(request, start='1 s', expect='10.5 m'))
        self.assertEqual(F(whole['value']), F(left['value']) + F(right['value']))
        request['points'].insert(1, {'x': '1 s', 'y': '2 m/s'})
        self.assertEqual(tool.calculate(request)['value'], whole['value'])

    def test_invalid_shapes_and_order(self):
        cases = [self.request(extra=True), self.request(schema='wrong'),
                 self.request(points=[]), self.request(points=tool.example()['points'] * 50),
                 self.request(start='2 s', end='2 s'), self.request(start='5 s', end='1 s'),
                 self.request(start='-1 s'), self.request(end='6 s'),
                 self.request(start='1 m'), self.request(to='m'),
                 self.request(expect='1 s'), self.request(to='-L'),
                 self.request(points=[{'x': '0 s', 'y': '0 L/s'},
                                      {'x': '0 ms', 'y': '1 L/s'}]),
                 self.request(points=[{'x': '2 s', 'y': '0 L/s'},
                                      {'x': '1 s', 'y': '1 L/s'}])]
        for request in cases:
            with self.subTest(request=request), self.assertRaises((ValueError, tool.UnitError)):
                tool.calculate(request)

    def test_invalid_unused_late_point(self):
        request = self.request(start='0 s', end='1 s')
        request['points'].append({'x': '9 s', 'y': '0 kg'})
        with self.assertRaises(ValueError):
            tool.calculate(request)
        request['points'][-1] = {'x': '0 kg', 'y': '0 L/s'}
        with self.assertRaises(ValueError):
            tool.calculate(request)

    def test_loader_rejects_ambiguous_or_unbounded_json(self):
        for raw in [b'{"schema":"a","schema":"b"}', b'{"x":2}', b'{"x":NaN}',
                    b'[[[[[]]]]]', b'\xff', b' ' * (tool.MAX_BYTES+1)]:
            with self.subTest(raw=raw[:80]), self.assertRaises((ValueError, UnicodeError)):
                tool.load(raw)
        request = tool.example()
        self.assertEqual(tool.load(json.dumps(request).encode()), request)

    def test_arithmetic_and_dimension_budgets(self):
        huge = '((2^12)^12)^8'
        request = self.request(points=[{'x': '0 s', 'y': f'({huge}) * m/s'},
                                       {'x': f'({huge}) * s', 'y': f'({huge}) * m/s'}],
                               start='0 s', end=f'({huge}) * s', to='m', expect='0 m')
        with self.assertRaisesRegex(tool.UnitError, '2048-bit arithmetic budget'):
            tool.calculate(request)
        # Each input dimension is legal, but their product exceeds the budget.
        dim = '((m^12)^12)'
        request = self.request(points=[{'x': f'0 * {dim}', 'y': f'1 * {dim}'},
                                       {'x': f'1 * {dim}', 'y': f'2 * {dim}'}],
                               start=f'0 * {dim}', end=f'1 * {dim}', to='m')
        with self.assertRaisesRegex(tool.UnitError, 'dimension exceeds'):
            tool.calculate(request)

    def test_cli_statuses_and_no_partial_output(self):
        script = str(Path(__file__).with_name('integral_flint.py'))
        requests = [(tool.example(), 0), (self.request(expect='10 L'), 1),
                    (self.request(expect='0 s'), 2)]
        for request, status in requests:
            run = subprocess.run([sys.executable, '-B', script, 'run'],
                                 input=json.dumps(request), text=True, capture_output=True)
            self.assertEqual(run.returncode, status, run.stderr)
            if status == 2:
                self.assertEqual(run.stdout, '')
                self.assertTrue(run.stderr)
            else:
                self.assertEqual(json.loads(run.stdout)['passes'], status == 0)


if __name__ == '__main__':
    unittest.main()
