const fs=require('fs');
const path=require('path');
process.chdir(__dirname);
const tpl=fs.readFileSync('scene.template.html','utf8');
const css=fs.readFileSync('heebo-inline.css','utf8');
const logo='data:image/png;base64,'+fs.readFileSync(path.join(__dirname,'..','..','assets','logo.png')).toString('base64');
fs.writeFileSync('scene.html',tpl.replace('__FONT_CSS__',css).replace('__LOGO__',logo));
console.log('scene.html',fs.statSync('scene.html').size,'bytes');
