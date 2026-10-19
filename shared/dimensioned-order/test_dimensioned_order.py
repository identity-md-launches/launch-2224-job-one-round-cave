"""Independent rational set-order checks, input rejection and offline portability."""
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import dimensioned_order as app

HERE = Path(__file__).resolve().parent


class OrderTests(unittest.TestCase):
    def test_demo_recurring_fraction_and_included_start(self):
        result = app.analyze(app.example())
        self.assertEqual(result['endpoints_seconds'][0]['start'], '1/3')
        self.assertEqual(result['endpoints_seconds'][1]['start'], '1/3')
        self.assertEqual(len(result['analysis']['definite_orders']), 2)
        self.assertEqual(result['analysis']['uncertain_pairs'], [
            {'events': ['point', 'window'], 'reason': 'intervals overlap'}])

    def test_exhaustive_rational_set_semantics(self):
        # Independent oracle: every possible left time is less than every
        # possible right time iff endpoints separate, with the left supremum
        # excluded at equality. No call to the inherited predicate here.
        values = [Fraction(i, 3) for i in range(-2, 4)]
        intervals = list(itertools.combinations_with_replacement(values, 2))
        for (a, b), (c, d) in itertools.product(intervals, repeat=2):
            events = [{'id': 'a', 'start': f'({a}) * s', 'end': f'({b}) * s'},
                      {'id': 'b', 'start': f'({c * 1000}) * ms', 'end': f'({d * 1000}) * ms'}]
            expected = []
            if b < c or (b == c and a != b):
                expected = [{'before': 'a', 'after': 'b'}]
            elif d < a or (d == a and c != d):
                expected = [{'before': 'b', 'after': 'a'}]
            for ordered in (events, list(reversed(events))):
                out = app.analyze({'origin': 'asserted', 'events': ordered})['analysis']
                self.assertEqual(out['definite_orders'], expected)
                self.assertEqual(len(out['definite_orders']) + len(out['uncertain_pairs']), 1)

    def test_invalid_dimensions_ids_shapes_and_limits(self):
        for value in ('0', '0 m', 's / m', '1 / 0', 's^13', '1e999 s'):
            with self.subTest(value=value), self.assertRaises((ValueError, app.units.UnitError)):
                app.analyze({'origin': 'a', 'events': [{'id': 'a', 'start': value, 'end': '1 s'}]})
        for value in ({}, {'origin': '', 'events': []}, {'origin': 'a', 'events': [None]},
                      {'origin': 'a', 'events': [{'id': 'a', 'start': '2 s', 'end': '1 s'}]},
                      {'origin': 'a', 'events': app.example()['events'] * 2},
                      {'origin': 'a', 'events': [app.example()['events'][0]] * 129}):
            with self.subTest(value=str(value)[:60]), self.assertRaises(ValueError):
                app.analyze(value)
        for raw in (b'{"origin":"a","origin":"b","events":[]}', b'NaN', b'\xff',
                    b' ' * (app.MAX_BYTES + 1)):
            with self.assertRaises(ValueError):
                app.review(raw)

    def test_exact_nearby_endpoints_never_merge(self):
        result = app.analyze({'origin': 'a', 'events': [
            {'id': 'a', 'start': '0 s', 'end': '1.00000000000000003 s'},
            {'id': 'b', 'start': '1.00000000000000002 s', 'end': '2 s'}]})
        self.assertEqual(result['analysis']['definite_orders'], [])

    def test_byte_hash_and_snapshots(self):
        raw = json.dumps(app.example()).encode()
        self.assertEqual(app.review(raw)['input_sha256'], hashlib.sha256(raw).hexdigest())
        for row in json.loads((HERE / 'provenance.json').read_text()):
            self.assertEqual(hashlib.sha256((HERE / row['copy']).read_bytes()).hexdigest(), row['sha256'])

    def test_copied_cli_and_no_partial_output(self):
        scratch = Path('test/scratch').resolve()
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as temporary:
            folder = Path(temporary) / 'portable'
            shutil.copytree(HERE, folder)
            command = [sys.executable, '-B', str(folder / 'dimensioned_order.py')]
            demo = subprocess.run(command + ['demo'], cwd=folder, capture_output=True, timeout=10)
            self.assertEqual(demo.returncode, 0, demo.stderr)
            self.assertEqual(json.loads(demo.stdout)['analysis']['events'], 3)
            for raw in (b'{}', b'{"origin":"a","events":[{"id":"a","start":"0 s","end":true}]}',
                        b' ' * (app.MAX_BYTES + 1)):
                bad = subprocess.run(command + ['review'], cwd=folder, input=raw,
                                     capture_output=True, timeout=10)
                self.assertEqual(bad.returncode, 2)
                self.assertEqual(bad.stdout, b'')


if __name__ == '__main__':
    unittest.main()
