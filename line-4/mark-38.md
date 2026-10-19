# The Gathering Flow — mark 38

Integral Flint checks the exact signed accumulation from a dimensioned
piecewise-linear table. A small worn ochre bowl receives falling charcoal
drops on bare lower-right stone: separate readings gathered into a total.

Used the imagegen skill and built-in image_gen tool in edit mode, with
wall-v20.png as the target. The generation changed some inherited details,
so the whole generated edit was not used. Only new bowl/drop pigment was
extracted, moved to bare lower-right rock and multiply-blended with the
ancestor. The generator depicted two distinct drops rather than the three
requested in the prompt; the delivered motif intentionally retains those
two drops. No digit-count requirement applies to drops.

Full prompt, apart from a save-path hint:

> Edit target: the inherited square cave painting wall-v20.png. Keep exact size, framing, warm rock, cracks, lighting, Pepe with heavy lidded eyes and wide mouth, and ALL existing ancestor marks unchanged. Add ONLY one small new motif in empty bare stone near bottom right: a shallow ochre clay collecting bowl with three tiny charcoal falling drops above it, representing accumulated flow. Rough worn earth pigment, handmade prehistoric Lascaux painting; stone visible through pigment. No hands added. No letters, numbers, symbols resembling text, captions, signatures, logos, watermark, borders. Preserve every other part.

The one-time `preserve-mark-38.js` operation and `mark-38-process.json`
record the source, destination, hashes and mask. The generated intermediate
was replaced in place by the finished wall. Exactly 3,584 pixels changed;
every other decoded pixel matches the latest ancestor. The current alias
`wall.png` points to the new `wall-v21.png`; the old wall remains intact.
No extra generated picture is retained in the workspace.

Final wall: 1254 × 1254 RGB8 PNG. Preview: 512 × 512 baseline JPEG,
created with the existing reviewed standard-library gathering/make_preview.py.
The sole preview is the explicitly required dist/line-4/38.jpg.

Chosen review: local visual inspection of the whole PNG and JPEG, plus
pixel comparison against the latest wall. Pepe retains heavy-lidded eyes,
wide mouth, and two hands with four fingers and one thumb each. No hands or
stencils were added. The cave size, rock, cracks, colours, light, framing and
ancestor marks remain. No writing, numbers, watermark, border, photos, 3D
figures, real people or prohibited symbols were observed. Unmet visual
requirements observed: none. The small mark loses detail in the preview;
this is local inspection, not independent artistic approval.
