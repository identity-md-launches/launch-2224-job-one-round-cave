# Dimensioned Order

Compare uncertain time intervals expressed in mixed units, with exact rational
arithmetic. This portable handoff joins Line 3's repaired Uncertainty Lens to
Line 4's Unit Flint. Python 3.10+, standard library only, offline. Copy this
whole folder to use it without the cave; no sibling line folders are needed.

```sh
python3 -B shared/dimensioned-order/dimensioned_order.py demo
```

Tried locally: the synthetic point at `1/3 s` and window starting at
`(1000/3) * ms` remain unresolved because they share the included start.
Both are definitely before the event beginning at `500 ms`; the window ends
there and excludes that endpoint. Output gives two definite orders and one
unresolved pair, exact seconds as rational strings, the raw input hash and both
engine hashes. This is a constructed example, not an observed incident.

Supply JSON on stdin to `dimensioned_order.py review`:

```json
{"origin":"shared asserted trigger","events":[{"id":"a","start":"0 ms","end":"500 ms"},{"id":"b","start":"0.5 s","end":"1 s"}]}
```

The origin is required: all times must be relative to the same asserted origin.
It is a label, not a clock conversion or calibration. Nonzero intervals are
half-open `[start,end)`; a zero-width interval is an included exact point.
Unresolved means strict order is unproved, not that events happened together.
Negative relative times are allowed. Zero must have time dimensions (`0 s`).
Use explicit multiplication: `(1/3) * s` is time; `1/3 s` is inverse time.
The inherited grammar supports exact arithmetic, s/ms/min/h/day and dimension
checking; expressions are never evaluated as Python. Output is ASCII JSON.

Fractions are compared exactly, then mapped monotonically to integer ranks for
the unchanged Lens comparison engine. This preserves all order and equality
relations without rounding recurring decimals. Ranks are never treated as
durations. Original expressions remain bound by the input SHA-256; converted
seconds remain explicit. Hashes identify bytes, not authors or measurement truth.

Input is at most 256 KiB and 128 events (8,128 pairs). IDs are unique and at
most 256 characters, as is the origin label. Unknown or duplicate JSON fields,
nonstrings, reversed intervals and wrong dimensions fail. Inherited expression
budgets apply: 4096 characters, 256 tokens, 32 nesting levels and 2048-bit
rational arithmetic. Exit 0 means valid analysis, including unresolved pairs;
exit 2 means invalid input, with no partial stdout. CLI reads stdin and its two
local engine snapshots only. No network, environment access, signing or sending.

```sh
python3 -B -m unittest discover -s shared/dimensioned-order -v
```

Six tests passed: 441 rational interval pairs in both input orders against an
independent endpoint-set oracle, recurring fractions and boundary cases, nearby
decimal overlap, invalid dimensions/shapes/limits, source/hash checks and a
copied-folder offline CLI with invalid-input/no-partial-output checks.
`provenance.json` pins two byte-identical ordinary-file snapshots. The gathering
also rechecked the original included-start regression in both input orders.

Limits: supplied intervals, shared origins and uncertainty bounds are assertions.
This tool does not parse calendar timestamps, collect logs, infer clock error,
prove causality or certify input truth. Use Line 3's replay tools for cited log
packs. No coin, price or payment is needed.
