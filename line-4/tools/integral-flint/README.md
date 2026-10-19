# Integral Flint

Check the accumulated quantity under a supplied piecewise-linear table using
exact rational arithmetic and explicit unit dimensions. Examples include
volume from flow versus time, distance from velocity versus time, and work
from force versus distance. Python 3.10+ and the standard library suffice.
Copy this whole folder for standalone offline use.

One command from the repository root shows it working:

```sh
python3 -B line-4/tools/integral-flint/integral_flint.py demo
```

Tried locally: the demo exits **0** and checks exactly **29/3 L** accumulated
between 1 and 4 seconds, using hypothetical flow observations at 0, 2 and
5 seconds. The clipped segment contributions are exactly 3 L and 20/3 L.
All **12 tests** passed, including 300 seeded nonuniform tables compared with
an independent affine-antiderivative `Fraction` oracle, mixed units, signed
cancellation, partition invariance, dimension checks, resource limits and
CLI statuses. A standalone folder copy also passed the demo and tests.
These checks establish the supplied model's arithmetic, not measurement truth.

## Supply a table

Send one JSON request on stdin:

```sh
printf '%s\n' '{"schema":"integral-flint/1","points":[{"x":"0 s","y":"1 m/s"},{"x":"4 s","y":"5 m/s"}],"start":"1 s","end":"3 s","to":"m","expect":"6 m"}' | python3 -B line-4/tools/integral-flint/integral_flint.py run
```

This exits 0 and reports exactly `6 m`. Required fields: `schema`, `points`,
`start`, `end`, `to`. Optional: `expect`. No other fields are accepted.
Each point has exactly `x` and `y`, both quantity expressions. All x dimensions
must agree, all y dimensions must agree, and x must be strictly increasing
after conversion. Input is never silently sorted or deduplicated. The whole
table is validated, including points outside the integration window.

`start` and `end` have x dimensions, must satisfy start < end, and must both
lie within the table. Endpoint knots are allowed; zero-width and reversed
windows are rejected. There is no extrapolation. Negative x and y are allowed.
`to` is a positive-scale target unit with dimensions x times y; `expect`, if
present, is a quantity with those same dimensions. Even zero retains dimensions.

For every segment intersecting the window, the tool linearly interpolates
the clipped endpoint values and integrates exactly:

`contribution = (right - left) * (y(left) + y(right)) / 2`

The result is a **signed integral**: negative values cancel positive values,
including where a segment crosses zero. It is not the area under the absolute
value. Output gives the original window, each contributing segment's zero-based
indices, clipped coordinates, endpoint readings and signed contribution in
base units. `x_base_unit`, `y_base_unit` and `base_unit` identify the units of
those fields. `value` and `unit` give the total in the requested target unit.
Numbers are exact decimal strings when terminating, otherwise fraction strings.
An optional `check` reports equality and exact `result - expect` in base units.

Exit **0**: valid calculation, with a passing claim or no claim.
Exit **1**: valid calculation disagrees with `expect`.
Exit **2**: invalid input or a resource limit; no partial stdout is emitted.
The CLI reads only stdin and writes only stdout/stderr. It has no file,
network, environment, wallet, signing or transaction interface.

## Grammar and limits

Expressions use the unchanged Unit Flint engine: `+ - * / ^ **`, parentheses,
exact decimal/scientific numbers, integer powers -12..12. Units: m, cm, mm,
km, in, ft, mi; kg, g, mg, t; s, ms, min, h, day; B, KiB, MiB, GiB;
L, mL; N, J, W. Dimensionless quantities use `1`. Use explicit multiplication:
`(1/3) * s` is time, whereas `1/3 s` is inverse time. `2 m^2` means `(2 m)^2`;
use `2 * m^2` for two square metres. Target units forbid addition/subtraction.

Requests are capped at 65,536 UTF-8 bytes, four JSON nesting levels and
2..128 points. Duplicate keys, JSON numeric values, nonfinite constants,
unknown fields and malformed UTF-8 are rejected. Quantities must be strings.
Expressions allow 4096 characters, 256 tokens and 32 nesting levels. Decimal
literals allow 80 characters, exponent magnitude 200 and adjusted magnitude
100. Parsed arithmetic and integration intermediates are capped at 2048
numerator/denominator bits and dimension exponents -256..256. A valid result
can be refused if an intermediate exceeds a budget, even if later cancellation
would reduce it. These are bounded arithmetic checks, not a universal integrator.

## Limits and provenance

Piecewise linearity is an explicit modeling assumption. The trapezoid formula
is exact for that model, but it supplies no error bound for the underlying
physical process, no uncertainty propagation, no sample completeness claim
and no sensor calibration. It does not fit curves, smooth readings, infer
units, treat affine temperatures, or fetch measurements or token prices.
No coin is needed for dimensional arithmetic.

`engine.py` is an ordinary-file, byte-identical copy of
`line-4/tools/unit-flint/unit_flint.py`. JSON input bounds and CLI conventions
follow Interpolation Flint. No packages or submodules are required.

```sh
python3 -B -m unittest discover -s line-4/tools/integral-flint -v
```
