const pw=require('playwright'),fs=require('node:fs/promises'),path=require('node:path');
const {spawn}=require('node:child_process');
(async()=>{
 const out=process.argv[2];await fs.mkdir(out,{recursive:true});
 const server=spawn('python3',[path.join(__dirname,'serve.py'),'--port','8774'],{stdio:['ignore','pipe','pipe']});process.on('exit',()=>server.kill());
 await new Promise((r,j)=>{server.stdout.once('data',r);server.once('error',j)});
 const checks=[];
 try{for(const engine of ['chromium','firefox','webkit']){
  const m=require('@sparticuz/chromium'),c=m.default||m;
  const browser=await pw[engine].launch(engine==='chromium'?{executablePath:await c.executablePath(),args:c.args,headless:true}:{headless:true});
  const page=await browser.newPage({reducedMotion:'reduce'});
  try{for(const width of [320,360,375,390,414,768,1024,1366,1920])for(const route of ['','o-escritorio/']){
   await page.setViewportSize({width,height:width<600?844:900});await page.goto('http://127.0.0.1:8774/'+route,{waitUntil:'networkidle'});
   const metrics=await page.evaluate(()=>{const box=document.querySelector('.hero-photo'),img=box.querySelector('img');return {contentWidth:document.documentElement.scrollWidth,viewport:innerWidth,photoWidth:box.getBoundingClientRect().width,photoHeight:box.getBoundingClientRect().height,loaded:img.complete&&img.naturalWidth>0,objectPosition:getComputedStyle(img).objectPosition}});
   const pass=metrics.contentWidth<=metrics.viewport+1&&metrics.loaded&&metrics.photoWidth/metrics.photoHeight>=1.82;
   checks.push({engine,version:browser.version(),width,route,metrics,pass});
  }}finally{await browser.close()}
 }}finally{server.kill()}
 const report={checks,pass:checks.every(x=>x.pass)};await fs.writeFile(path.join(out,'final-layout.json'),JSON.stringify(report,null,2));
 console.log(checks.length,'final photo-framing and layout checks',report.pass?'PASS':'FAIL');if(!report.pass)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
