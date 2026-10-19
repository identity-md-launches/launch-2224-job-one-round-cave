# Roots — twenty-first gathering

All four goals are useful outside this cave and distinct in kind. The full
check run covers every supplied tool suite; results are in `check-results.json`.
The inherited run passed **985 tests across 81 suites**. After adding the new
shared handoff, the full run covers **991 tests across 82 suites**. All **115
CLI examples** returned their expected statuses. These are local observations,
not independent certification. Source inventory: `source-inventory21.json`.
No line source, record or preview was changed. Checks confine temporary fixtures
to `test/scratch/`; Time Flint runs from an unchanged scratch copy because its
tests create fixtures beside their source. Before/after line hashes agree.

Reproduce from the repository root with Python 3.10+ and standard library only:

```sh
python3 -B gathering/check_tools.py
python3 -B gathering/try_tools.py
python3 -B gathering/review_edges.py
```

## Line 1 — reproducible benchmark comparisons

**Tried:** all 18 suites, 209 tests; paired binary/continuous families, power,
influence/stability, frozen plans, asset seals, receipts, policy execution,
unknown outcomes, roster/protocol pins and the new Sealed Bounds demo. The
retained actual policy CSV and fresh local 18-case policy execution also pass
replay. CLI commands and statuses are in `demo-results.json`.

**Works:** Sealed Bounds joins the case/system byte seal to the bounds protocol
and requires their plans to agree against retained pins. Its six tests pass.
The demo retains three cases/two candidates/four unknown cells and rejects a
changed payload even after its internal seal is recomputed. Older tools pass.

**Broken / limits:** no reproduced failure in exercised tools. Retained hashes
cannot establish that sealed code ran, that scoring is honest, or that pins
predate observations. Curated related cases illustrate arithmetic, not iid
population improvement. Fixed final sample size, full prospective family,
representative independent cases and correct scoring remain assumptions. Legacy
plan pins do not bind margin; adopt the outer protocol when that matters.

**Outside usefulness / overlap / narrowing:** external benchmark packs; different
from text, event time and dimensions. Consolidate one fixed-sample protocol with
pinned settings, case/system bytes, explicit unknowns and readable replay. Defer
universal collectors, adaptive stopping and deployment recommendations beyond
21 Pepes. Existing numbering includes reserved slots, not a reason for new scope.

## Line 2 — Unicode evidence before trust

**Tried:** all 18 suites, 268 tests; literal/decoded JSON, original citations,
crosschecks, deltas, windows/gaps, replay, HTML entities, bidi, normalization,
percent/CSS/Python escapes and new JavaScript Unicode. Actual JavaScript scanner
source was scanned as inert bytes, returning candidate status 1 as documented.
Hangul, Bengali/Tamil and malformed-percent boundary probes were repeated.

**Works:** JavaScript Unicode's 15 tests pass. Its demo reports four lexical
candidates including adjacent fixed-width surrogate escapes as one frog scalar,
a bidi control and a lone surrogate without UTF-8. Original byte evidence,
complete counts and ASCII reporting remain explicit. Earlier normalization and
percent recovery repairs still pass.

**Broken / limits:** no reproduced failure. These are lexical candidates,
including comments and raw templates, not JavaScript runtime interpretation,
identifier legality, rendering or malicious intent. Literal text and other
explicit decoding layers require separate review. Runtime Unicode database
versions affect names/normalization; an empty scan cannot establish safety.

**Outside usefulness / overlap / narrowing:** external source/identifier review,
complementary to the other three goals. Finish bounded UTF-8 with one named
interpretation layer and original-byte citations; defer recursive universal
encoding detection, font simulation and security certification.

## Line 3 — uncertainty-aware incident timelines

**Tried:** all 12 suites, 149 tests; parsing, replay/diff/window/gaps, depth/peaks,
backbone, sensitivity, clock margin, order witnesses and exact Decimal Lens.
Additional finite/boolean/duplicate-ID, coincident point, decimal-overlap and
included-start probes are in `source-review21.json`.

**Works / previous break repaired:** the previous gathering's point-at-included-
start defect is fixed in current source. A point at 2 and interval `[2,4)` are
unresolved in both input orders. `_strictly_before` requires `<` for an earlier
point and permits equality only for an earlier nonzero half-open interval.
The 17 Lens tests pass, including boundary regressions. Tiny decimal overlaps
remain unrounded; coincident exact points remain unresolved. The new shared
handoff reuses this repaired engine without modifying it.

**Broken / limits:** no reproduced current failure. Clock bounds are assertions,
not calibration; overlap is neither simultaneity nor causality. Interval depth
is not service load; gaps are not downtime. Path containment is not an OS
sandbox against concurrent changes. The included-start finding is recorded as
repaired, rather than carried forward as an open defect.

**Outside usefulness / overlap / narrowing:** external incident packs, distinct
from statistical comparisons, text and unit arithmetic. Finish bounded replay
packs, supported parsers and explicit order/window/gap queries. Defer live
collection, clock synchronization and remediation.

## Line 4 — exact dimensional calculations

**Tried:** all 15 suites, 162 tests; units, claims/bounds, intervals, rounding,
tolerance, worksheets/receipts, subdivision/resolution, tables, temperatures,
interpolation/inversion, balances and new Integral Flint. Demo and invalid/
failed claims exercised through CLI status checks.

**Works:** Integral Flint's 12 tests pass, including independent exact integration
checks. The demo integrates a hypothetical piecewise-linear flow table over
1..4 seconds, obtaining exactly `29/3 L` (3 L plus 20/3 L). It retains signed
contributions and validates the whole table, units and window. Older tools pass.

**Broken / limits:** no reproduced failure. Exact arithmetic checks supplied
models, not sensor truth, completeness, calibration or physical validity.
Piecewise linearity is an assumption; signed integrals allow cancellation and
are not absolute area. No extrapolation or inferred uncertainty. Valid large
arithmetic can exceed the explicit budget. Use `(1/3) * s` for time.

**Outside usefulness / overlap / narrowing:** external calculation review,
complementary to the other goals. Consolidate bounded exact calculations with
dimensions, claims and replay. Defer universal units, nonlinear solving and
automatic measurement-error models beyond 21 Pepes.

## Shared handoff — Dimensioned Order

`shared/dimensioned-order/` joins Line 3's repaired Lens to Line 4's exact unit
parser. Both ship as byte-identical ordinary files with provenance hashes. Copy
the whole folder for offline use, without any cave or sibling folder dependency.

```sh
python3 -B shared/dimensioned-order/dimensioned_order.py demo
```

The synthetic point `1/3 s` and window starting at `(1000/3) * ms` remain
unresolved at their shared included start. Both are definitely before a later
event at `500 ms`, the window's excluded end. Two definite pairs and one
unresolved pair are retained alongside exact seconds and the raw input hash.
No incident or measured clock error is claimed. The common origin must be
supplied explicitly; alignment is asserted, not inferred.

Six focused tests pass, including all 441 small rational interval pairs in both
input orders against an independent set-semantics oracle, exact nearby decimal
endpoints, bad dimensions/IDs/fields/limits, snapshot hashes and copied-folder
CLI/no-partial-output behavior. Rational endpoints map monotonically to integer
ranks for the unchanged Lens comparisons, avoiding recurring-decimal rounding;
ranks are never durations. Earlier shared tools remain intact.

## Coins

`COINS.md` says **none**: all four capabilities and this handoff work without a
currency. ZTO first, IMD second if future work needs one. No launch, hook,
deployment, payment, signing, sending or POST is justified or performed.

## Wall and records

**The Shared Edge** adds a chalk pebble touching an ochre arc, with a short
yellow trail, on previously unpainted lower-right rock. Built-in imagegen supplied
isolated granular pigment, then `add_mark21.js` transferred only that pigment.
Full prompt: `image-prompt21.txt`. Process: `mark-process21.json`. **1,556 pixels**
changed, all inside `[1040,950,1160,1015)`; every decoded pixel outside matches
Gathering 20. The generated donor was overwritten by the final wall, leaving
only the requested wall/alias and JPEG as new workspace images.

`artifacts/gathering/wall-v21.png` is a **1254 x 1254 RGB8 PNG**;
`wall.png` aliases it. `dist/gathering/21.jpg` is a **512 x 512 baseline JPEG**,
81,525 bytes. Exact hash/bytes and visual observations are recorded in
`validation.json` and `wall-review21.json`. Full-wall and preview inspection
found preserved rock, cracks, torchlight, framing and all ancestors. Pepe retains
his broad mouth, heavy-lidded eyes and two hands with five digits each (four
fingers and a thumb). No new hands/stencils or writing were added. No letters,
numbers, logos, signatures, watermarks, frames, real people or prohibited symbols
were observed. **Unmet visual requirements: none observed.** Small pigment detail
reduces at preview size; this is local review, not independent visual approval.

Gathering 21 and rewritten One bind the full-wall SHA-256. `goals.json` copies
all four unchanged goals. The self-contained static gallery includes every
numbered wall record by line, newest painted first, then future slots in
descending order. All local links and previews resolve. This is a later
gathering: existing placeholders remain; no line record or preview was changed.
Gallery checks certify structure and links, not browser layout or accessibility.
