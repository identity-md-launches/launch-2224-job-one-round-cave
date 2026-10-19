'use strict';
// One-shot transfer of generated mineral pigment onto unpainted inherited rock.
const fs = require('node:fs');
const crypto = require('node:crypto');
const {decodePNG, encodePNG, preview} = require('./finish_wall.js');
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const source = 'artifacts/line-1/wall-v20.png';
const destination = 'artifacts/line-1/wall-v21.png';
if (fs.existsSync('dist/line-1/39.json')) throw Error('record 39 already exists');
const ancestorRaw = fs.readFileSync(source);
const donorRaw = fs.readFileSync(destination);
if (!ancestorRaw.equals(fs.readFileSync('artifacts/line-1/wall.png'))) throw Error('current wall is not record 38');
if (JSON.parse(fs.readFileSync('dist/line-1/38.json')).image !==
    'https://api.imd.fun/artifacts/' + hash(ancestorRaw)) throw Error('ancestor record pin mismatch');
const ancestor = decodePNG(source), donor = decodePNG(destination);
if (ancestor.width !== 1254 || ancestor.height !== 1254 || ancestor.channels !== 3 ||
    donor.channels !== 3) throw Error('unexpected image format');
const out = {...ancestor, pixels: Buffer.from(ancestor.pixels)};
// The small patch is bare rock above and to the right of the upper Pepe.
const bounds = [846, 274, 1006, 369];
const crop = [350, 230, 1180, 720];
let transferred = 0;
for (let y = bounds[1]; y < bounds[3]; y++) for (let x = bounds[0]; x < bounds[2]; x++) {
  const sx0 = crop[0] + (x-bounds[0]) * (crop[2]-crop[0]) / (bounds[2]-bounds[0]);
  const sx1 = crop[0] + (x+1-bounds[0]) * (crop[2]-crop[0]) / (bounds[2]-bounds[0]);
  const sy0 = crop[1] + (y-bounds[1]) * (crop[3]-crop[1]) / (bounds[3]-bounds[1]);
  const sy1 = crop[1] + (y+1-bounds[1]) * (crop[3]-crop[1]) / (bounds[3]-bounds[1]);
  let weight = 0, cover = 0;
  const sum = [0, 0, 0];
  for (let yy = Math.floor(sy0); yy < Math.ceil(sy1); yy++) for (let xx = Math.floor(sx0); xx < Math.ceil(sx1); xx++) {
    const w = (Math.min(sx1,xx+1)-Math.max(sx0,xx)) *
              (Math.min(sy1,yy+1)-Math.max(sy0,yy));
    const i = (yy*donor.width+xx)*3;
    const r = donor.pixels[i], g = donor.pixels[i+1], b = donor.pixels[i+2];
    weight += w;
    // Donor's surrounding pure black is transparent for this transfer.
    if (Math.max(r,g,b) > 38 && (r > 1.14*g || Math.min(r,g,b) > 35)) {
      cover += w;
      for (let c=0; c<3; c++) sum[c] += donor.pixels[i+c]*w;
    }
  }
  if (!cover) continue;
  const alpha = 0.73 * cover / weight;
  const at = (y*out.width+x)*3;
  for (let c=0; c<3; c++)
    out.pixels[at+c] = Math.round(out.pixels[at+c]*(1-alpha) + sum[c]/cover*alpha);
  transferred++;
}
let changed = 0;
for (let y=0; y<out.height; y++) for (let x=0; x<out.width; x++) {
  const i=(y*out.width+x)*3;
  if (!out.pixels.subarray(i,i+3).equals(ancestor.pixels.subarray(i,i+3))) {
    changed++;
    if (x<bounds[0] || x>=bounds[2] || y<bounds[1] || y>=bounds[3])
      throw Error('ancestral pixel changed outside patch');
  }
}
if (changed < 300 || transferred < 300) throw Error('insufficient pigment transferred');
const png=encodePNG(out), jpg=preview(out), digest=hash(png);
if (jpg.length>100000) throw Error('preview exceeds 100 KB');
fs.writeFileSync(destination,png);
fs.writeFileSync('artifacts/line-1/wall.png',png);
fs.writeFileSync('dist/line-1/39.jpg',jpg);
fs.writeFileSync('dist/line-1/39.json',JSON.stringify({
  name:'The Joined Pins', image:'https://api.imd.fun/artifacts/'+digest,
  attributes:[
    {trait_type:'Cave',value:'Roots'}, {trait_type:'Wall',value:'Line 1'},
    {trait_type:'Number',value:39}, {trait_type:'Left behind',value:'Sealed Bounds'},
    {trait_type:'Meaning',value:'A cord joins two mineral pins while each stone keeps its own colour and place.'},
    {trait_type:'One thing',value:'Reproducible benchmark evidence'}
  ]},null,2)+'\n');
const review={wall:destination,width:out.width,height:out.height,format:'PNG RGB8',
  bytes:png.length,sha256:digest,
  preview:{path:'dist/line-1/39.jpg',width:512,height:512,format:'JPEG',bytes:jpg.length},
  ancestor:source,ancestor_sha256:hash(ancestorRaw),generated_donor_sha256:hash(donorRaw),
  bounds,donor_crop:crop,changed_pixels:changed,all_pixels_outside_bounds_identical:true,
  visual_review:{status:'pending local inspection',unmet_visual_requirements:[]}};
fs.writeFileSync('line-1/wall-review-39.json',JSON.stringify(review,null,2)+'\n');
console.log(JSON.stringify(review));
