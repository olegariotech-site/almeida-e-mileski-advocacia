const fs=require('node:fs/promises');
const path=require('node:path');
const {spawn}=require('node:child_process');
const {chromium}=require('playwright');
(async()=>{
 const out=process.argv[2];if(!out)throw Error('Pass output directory');await fs.mkdir(out,{recursive:true});
 const mod=require('@sparticuz/chromium'),c=mod.default||mod;
 const server=spawn('python3',[path.join(__dirname,'serve.py')],{stdio:['ignore','pipe','pipe']});process.on('exit',()=>server.kill());
 await new Promise((resolve,reject)=>{server.stdout.once('data',resolve);server.once('error',reject)});
 const browser=await chromium.launch({executablePath:await c.executablePath(),args:c.args,headless:true});
 const areas=JSON.parse(await fs.readFile(path.join(__dirname,'../content/areas.json'),'utf8'));
 const routes=['','o-escritorio/','as-advogadas/',...areas.map(a=>'areas/'+a.slug+'/'),'conteudos/','contato/','politica-de-privacidade/','404.html'];
 try{
  const page=await browser.newPage({reducedMotion:'reduce'});
  const capture=async(name)=>{
   for(const img of await page.locator('img').all()){await img.scrollIntoViewIfNeeded();await img.evaluate(async el=>await el.decode());}
   await page.evaluate(()=>{document.activeElement?.blur();scrollTo(0,0)});
   await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
   await page.screenshot({path:path.join(out,name+'.png'),fullPage:true,animations:'disabled'});
  };
  for(const width of [390,1366]){
   await page.setViewportSize({width,height:width===390?844:900});
   for(const route of routes){
    await page.goto('http://127.0.0.1:8765/'+route,{waitUntil:'networkidle'});await page.evaluate(()=>document.fonts.ready);
    const name=(route||'home').replaceAll('/','-').replace(/-$/,'')+'-'+width;
    await capture(name+'-closed');
    if(await page.locator('[data-expand="true"]').count()){
     await page.locator('[data-expand="true"]').click();await capture(name+'-open');
    }
   }
  }
  console.log('36 screenshots captured with images loaded and scroll reset');
 }finally{await browser.close();server.kill();}
})().catch(e=>{console.error(e);process.exit(1)});
