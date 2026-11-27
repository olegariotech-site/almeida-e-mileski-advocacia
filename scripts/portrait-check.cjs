const pw=require('playwright'),fs=require('node:fs/promises'),path=require('node:path');
const {spawn}=require('node:child_process');
(async()=>{
 const out=process.argv[2];await fs.mkdir(out,{recursive:true});
 const server=spawn('python3',[path.join(__dirname,'serve.py'),'--port','8776'],{stdio:['ignore','pipe','pipe']});process.on('exit',()=>server.kill());
 await new Promise((r,j)=>{server.stdout.once('data',r);server.once('error',j)});const checks=[];
 try{for(const engine of ['chromium','firefox','webkit']){
  const m=require('@sparticuz/chromium'),c=m.default||m;
  const browser=await pw[engine].launch(engine==='chromium'?{executablePath:await c.executablePath(),args:c.args,headless:true}:{headless:true});
  try{for(const width of [390,412,1366]){
   const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1.75,reducedMotion:'reduce'});
   await page.goto('http://127.0.0.1:8776/as-advogadas/',{waitUntil:'networkidle'});
   const images=await page.locator('.portrait img').evaluateAll(els=>els.map(i=>({src:i.currentSrc,loaded:i.complete&&i.naturalWidth>0,width:i.naturalWidth})));
   checks.push({engine,version:browser.version(),viewport:width,dpr:1.75,images,pass:images.length===2&&images.every(i=>i.loaded)&&(width>412||images.every(i=>i.src.endsWith('-672.webp')))});
   if(width===390){
    await page.goto('http://127.0.0.1:8776/areas/direito-imobiliario-e-condominial/',{waitUntil:'networkidle'});
    await page.locator('.context-nav a[href="#tema-2"]').click();
    await page.waitForFunction(()=>document.querySelector('.context-nav a[href="#tema-2"]').getAttribute('aria-current')==='location');
    const top=await page.locator('#tema-2').evaluate(el=>el.getBoundingClientRect().top);
    checks.push({engine,name:'Active contextual topic after anchor navigation',top,pass:top>=90&&top<=180});
   }
   await page.close();
  }}finally{await browser.close()}
 }}finally{server.kill()}
 const report={checks,pass:checks.every(c=>c.pass)};await fs.writeFile(path.join(out,'portraits.json'),JSON.stringify(report,null,2));
 console.log(checks.length,'responsive portrait checks',report.pass?'PASS':'FAIL');if(!report.pass)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
