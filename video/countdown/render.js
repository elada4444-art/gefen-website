const {chromium}=require('playwright-core');
const fs=require('fs');
process.chdir(__dirname);
const FPS=Number(process.env.FPS||30);
const OUT=process.env.OUT||'frames';
(async()=>{
  fs.rmSync(OUT,{recursive:true,force:true}); fs.mkdirSync(OUT,{recursive:true});
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',
    args:['--no-sandbox','--font-render-hinting=none','--force-color-profile=srgb','--disable-lcd-text']});
  const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  await p.goto('file://'+process.cwd()+'/scene.html');
  await p.evaluate(()=>document.fonts.ready);
  await p.waitForTimeout(400);
  await p.evaluate(()=>window.calibrate());
  const dur=await p.evaluate(()=>window.SCENE_DURATION);
  const n=Math.round(dur*FPS);
  console.log(`duration ${dur}s @ ${FPS}fps -> ${n} frames`);
  for(let i=0;i<n;i++){
    await p.evaluate(t=>window.render(t), i/FPS);
    await p.screenshot({path:`${OUT}/${String(i+1).padStart(4,'0')}.png`});
    if((i+1)%40===0) console.log('  frame',i+1,'/',n);
  }
  await b.close();
  console.log('done',n,'frames');
})();
