// Export only the imagegen-painted object regions; retain original pixels elsewhere.
// Usage: NODE_PATH=<bundled modules> node export_retouches.cjs <repo> <library generation> <campus generation>
const sharp = require('sharp');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const [root, libraryPaint, campusPaint] = process.argv.slice(2);
if (!root || !libraryPaint || !campusPaint) throw new Error('Three input paths required');
const assets = path.join(root, 'assets/uqam_promo');
const output = path.join(root, 'dist/uqam_revision_20261004/photo_edits');
const jobs = [
  {original:'redaction_sciences_2026.jpg', painted:libraryPaint, final:'redaction_sciences_2026_no_red_bag.png',
    polygons:[[[1315,852],[1333,836],[1392,831],[1395,819],[1423,819],[1430,831],[1469,835],[1483,854],[1490,886],[1453,896],[1391,889],[1342,883],[1315,874]]]},
  {original:'president_kennedy.jpg', painted:campusPaint, final:'president_kennedy_no_vehicles.png',
    protect:[[[380,1290],[402,1290],[382,1593],[360,1593]]],
    polygons:[
      [[143,1420],[166,1371],[171,1300],[249,1287],[270,1321],[420,1338],[501,1340],[514,1496],[512,1578],[614,1595],[446,1610],[181,1590],[141,1535]],
      [[480,1502],[527,1471],[620,1473],[661,1488],[690,1518],[701,1554],[771,1594],[676,1610],[494,1608],[469,1568]],
      [[1665,1541],[1691,1507],[1770,1505],[1806,1519],[1831,1540],[1840,1593],[1840,1609],[1658,1608]],
      [[2031,1542],[2042,1525],[2082,1525],[2097,1540],[2100,1571],[2033,1574]],
      [[2145,1530],[2151,1524],[2167,1524],[2170,1538],[2158,1549],[2145,1548]],
      [[2234,1529],[2239,1521],[2264,1521],[2270,1530],[2268,1546],[2235,1547]],
      [[2335,1515],[2344,1515],[2349,1539],[2340,1541]],
      [[0,1455],[30,1452],[42,1465],[43,1485],[0,1487]],
      [[75,1458],[93,1457],[99,1475],[76,1476]]
    ]}
];
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
(async()=>{
  fs.mkdirSync(output,{recursive:true});
  const records=[];
  for(const job of jobs){
    const originalPath=path.join(assets,job.original);
    const {data:original,info}=await sharp(originalPath).removeAlpha().raw().toBuffer({resolveWithObject:true});
    const painted=await sharp(job.painted).resize(info.width,info.height,{fit:'fill'}).removeAlpha().raw().toBuffer();
    const polygons=job.polygons.map(p=>`<polygon points="${p.map(x=>x.join(',')).join(' ')}" fill="white"/>`).join('');
    const svg=Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${info.width}" height="${info.height}"><rect width="100%" height="100%" fill="black"/>${polygons}</svg>`);
    const mask=await sharp(svg).blur(job.protect ? 3 : 0.65).removeAlpha().greyscale().raw().toBuffer();
    if(job.protect){
      const shapes=job.protect.map(p=>`<polygon points="${p.map(x=>x.join(',')).join(' ')}" fill="white"/>`).join('');
      const protectedPixels=await sharp(Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${info.width}" height="${info.height}"><rect width="100%" height="100%" fill="black"/>${shapes}</svg>`)).removeAlpha().greyscale().raw().toBuffer();
      for(let i=0;i<mask.length;i++) if(protectedPixels[i]) mask[i]=0;
    }
    const final=Buffer.from(original);
    let editedPixels=0,changedOutsideMask=0;
    for(let i=0;i<mask.length;i++){
      const a=mask[i]/255;
      if(a){editedPixels++;for(let c=0;c<3;c++) final[i*3+c]=Math.round(original[i*3+c]*(1-a)+painted[i*3+c]*a);}
    }
    await sharp(final,{raw:{width:info.width,height:info.height,channels:3}}).png().toFile(path.join(assets,job.final));
    const check=await sharp(path.join(assets,job.final)).removeAlpha().raw().toBuffer();
    for(let i=0;i<mask.length;i++) if(!mask[i]) for(let c=0;c<3;c++) if(check[i*3+c]!==original[i*3+c]) changedOutsideMask++;
    if(changedOutsideMask) throw new Error('Pixels changed outside approved object regions');
    await sharp(mask,{raw:{width:info.width,height:info.height,channels:1}}).png().toFile(path.join(output,job.final.replace('.png','_mask.png')));
    fs.copyFileSync(job.painted,path.join(output,job.final.replace('.png','_imagegen_full.png')));
    records.push({original:job.original,original_sha256:hash(originalPath),generation_sha256:hash(job.painted),final:job.final,final_sha256:hash(path.join(assets,job.final)),dimensions:{width:info.width,height:info.height},polygons:job.polygons,protected_polygons:job.protect||[],edited_pixels:editedPixels,changed_channel_values_outside_mask:changedOutsideMask,method:'Built-in imagegen repaint, bounded-region composite. Original decoded RGB pixels retained exactly outside object masks.',generation_resized_for_patch_alignment:true});
  }
  fs.writeFileSync(path.join(output,'PHOTO_EDIT_QA.json'),JSON.stringify({date:'2026-10-04',records},null,2)+'\n');
  process.stdout.write(JSON.stringify(records.map(({final,final_sha256,dimensions,changed_channel_values_outside_mask})=>({final,final_sha256,dimensions,changed_channel_values_outside_mask})))+'\n');
})();
