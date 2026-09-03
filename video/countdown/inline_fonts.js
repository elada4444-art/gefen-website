const fs=require('fs');
process.chdir(__dirname);
let css=fs.readFileSync('heebo.css','utf8');
const urls=[...new Set(css.match(/https:\/\/fonts\.gstatic\.com[^)]+/g))];
console.log('unique font files:',urls.length);
(async()=>{
  for(const u of urls){
    const r=await fetch(u);
    const b=Buffer.from(await r.arrayBuffer());
    console.log(u.split('/').pop(), b.length);
    css=css.split(u).join('data:font/woff2;base64,'+b.toString('base64'));
  }
  fs.writeFileSync('heebo-inline.css',css);
  console.log('css bytes',css.length);
})();
