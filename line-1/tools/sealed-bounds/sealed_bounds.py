#!/usr/bin/env python3
"""Check sealed benchmark assets and pinned incomplete-result bounds together."""
import argparse
import base64
import json
import sys

import benchmark_seal as seal
import bound_protocol as bounds
import frozen_engine as frozen


def audit(protocol_raw, pack_raw, results_raw, plan_pin, protocol_pin,
          seal_pin, results_pin):
    """Return one receipt and admitted CSV, after checking four external pins."""
    bounds.pin(plan_pin, 'plan pin')
    protocol = bounds.verify(protocol_raw, protocol_pin)
    if protocol['manifest']['plan_sha256'] != plan_pin:
        raise ValueError('protocol plan differs from independently retained plan pin')

    # The seal checker validates the complete payloads, their membership and
    # order, and its own independently retained pin before any interpretation.
    seal_report, _ = seal.verify(pack_raw, seal_pin)
    sealed_pack = frozen.parse_json(pack_raw)
    if sealed_pack['content']['manifest'] != protocol['manifest']:
        raise ValueError('sealed assets and bounds protocol name different plans')
    if seal_report['plan_sha256'] != plan_pin:
        raise ValueError('sealed asset plan differs from independently retained plan pin')

    bound_report, admitted_csv = bounds.check(
        protocol_raw, results_raw, protocol_pin, results_pin)
    roster = bound_report['roster_report']
    if roster['plan_sha256'] != plan_pin or roster['normalized_csv_sha256'] != frozen.digest(admitted_csv):
        raise ValueError('bound analysis and admitted rows disagree')
    receipt = {
        'schema': 'sealed-bounds-receipt-v1',
        'status': 'pinned_assets_protocol_and_observations_agree',
        'pins': {'plan_sha256': plan_pin, 'protocol_sha256': protocol_pin,
                 'seal_sha256': seal_pin, 'results_sha256': results_pin},
        'source_bytes': {'protocol_sha256': frozen.digest(protocol_raw),
                         'pack_sha256': frozen.digest(pack_raw),
                         'results_sha256': frozen.digest(results_raw)},
        'sealed_assets': seal_report['assets'],
        'bounds': bound_report,
        'admitted_csv_sha256': frozen.digest(admitted_csv),
        'limits': [
            'Retain the plan, protocol and seal pins independently before observations, and the raw results pin at handoff.',
            'The receipt binds supplied bytes and settings; it cannot prove that those bytes were executed or scored honestly.',
            'Unknown cells are preserved, not imputed. Missing rows follow only the pinned omission policy.',
            'Fixed endpoint, representative independent cases, full family and correct scoring remain assumptions.'
        ]
    }
    return receipt, admitted_csv


def demo():
    plan = {'schema': frozen.SCHEMA, 'baseline': 'synthetic-base-v1',
            'candidates': ['synthetic-a-v1', 'synthetic-b-v1'],
            'pass_rule': 'Synthetic exact-match fixture only.', 'alpha': '0.05',
            'cases': ['empty', 'unicode', 'truncated']}
    manifest = frozen.freeze(frozen.canonical(plan))
    plan_pin = manifest['plan_sha256']
    protocol = bounds.freeze(frozen.canonical(manifest), plan_pin, '0.1',
                             'restore-as-unknown')
    content = {'manifest': manifest,
               'cases': [{'id': name, 'data_b64': base64.b64encode(
                   ('synthetic case payload: ' + name).encode()).decode()}
                         for name in plan['cases']],
               'systems': [{'id': name, 'data_b64': base64.b64encode(
                   ('synthetic system bundle: ' + name).encode()).decode()}
                           for name in [plan['baseline']] + plan['candidates']]}
    pack = seal.seal(frozen.canonical(content), plan_pin)
    raw = (b'case,baseline,synthetic-a-v1,synthetic-b-v1\n'
           b'empty,1,1,1\ntruncated,0,1,?\n')
    pins = (plan_pin, protocol['protocol_sha256'], pack['seal_sha256'],
            frozen.digest(raw))
    receipt, admitted = audit(frozen.canonical(protocol), frozen.canonical(pack),
                              raw, *pins)
    replacement = json.loads(json.dumps(pack))
    replacement['content']['cases'][0]['data_b64'] = base64.b64encode(
        b'changed synthetic case').decode()
    replacement['seal_sha256'] = frozen.digest(frozen.canonical(replacement['content']))
    try:
        audit(frozen.canonical(protocol), frozen.canonical(replacement), raw, *pins)
    except ValueError as exc:
        rejection = str(exc)
    else:
        raise RuntimeError('replacement payload passed the retained seal pin')
    return {'data_kind': 'synthetic_demonstration', 'receipt': receipt,
            'admitted_csv': admitted.decode(), 'rehashed_replacement_rejected': rejection}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('demo')
    check = sub.add_parser('check')
    for option in ('protocol', 'pack', 'results', 'expected-plan-sha256',
                   'expected-protocol-sha256', 'expected-seal-sha256',
                   'expected-results-sha256'):
        check.add_argument('--' + option, required=True)
    check.add_argument('--emit-csv', action='store_true')
    args = parser.parse_args(argv)
    try:
        if args.command == 'demo':
            result = demo()
        else:
            result, admitted = audit(
                frozen.read_workspace(args.protocol), frozen.read_workspace(args.pack),
                frozen.read_workspace(args.results), args.expected_plan_sha256,
                args.expected_protocol_sha256, args.expected_seal_sha256,
                args.expected_results_sha256)
            if args.emit_csv:
                sys.stdout.buffer.write(admitted)
                return 0
    except (ValueError, OSError, TypeError, RecursionError) as exc:
        parser.exit(2, 'error: ' + str(exc)[:240] + '\n')
    print(json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
