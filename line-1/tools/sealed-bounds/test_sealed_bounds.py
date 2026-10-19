import base64
import json
import subprocess
import sys
import unittest
from pathlib import Path

import benchmark_seal as seal
import bound_protocol as bounds
import frozen_engine as frozen
import sealed_bounds as joined


def fixture(policy='restore-as-unknown', changed_plan=False):
    plan = {'schema': frozen.SCHEMA, 'baseline': 'b',
            'candidates': ['a', 'c'], 'pass_rule': 'synthetic exact match',
            'alpha': '0.05', 'cases': ['one', 'two']}
    manifest = frozen.freeze(frozen.canonical(plan))
    protocol = bounds.freeze(frozen.canonical(manifest), manifest['plan_sha256'],
                             '0.1', policy)
    sealed_plan = dict(plan)
    if changed_plan:
        sealed_plan['pass_rule'] = 'another synthetic rule'
    sealed_manifest = frozen.freeze(frozen.canonical(sealed_plan))
    pack = seal.seal(frozen.canonical({
        'manifest': sealed_manifest,
        'cases': [{'id': name, 'data_b64': base64.b64encode(name.encode()).decode()}
                  for name in plan['cases']],
        'systems': [{'id': name, 'data_b64': base64.b64encode(name.encode()).decode()}
                    for name in ['b', 'a', 'c']]}), sealed_manifest['plan_sha256'])
    raw = b'case,baseline,a,c\none,1,1,?\n'
    args = [frozen.canonical(protocol), frozen.canonical(pack), raw,
            manifest['plan_sha256'], protocol['protocol_sha256'],
            pack['seal_sha256'], frozen.digest(raw)]
    return args


class JoinedEvidenceTest(unittest.TestCase):
    def test_complete_join_retains_unknown_and_seal_summary(self):
        report, csv = joined.audit(*fixture())
        self.assertEqual(report['status'], 'pinned_assets_protocol_and_observations_agree')
        self.assertEqual(report['admitted_csv_sha256'], frozen.digest(csv))
        self.assertIn(b'two,?,?,?\n', csv)
        self.assertEqual(report['bounds']['roster_report']['analysis']['missing_cells'], 4)
        self.assertEqual(len(report['sealed_assets']['cases']), 2)
        self.assertEqual(len(report['sealed_assets']['systems']), 3)

    def test_each_external_pin_is_required(self):
        args = fixture()
        for offset in range(3, 7):
            altered = list(args)
            altered[offset] = '0' * 64
            with self.subTest(pin=offset), self.assertRaises(ValueError):
                joined.audit(*altered)

    def test_two_valid_but_different_plans_cannot_be_joined(self):
        with self.assertRaisesRegex(ValueError, 'different plans'):
            joined.audit(*fixture(changed_plan=True))

    def test_omission_policy_is_enforced(self):
        with self.assertRaisesRegex(ValueError, 'omitted'):
            joined.audit(*fixture(policy='reject'))

    def test_payload_replacement_with_rehashed_internal_seal_is_rejected(self):
        args = fixture()
        pack = json.loads(args[1])
        pack['content']['cases'][0]['data_b64'] = base64.b64encode(b'replacement').decode()
        pack['seal_sha256'] = frozen.digest(frozen.canonical(pack['content']))
        args[1] = frozen.canonical(pack)
        with self.assertRaisesRegex(ValueError, 'seal mismatch'):
            joined.audit(*args)

    def test_cli_demo_is_json(self):
        script = Path(__file__).with_name('sealed_bounds.py')
        run = subprocess.run([sys.executable, '-B', str(script), 'demo'],
                             capture_output=True, check=True, text=True)
        value = json.loads(run.stdout)
        self.assertEqual(value['data_kind'], 'synthetic_demonstration')
        self.assertIn('seal mismatch', value['rehashed_replacement_rejected'])


if __name__ == '__main__':
    unittest.main()
