"""Offline regression tests; no submitted text is executed."""
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import shutil
import tempfile
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('javascript_unicode', HERE / 'javascript_unicode.py')
u = importlib.util.module_from_spec(spec)
spec.loader.exec_module(u)


class EscapeTests(unittest.TestCase):
    def values(self, data):
        return [None if d['decoded_codepoint'] is None else d['decoded_codepoint']['codepoint']
                for d in u.scan(data)['details']]

    def test_demo(self):
        r = u.scan(u.DEMO)
        self.assertEqual(r['candidate_count'], 4)
        self.assertEqual(self.values(u.DEMO), ['U+0456', 'U+1F438', 'U+202E', 'U+D800'])
        self.assertEqual(r['details'][1]['form'], 'fixed-surrogate-pair')

    def test_fixed_against_json_decoder(self):
        rng = random.Random(737)
        for value in [0, 0x7f, 0xd7ff, 0xd800, 0xdfff, 0xe000, 0xffff] + [rng.randrange(65536) for _ in range(600)]:
            token = ('\\u%04x' % value).encode()
            decoded = json.loads('"' + token.decode() + '"')
            self.assertEqual(self.values(token), ['U+%04X' % ord(decoded)])

    def test_pairs_against_json_decoder(self):
        rng = random.Random(39)
        for _ in range(600):
            hi, lo = rng.randrange(0xd800, 0xdc00), rng.randrange(0xdc00, 0xe000)
            token = ('\\u%04x\\u%04x' % (hi, lo)).encode()
            expected = json.loads('"' + token.decode() + '"')
            self.assertEqual(self.values(token), ['U+%04X' % ord(expected)])
            d = u.scan(token)['details'][0]
            self.assertEqual(d['component_byte_ranges'], [[0, 6], [6, 12]])
            self.assertEqual(d['source_byte_range'], [0, 12])

    def test_braced_and_zeroes(self):
        self.assertEqual(self.values(br'\u{0000001f438}\u{10ffff}\u{0}'), ['U+1F438', 'U+10FFFF', 'U+0000'])
        self.assertEqual(self.values(b'\\u{' + b'0' * 10000 + b'41}'), ['U+0041'])
        d = u.scan(br'\u{110000}')['details'][0]
        self.assertEqual(d['issue'], 'out-of-range')

    def test_braced_surrogates_not_combined(self):
        self.assertEqual(self.values(br'\u{d83d}\u{dc38}'), ['U+D83D', 'U+DC38'])
        self.assertEqual(self.values(br'\uD83D\u{DC38}'), ['U+D83D', 'U+DC38'])
        self.assertEqual(self.values(br'\u{D83D}\uDC38'), ['U+D83D', 'U+DC38'])

    def test_pair_adjacency_and_order(self):
        self.assertEqual(self.values(br'\uD83D \uDC38'), ['U+D83D', 'U+DC38'])
        self.assertEqual(self.values(br'\uDC38\uD83D'), ['U+DC38', 'U+D83D'])
        self.assertEqual(self.values(br'\uD800\uD83D\uDC38'), ['U+D800', 'U+1F438'])
        self.assertEqual(self.values(br'\uD83D\uDC38\uDC38'), ['U+1F438', 'U+DC38'])

    def test_surrogate_has_no_utf8(self):
        self.assertIsNone(u.scan(br'\uD800')['details'][0]['decoded_codepoint']['utf8_hex'])
        self.assertEqual(u.scan(br'\uD83D\uDC38')['details'][0]['decoded_codepoint']['utf8_hex'], 'f09f90b8')

    def test_parity_and_nonrecursive(self):
        for n in range(1, 12):
            self.assertEqual(u.scan(b'\\' * n + b'u0041')['candidate_count'], n % 2)
        self.assertEqual(self.values(br'\u005cu202e'), ['U+005C'])
        self.assertEqual(self.values(br'\U0001f438\x41\n'), [])

    def test_malformed_recovery(self):
        for prefix in [br'\u', br'\u12', br'\u{', br'\u{12', br'\u{}', br'\u{z', br'\u{110000}']:
            r = u.scan(prefix + br'\u202e')
            self.assertEqual(r['candidate_count'], 2)
            self.assertEqual(r['details'][0]['kind'], 'malformed')
            self.assertEqual(r['details'][1]['decoded_codepoint']['codepoint'], 'U+202E')
        self.assertEqual(self.values(br'\uD83D\u00Z\u202e'), ['U+D83D', None, 'U+202E'])

    def test_original_byte_citations(self):
        data = 'é\n🐸x'.encode() + br'\u{456}' + b'\r\n' + br'\uD83D\uDC38'
        r = u.scan(data)
        self.assertEqual(r['source_sha256'], hashlib.sha256(data).hexdigest())
        for d, loc in zip(r['details'], [(2, 6), (3, 1)]):
            lo, hi = d['source_byte_range']
            raw = data[lo:hi]
            self.assertEqual(d['source_escape_hex'], raw.hex())
            self.assertEqual(d['source_span_sha256'], hashlib.sha256(raw).hexdigest())
            self.assertEqual((d['source_line'], d['source_byte_column']), loc)
        self.assertTrue(json.dumps(r, ensure_ascii=True).isascii())

    def test_caps_preserve_complete_counts(self):
        data = (br'\u{456}\uD83D\uDC38\uD800\u{}' * 2000)
        full, capped = u.scan(data, 1000), u.scan(data, 0)
        self.assertEqual(full['counts_by_kind'], capped['counts_by_kind'])
        self.assertEqual(capped['candidate_count'], 8000)
        self.assertEqual(capped['omitted_details'], 8000)
        self.assertTrue(capped['analysis_complete'])

    def test_size_and_type_validation(self):
        for bad in ['text', bytearray(b'text'), b'x' * (u.MAX_BYTES + 1), b'\xff']:
            with self.assertRaises((ValueError, UnicodeError)):
                u.scan(bad)
        for cap in [True, -1, 1001, 0.5]:
            with self.assertRaises(ValueError):
                u.scan(b'', cap)
        self.assertEqual(u.scan(b'')['candidate_count'], 0)

    def test_maximum_input(self):
        token = br'\u0041'
        n = u.MAX_BYTES // len(token)
        data = token * n + b' ' * (u.MAX_BYTES % len(token))
        r = u.scan(data, 0)
        self.assertEqual(r['candidate_count'], n)
        self.assertEqual(r['retained_details'], 0)
        self.assertEqual(r['counts_by_kind'], {'ascii': n})

    def test_portable_folder_and_containment(self):
        scratch = Path('test/scratch').resolve()
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as tmp:
            root = Path(tmp)
            portable = root / 'portable'
            portable.mkdir()
            shutil.copyfile(HERE / 'javascript_unicode.py', portable / 'javascript_unicode.py')
            demo = subprocess.run([sys.executable, '-B', 'javascript_unicode.py', '--demo'],
                                  cwd=portable, capture_output=True)
            self.assertEqual(demo.returncode, 0)
            self.assertEqual(json.loads(demo.stdout)['candidate_count'], 4)
            (root / 'outside.txt').write_bytes(b'ordinary fixture')
            (portable / 'link.txt').symlink_to(root / 'outside.txt')
            for name in ['../outside.txt', 'link.txt', '.']:
                result = subprocess.run([sys.executable, '-B', 'javascript_unicode.py', '--file', name],
                                        cwd=portable, capture_output=True)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, b'')
                if name != '.':
                    self.assertIn('within the current working directory', json.loads(result.stderr)['error'])

    def test_cli(self):
        script = str(HERE / 'javascript_unicode.py')
        def run(*args):
            return subprocess.run([sys.executable, '-B', script, *args], capture_output=True)
        demo = run('--demo')
        self.assertEqual(demo.returncode, 0)
        self.assertEqual(json.loads(demo.stdout)['source_kind'], 'synthetic-demo')
        actual = run('--file', script, '--max-details', '0')
        self.assertEqual(actual.returncode, 1)
        self.assertGreater(json.loads(actual.stdout)['candidate_count'], 0)
        invalid = run('--demo', '--max-details', '-1')
        self.assertEqual(invalid.returncode, 2)
        self.assertEqual(invalid.stdout, b'')
        outside = run('--file', '../outside-workspace')
        self.assertEqual(outside.returncode, 2)
        self.assertEqual(outside.stdout, b'')


if __name__ == '__main__':
    unittest.main()
