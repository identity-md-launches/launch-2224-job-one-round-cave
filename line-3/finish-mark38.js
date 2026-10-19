'use strict';
// Local finishing: preserve ancestor pixels outside the new bare-rock motif.
const fs = require('node:fs');
const crypto = require('node:crypto');
const {decodePNG, encodePNG, preview} = require('../line-1/wall-render/finish_wall.js');
const hash = b => crypto.createHash('sha256').update(b).digest('hex');
const ancestorPath = 'artifacts/line-3/wall-v20.png';
const outputPath = 'artifacts/line-3/wall-v21.png';
const ancestor = decodePNG(ancestorPath), donorBytes = fs.readFileSync(outputPath);
const donor = decodePNG(outputPath);
if (ancestor.width !== donor.width || ancestor.height !== donor.height || ancestor.channels !== donor.channels) throw Error('matching dimensions required');
const result = {...ancestor, pixels: Buffer.from(ancestor.pixels)};
const bounds = [423, 940, 527, 991];
const [left, top, right, bottom] = bounds;
for(let y=top;y<bottom;y++) for(let x=left;x<right;x++) {
  const alpha=Math.max(0,Math.min(1,(x-left)/5,(right-1-x)/5,(y-top)/5,(bottom-1-y)/5));
  for(let c=0;c<result.channels;c++) {
    const at=(y*result.width+x)*result.channels+c;
    result.pixels[at]=Math.round(ancestor.pixels[at]*(1-alpha)+donor.pixels[at]*alpha);
  }
}
let changed=0,outside=0;
for(let y=0;y<result.height;y++) for(let x=0;x<result.width;x++) {
 const at=(y*result.width+x)*result.channels;
 if(!result.pixels.subarray(at,at+result.channels).equals(ancestor.pixels.subarray(at,at+result.channels))) {
  changed++;
  if(x<left||x>=right||y<top||y>=bottom) outside++;
 }
}
if(!changed||outside) throw Error('invalid preservation');
const png=encodePNG(result),jpg=preview(result);
if(jpg.length>100000)throw Error('preview too large');
fs.writeFileSync(outputPath,png);
// Replace an alias without following it; never modify an older wall.
if(fs.existsSync('artifacts/line-3/wall.png') || (()=>{try{return fs.lstatSync('artifacts/line-3/wall.png').isSymbolicLink()}catch{return false}})()) fs.unlinkSync('artifacts/line-3/wall.png');
fs.writeFileSync('artifacts/line-3/wall.png',png);
fs.writeFileSync('dist/line-3/38.jpg',jpg);
const stats={ancestor:ancestorPath,ancestor_sha256:hash(fs.readFileSync(ancestorPath)),donor_sha256:hash(donorBytes),patch_bounds_exclusive:bounds,changed_pixels:changed,changed_outside_patch:outside,wall:{path:outputPath,format:'PNG',width:result.width,height:result.height,color:'RGB8',bytes:png.length,sha256:hash(png)},preview:{path:'dist/line-3/38.jpg',format:'JPEG',width:512,height:512,bytes:jpg.length}};
fs.writeFileSync('line-3/round-38-image-check.json',JSON.stringify(stats,null,2)+'\n');
console.log(JSON.stringify(stats));
