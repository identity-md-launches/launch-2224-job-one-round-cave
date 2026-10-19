# Sealed Bounds

Join the line's two prospective evidence tracks into **one checked receipt**.
Benchmark Seal binds the actual case and system bundle bytes to a Frozen
Benchmark plan. Bound Protocol binds that same plan to a practical margin and
missing-row policy, then computes simultaneous bounds over incomplete binary
outcomes. This tool verifies both against separately retained pins, requires the
plans to agree exactly, admits the observations once, and emits one JSON receipt
with the asset digests, settings, unknown counts, bounds and normalized CSV hash.
Python 3.10+ and the standard library are enough; copy this entire folder to
use it offline.

From the repository root, one command shows the complete join working:

```sh
python3 -B line-1/tools/sealed-bounds/sealed_bounds.py demo
```

When tried locally, the synthetic demo retained all three planned cases and
both candidates. Its omitted `unicode` row became three explicit unknown cells
under the pinned `restore-as-unknown` policy; one supplied cell was also unknown.
The receipt showed six sealed asset byte digests, the actual simultaneous
bounds and the admitted CSV digest. A changed case payload with a **recomputed
internal seal** failed against the original external seal pin. The full actual
stdout is in `example-run.json`. These authored fixtures are not measurements of
systems or evidence of an improvement.

## Use on a fixed benchmark

First create and independently retain the Frozen Benchmark plan SHA-256. Before
outcomes, make the complete case/system pack with Benchmark Seal and the bounds
protocol with Bound Protocol. Independently retain their seal and protocol
SHA-256 values too. Those ordinary source snapshots are present in this folder:

* `benchmark_seal.py` + `frozen_engine.py` bind case and system bytes.
* `bound_protocol.py` + `roster_bounds.py` + `missing_bounds.py` +
  `bounds_engine.py` bind margin/policy and analyze complete or unknown results.

Keep the original pack and protocol, not just their hashes. At the fixed
endpoint, retain the raw CSV SHA-256 independently at handoff. Then supply the
four retained values (not values copied from the untrusted files being checked):

```sh
python3 -B line-1/tools/sealed-bounds/sealed_bounds.py check --protocol PROTOCOL.json --pack PACK.json --results RESULTS.csv --expected-plan-sha256 RETAINED_PLAN_SHA256 --expected-protocol-sha256 RETAINED_PROTOCOL_SHA256 --expected-seal-sha256 RETAINED_SEAL_SHA256 --expected-results-sha256 RETAINED_RESULTS_SHA256
```

The command prints JSON only after all checks succeed. `--emit-csv` instead
prints only the fully admitted, planned-order CSV after the same checks. Exit 0
means the supplied material is consistent, including an inconclusive analysis;
exit 2 means an input or pin failed, with no partial stdout. Input files must
resolve to regular files inside the working directory and are read at most 2 MiB
each. Nothing is written, executed, fetched, posted or sent by the tool.

The output keeps the asset **digests and sizes**, not the payload bytes. The pack
itself contains its base64 payloads and may contain private data; review it
before sharing. The receipt's nested `bounds` report retains the full family,
unknown counts, intervals and strict margin decisions. Keep the raw CSV and pack
alongside the receipt so a later worker can replay the check. The two inner
engines remain byte-identical to their originals; `provenance.json` records each
source hash.

## Interpretation and limits

This join closes the bookkeeping gap between the asset seal and the bounds
protocol. It cannot verify that the sealed code ran, that the sealed cases were
sampled representatively, that scoring was honest, or that pins really preceded
observations. The independent retention process must establish timing and
authenticity. Population coverage additionally assumes fixed final sample size,
an unchanged full candidate family, independent identically distributed latent
case vectors and correct scoring. Unknown results stay unknown; restoring an
omitted row does not measure it. Do not use repeated looks to stop when a bound
first clears a margin. An inconclusive interval is not evidence of equivalence.

The tool needs no coin, price, pool, balance or payment; it operates only on
locally supplied benchmark bytes. It never reads environment variables, keys,
wallets or files outside the selected workspace.

## Checks

```sh
python3 -B -m unittest discover -s line-1/tools/sealed-bounds -v
```

Six local tests passed: a complete joined receipt with unknowns, each retained
pin, disagreement between two otherwise valid plans, refusal of omitted rows
under the reject policy, a rehashed payload replacement, and the CLI demo. These
check the integration behavior; they do not certify benchmark validity.
