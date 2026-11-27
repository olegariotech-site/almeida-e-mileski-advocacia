const assert=require('node:assert/strict');
const fs=require('node:fs/promises');
const path=require('node:path');
const {spawn}=require('node:child_process');
const {chromium}=require('playwright');
(async()=>{
 const out=process.argv[2];if(!out)throw Error('Pass output directory');await fs.mkdir(out,{recursive:true});
 const server=spawn('python3',[path.join(__dirname,'serve.py'),'--port','8772'],{stdio:['ignore','pipe','pipe']});process.on('exit',()=>server.kill());
 await new Promise((r,j)=>{server.stdout.once('data',r);server.once('error',j)});
 const m=require('@sparticuz/chromium'),c=m.default||m,browser=await chromium.launch({executablePath:await c.executablePath(),args:c.args});
 const checks=[];const base='http://127.0.0.1:8772/';const page=await browser.newPage({reducedMotion:'reduce'});
 const check=async(name,fn)=>{try{const detail=await fn();checks.push({name,pass:true,detail})}catch(e){checks.push({name,pass:false,error:e.message})}};
 try{
  for(const width of [320,360,375,390,414])await check(`Home ${width}: photograph before description and no CTA overlap`,async()=>{
   await page.setViewportSize({width,height:844});await page.goto(base,{waitUntil:'networkidle'});
   const metrics=await page.evaluate(()=>{const photo=document.querySelector('.hero figure').getBoundingClientRect(),lead=document.querySelector('.hero .lead').getBoundingClientRect(),cta=document.querySelector('.hero .whatsapp').getBoundingClientRect();return {photoTop:photo.top,photoBottom:photo.bottom,leadTop:lead.top,ctaBottom:cta.bottom}});
   assert.ok(metrics.photoTop<500,JSON.stringify(metrics));assert.ok(metrics.photoBottom<=metrics.leadTop,JSON.stringify(metrics));
   await page.locator('.hero .whatsapp').scrollIntoViewIfNeeded();await page.waitForFunction(()=>getComputedStyle(document.querySelector('.wa-float')).visibility==='hidden');
   return metrics;
  });
  for(const height of [768,900])await check(`Notebook 1366x${height}: contact action visible`,async()=>{
   await page.setViewportSize({width:1366,height});await page.goto(base,{waitUntil:'networkidle'});
   const cta=await page.locator('.hero .whatsapp').boundingBox();assert.ok(cta.y+cta.height<=height,JSON.stringify(cta));return cta;
  });
  await check('Compact header preserves layout height',async()=>{
   const before=await page.locator('.site-header').boundingBox();await page.locator('#areas').scrollIntoViewIfNeeded();
   await page.waitForFunction(()=>document.querySelector('.site-header').classList.contains('is-scrolled'));
   const after=await page.locator('.site-header').boundingBox();assert.equal(before.height,after.height);return {before:before.height,after:after.height};
  });
  await check('Footer has five area links and floating control yields',async()=>{
   assert.equal(await page.locator('.footer nav[aria-label="Áreas jurídicas no rodapé"] a').count(),5);
   await page.locator('.footer').scrollIntoViewIfNeeded();await page.waitForFunction(()=>getComputedStyle(document.querySelector('.wa-float')).visibility==='hidden');
  });
  await check('Normal-motion native disclosure completes opening and closing',async()=>{
   await page.emulateMedia({reducedMotion:'no-preference'});await page.goto(base);const row=page.locator('details.signature').first();
   await row.locator('summary').click();await row.locator('.signature-body').waitFor({state:'visible'});assert.equal(await row.getAttribute('open'),'');
   await row.locator('summary').click();assert.equal(await row.getAttribute('open'),null);
  });
 }finally{await browser.close();server.kill();}
 await fs.writeFile(path.join(out,'refinement.json'),JSON.stringify({checks,pass:checks.every(c=>c.pass)},null,2));
 console.log(JSON.stringify(checks,null,2));if(checks.some(c=>!c.pass))process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
