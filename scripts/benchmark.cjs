/* Direct-browser research, no copying third-party assets into the implementation. */
const fs = require('node:fs/promises');
const path = require('node:path');
const { chromium } = require('playwright');
const refs = [
 ['dla-piper','https://www.dlapiper.com/'],
 ['withers','https://www.withersworldwide.com/'],
 ['irwin-mitchell','https://www.irwinmitchell.com/'],
 ['holland-knight','https://www.hklaw.com/'],
 ['squire-patton-boggs','https://www.squirepattonboggs.com/'],
 ['king-and-wood','https://www.kingandwood.com/'],
 ['stowe','https://www.stowefamilylaw.co.uk/'],
 ['akerman','https://www.akerman.com/'],
 ['morgan-morgan','https://www.forthepeople.com/'],
];
(async()=>{
 const out=process.argv[2];if(!out)throw Error('Pass output directory');await fs.mkdir(out,{recursive:true});
 let executable=process.env.CHROMIUM_EXECUTABLE;
 let args=[];
 if(process.env.SPARTICUZ_CHROMIUM){const mod=require('@sparticuz/chromium');const c=mod.default||mod;executable=await c.executablePath();args=c.args;}
 const proxyUrl=process.env.HTTPS_PROXY && new URL(process.env.HTTPS_PROXY);
 const proxy=proxyUrl?{server:proxyUrl.origin,...(proxyUrl.username?{username:decodeURIComponent(proxyUrl.username),password:decodeURIComponent(proxyUrl.password)}:{})}:undefined;
 const browser=await chromium.launch({headless:true,executablePath:executable,args,proxy});
 const results=[];
 for(const [name,url] of refs){
  const context=await browser.newContext({viewport:{width:1366,height:900},reducedMotion:'reduce'});
  const page=await context.newPage();
  const entry={name,url,observedAt:new Date().toISOString(),viewports:[]};
  try{
   const response=await page.goto(url,{timeout:20000,waitUntil:'domcontentloaded'});
   entry.status=response?.status();entry.finalUrl=page.url();entry.title=await page.title();
   for(const [label,width,height] of [['desktop',1366,900],['mobile',390,844]]){
    await page.setViewportSize({width,height});
    await page.screenshot({path:path.join(out,`${name}-${label}.png`),timeout:10000});
    const dom=await page.locator('body').innerText({timeout:8000});
    await fs.writeFile(path.join(out,`${name}-${label}.txt`),dom);
    const structure=await page.evaluate(()=>({
     headings:[...document.querySelectorAll('h1,h2,h3')].map(x=>({level:x.tagName,text:x.textContent.trim()})).slice(0,35),
     buttons:[...document.querySelectorAll('button,summary,[role=button]')].map(x=>({text:x.getAttribute('aria-label')||x.textContent.trim(),expanded:x.getAttribute('aria-expanded')})).filter(x=>x.text).slice(0,30),
     nav:[...document.querySelectorAll('header a,nav a')].map(x=>({text:x.textContent.trim()||x.getAttribute('aria-label'),href:x.getAttribute('href')})).slice(0,45),
     width:innerWidth,scrollWidth:document.documentElement.scrollWidth,
    }));
    entry.viewports.push({label,...structure});
   }
   await page.mouse.wheel(0,850);
   entry.scrolled=await page.evaluate(()=>({y:scrollY,header:[...document.querySelectorAll('header')].map(e=>({top:e.getBoundingClientRect().top,position:getComputedStyle(e).position})).slice(0,3)}));
   await page.screenshot({path:path.join(out,`${name}-mobile-scroll.png`),timeout:10000});
   await page.mouse.wheel(0,-10000);
   // Only operate an actually observed navigation control.
   const menus=page.getByRole('button',{name:/^(menu|open menu|open navigation|toggle navigation menu|navigation-menu)$/i});
   if(await menus.count()===1 && await menus.isVisible()){
    await menus.click({timeout:4000});
    entry.mobileMenu=await page.locator('body').innerText();
    await page.screenshot({path:path.join(out,`${name}-mobile-menu.png`),timeout:10000});
   }
  }catch(e){entry.error=e.message;}
  results.push(entry);await fs.writeFile(path.join(out,'observations.json'),JSON.stringify(results,null,2));
  console.log(name,entry.status||'',entry.error?.split('\n')[0]||'inspected');
  await context.close();
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
