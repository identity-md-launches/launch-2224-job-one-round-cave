// One-time transfer of generated mineral pigment onto the inherited RGB8 wall.
// The generated donor temporarily occupies wall-v21.png; never run twice.
const fs = require('fs');
const zlib = require('zlib');
const crypto = require('crypto');

function decode(data) {
  if (data.subarray(0, 8).toString('hex') !== '89504e470d0a1a0a') throw Error('PNG signature');
  let pos = 8, idat = [], width, height;
  while (pos < data.length) {
    const n = data.readUInt32BE(pos), kind = data.toString('ascii', pos + 4, pos + 8);
    const payload = data.subarray(pos + 8, pos + 8 + n);
    if (kind === 'IHDR') {
      width = payload.readUInt32BE(0); height = payload.readUInt32BE(4);
      if (payload[8] !== 8 || payload[9] !== 2 || payload[12] !== 0) throw Error('RGB8 noninterlaced required');
    }
    if (kind === 'IDAT') idat.push(payload);
    pos += n + 12;
    if (kind === 'IEND') break;
  }
  if (width !== 1254 || height !== 1254) throw Error('wall dimensions');
  const raw = zlib.inflateSync(Buffer.concat(idat));
  const stride = width * 3, pixels = Buffer.alloc(width * height * 3);
  if (raw.length !== (stride + 1) * height) throw Error('scanline size');
  for (let y = 0; y < height; y++) {
    const mode = raw[y * (stride + 1)];
    for (let x = 0; x < stride; x++) {
      const k = y * stride + x;
      const a = x >= 3 ? pixels[k - 3] : 0;
      const b = y ? pixels[k - stride] : 0;
      const c = y && x >= 3 ? pixels[k - stride - 3] : 0;
      let p = 0;
      if (mode === 1) p = a;
      else if (mode === 2) p = b;
      else if (mode === 3) p = Math.floor((a + b) / 2);
      else if (mode === 4) {
        const v = a + b - c, da = Math.abs(v - a), db = Math.abs(v - b), dc = Math.abs(v - c);
        p = da <= db && da <= dc ? a : db <= dc ? b : c;
      } else if (mode !== 0) throw Error('PNG filter');
      pixels[k] = (raw[y * (stride + 1) + 1 + x] + p) & 255;
    }
  }
  return {width, height, pixels};
}

function crc(data) {
  let c = 0xffffffff;
  for (const b of data) {
    c ^= b;
    for (let j = 0; j < 8; j++) c = (c >>> 1) ^ ((c & 1) ? 0xedb88320 : 0);
  }
  return (c ^ 0xffffffff) >>> 0;
}
function chunk(name, data) {
  const kind = Buffer.from(name), out = Buffer.alloc(data.length + 12);
  out.writeUInt32BE(data.length, 0); kind.copy(out, 4); data.copy(out, 8);
  out.writeUInt32BE(crc(Buffer.concat([kind, data])), data.length + 8);
  return out;
}
function encode(img) {
  const header = Buffer.alloc(13); header.writeUInt32BE(img.width, 0); header.writeUInt32BE(img.height, 4);
  header[8] = 8; header[9] = 2;
  const stride = img.width * 3, raw = Buffer.alloc((stride + 1) * img.height);
  for (let y = 0; y < img.height; y++) img.pixels.copy(raw, y * (stride + 1) + 1, y * stride, (y + 1) * stride);
  return Buffer.concat([Buffer.from('89504e470d0a1a0a', 'hex'), chunk('IHDR', header),
    chunk('IDAT', zlib.deflateSync(raw)), chunk('IEND', Buffer.alloc(0))]);
}

const ancestorPath = 'artifacts/line-4/wall-v20.png';
const targetPath = 'artifacts/line-4/wall-v21.png';
const ancestorBytes = fs.readFileSync(ancestorPath), donorBytes = fs.readFileSync(targetPath);
const ancestor = decode(ancestorBytes), donor = decode(donorBytes);
const hash = data => crypto.createHash('sha256').update(data).digest('hex');
const source = [975,950,1125,1080], destination = [790,1080,940,1210];
let changed=0, bbox=[1254,1254,0,0];
const mask = Buffer.alloc(1254*1254);
for(let y=950;y<1080;y++) for(let x=975;x<1125;x++) {
  const k=(y*1254+x)*3;
  const [r,g,b]=[donor.pixels[k],donor.pixels[k+1],donor.pixels[k+2]];
  // Restrict extraction to new bowl's red pigment and the two falling drops.
  const bowl = y>=1020 && y<=1073 && r>45 && r>2.7*g && r>3*b;
  const drops = x>=1038 && x<=1070 && y>=955 && y<=1018 && Math.max(r,g,b)<66;
  if(!bowl && !drops) continue;
  const dx=x-975+790, dy=y-950+1080, j=(dy*1254+dx)*3;
  // Pigment darkens existing stone rather than pasting generated background.
  let differs=false;
  for(let c=0;c<3;c++) {
    const value=Math.round(ancestor.pixels[j+c]*(0.32+0.68*donor.pixels[k+c]/255));
    if(value!==ancestor.pixels[j+c]) differs=true;
    ancestor.pixels[j+c]=value;
  }
  if(differs) {
    changed++; mask[dy*1254+dx]=1;
    bbox=[Math.min(bbox[0],dx),Math.min(bbox[1],dy),Math.max(bbox[2],dx),Math.max(bbox[3],dy)];
  }
}
if(changed<500 || changed>6000) throw Error('unexpected pigment count '+changed);
const original=decode(ancestorBytes);
let outside=0;
for(let i=0;i<mask.length;i++) if(!mask[i]) for(let c=0;c<3;c++) {
  if(original.pixels[3*i+c]!==ancestor.pixels[3*i+c]) {outside++; break;}
}
if(outside) throw Error('ancestor changed outside pigment mask');
const bytes=encode(ancestor);
fs.writeFileSync(targetPath,bytes);
// Update the alias itself; never write through the inherited symlink.
const alias='artifacts/line-4/wall.png';
fs.rmSync(alias,{force:true});
fs.symlinkSync('wall-v21.png',alias);
const report={method:'New generated bowl and falling drops, pigment-only transfer to bare lower-right rock with multiply blending.',
ancestor:ancestorPath,ancestor_sha256:hash(ancestorBytes),donor_sha256:hash(donorBytes),source,destination,
changed_pixels:changed,changed_bbox_xyxy_inclusive:bbox,outside_mask_changed_pixels:outside,
mask_sha256:hash(mask),final_sha256:hash(bytes),
preservation:'All decoded pixels outside the new pigment mask match the latest ancestor exactly.'};
fs.writeFileSync('line-4/mark-38-process.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
