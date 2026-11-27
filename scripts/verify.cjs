const fs=require('node:fs/promises');
const path=require('node:path');
const assert=require('node:assert/strict');
const {spawn}=require('node:child_process');
const pw=require(process.env.PLAYWRIGHT_PACKAGE||'playwright');
const axePath=require.resolve('axe-core/axe.min.js');
const routes=['','o-escritorio/','as-advogadas/',
 'areas/direito-imobiliario-e-condominial/','areas/direito-de-familia-e-sucessoes/',
 'areas/direito-bancario/','areas/direito-do-consumidor/','areas/direito-previdenciario-e-assistencial/',
 'conteudos/','contato/','politica-de-privacidade/','404.html'];
const base=process.env.PREVIEW_URL||'http://127.0.0.1:8765/';
(async()=>{
 const server=spawn('python3',[path.join(__dirname,'serve.py')],{stdio:['ignore','pipe','pipe']});
 process.on('exit',()=>server.kill());
 await new Promise((resolve,reject)=>{server.stdout.once('data',resolve);server.once('error',reject);server.once('exit',code=>reject(Error('Preview server exited: '+code)));});
 const out=process.argv[2];if(!out)throw Error('Pass output directory');await fs.mkdir(out,{recursive:true});
 const result={at:new Date().toISOString(),base,engines:[],failures:[]};
 const check=async(name,fn)=>{try{await fn();return {name,pass:true}}catch(e){const f={name,pass:false,error:e.message};result.failures.push(f);return f}};
 for(const engine of (process.env.TEST_ENGINES||'chromium,firefox,webkit').split(',')){
  let executable=process.env.CHROMIUM_EXECUTABLE,args=[];
  if(engine==='chromium'&&process.env.SPARTICUZ_CHROMIUM){const mod=require('@sparticuz/chromium'),c=mod.default||mod;executable=await c.executablePath();args=c.args;}
  let browser;
  try{browser=await pw[engine].launch({headless:true,...(engine==='chromium'?{executablePath:executable,args}:{})});}
  catch(e){result.engines.push({name:engine,blocked:e.message});console.log(engine,'BLOCKED');continue;}
  const summary={name:engine,version:browser.version(),checks:[],axe:[],screenshots:[]};
  const context=await browser.newContext({reducedMotion:'reduce'}),page=await context.newPage();
  const errors=[],external=new Set();
  page.on('pageerror',e=>errors.push(e.message));
  page.on('request',req=>{if(!req.url().startsWith(base)&&!req.url().startsWith('data:'))external.add(req.url());});
  for(const width of [320,390,768,1366,1920]){
   await page.setViewportSize({width,height:width<600?844:900});
   for(const route of routes){
    summary.checks.push(await check(`${width} ${route||'home'} route/assets/overflow`,async()=>{
     const bad=[];const listener=r=>{if(r.status()>=400)bad.push(r.url())};page.on('response',listener);
     const response=await page.goto(base+route,{waitUntil:'networkidle'});await page.evaluate(()=>document.fonts.ready);
     assert.ok([200,304].includes(response.status()),`Unexpected HTTP status: ${response.status()}`);
     assert.deepEqual(bad,[]);page.off('response',listener);
     assert.equal(await page.locator('h1').count(),1);
     assert.equal(await page.locator('meta[name="robots"]').getAttribute('content'),'noindex,nofollow');
     const layout=await page.evaluate(()=>({viewport:innerWidth,content:document.documentElement.scrollWidth,images:[...document.images].filter(i=>i.getBoundingClientRect().top<innerHeight&&!i.complete||i.complete&&i.naturalWidth===0).map(i=>i.src)}));
     assert.ok(layout.content<=layout.viewport+1,JSON.stringify(layout));
     assert.deepEqual(layout.images,[]);
    }));
    if(engine==='chromium' && [390,1366].includes(width)){
     const label=(route||'home').replaceAll('/','-').replace(/-$/,'');
     const name=`${label}-${width}-closed.png`;
     for(const lazy of await page.locator('img[loading="lazy"]').all()){
      await lazy.scrollIntoViewIfNeeded();await lazy.evaluate(async img=>{await img.decode()});
     }
     await page.evaluate(()=>scrollTo(0,0));
     await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
     await page.screenshot({path:path.join(out,name),fullPage:true,animations:'disabled'});summary.screenshots.push(name);
     await page.addScriptTag({path:axePath});
     const audit=await page.evaluate(async()=>await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}}));
     summary.axe.push({route,width,violations:audit.violations.map(v=>({id:v.id,impact:v.impact,description:v.description,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))})),incomplete:audit.incomplete.map(v=>v.id)});
     const expand=page.getByRole('button',{name:'Expandir todas',exact:true});
     if(await expand.count()){
      await expand.click();assert.equal(await page.locator('details.signature:not([open])').count(),0);
      const opened=`${label}-${width}-open.png`;await page.screenshot({path:path.join(out,opened),fullPage:true});summary.screenshots.push(opened);
      await page.getByRole('button',{name:'Recolher todas',exact:true}).click();assert.equal(await page.locator('details.signature[open]').count(),0);
     }
    }
   }
  }
  summary.checks.push(await check('keyboard and menu',async()=>{
   await page.setViewportSize({width:390,height:844});await page.goto(base);
   await page.keyboard.press('Tab');assert.equal(await page.locator(':focus').innerText(),'Ir para o conteúdo');
   const menu=page.locator('#menu-toggle');await menu.click();assert.equal(await page.locator('#mobile-menu').getAttribute('open'),'');
   await page.keyboard.press('Escape');assert.equal(await page.locator('#mobile-menu').getAttribute('open'),null);assert.equal(await page.locator(':focus').getAttribute('id'),'menu-toggle');
   const row=page.locator('details.signature>summary').first();await row.focus();await page.keyboard.press('Enter');assert.equal(await page.locator('details.signature').first().getAttribute('open'),'');
   await page.keyboard.press('Space');assert.equal(await page.locator('details.signature').first().getAttribute('open'),null);
  }));
  summary.checks.push(await check('hash navigation opens legal section',async()=>{
   await page.goto(base+routes[3]+'#tema-2');assert.equal(await page.locator('#tema-2').getAttribute('open'),'');
   await page.locator('.context-nav a[href="#tema-1"]').click();assert.equal(await page.locator('#tema-1').getAttribute('open'),'');
  }));
  summary.checks.push(await check('reduced motion',async()=>{
   assert.equal(await page.locator('h1').evaluate(el=>getComputedStyle(el).animationName),'none');
   assert.equal(await page.locator('html').evaluate(el=>getComputedStyle(el).scrollBehavior),'auto');
  }));
  summary.checks.push(await check('UTM same-site only, no storage/tracking',async()=>{
   await page.goto(base+'?utm_source=qa&utm_campaign=review&private=discard');
   const next=await page.locator('a[data-internal][href*="o-escritorio/"]').first().getAttribute('href');
   assert.equal(new URL(next).searchParams.get('utm_source'),'qa');assert.equal(new URL(next).searchParams.get('private'),null);
   for(const href of await page.locator('a[href^="https://wa.me/"]').evaluateAll(els=>els.map(e=>e.href))){assert.equal(new URL(href).searchParams.get('utm_source'),null);assert.equal(new URL(href).pathname,'/5519996837596');}
   assert.equal(await page.evaluate(()=>localStorage.length+sessionStorage.length),0);assert.deepEqual(await context.cookies(),[]);
   assert.deepEqual([...external],[]);assert.deepEqual(errors,[]);
  }));
  for(const prefix of ['', 'almeida-e-mileski-advocacia/']){
   summary.checks.push(await check(`all internal links with prefix /${prefix}`,async()=>{
    for(const route of routes.filter(r=>r!=='404.html')){
     await page.goto(base+prefix+route);
     const hrefs=await page.locator('a[href]').evaluateAll(els=>els.map(e=>e.href));
     for(const href of [...new Set(hrefs)]){
      const url=new URL(href);if(url.origin!==new URL(base).origin)continue;
      if(prefix)assert.ok(url.pathname.startsWith('/'+prefix),url.href);
      const response=await context.request.get(url.href);assert.ok(response.ok(),`${url.href}: ${response.status()}`);
     }
    }
    const miss=await page.goto(base+prefix+'inexistente/aninhada/');assert.equal(miss.status(),404);
    assert.equal(await page.locator('#home-link').getAttribute('href'),prefix?'/'+prefix:'/');
   }));
  }
  const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}}),plain=await nojs.newPage();
  summary.checks.push(await check('all routes usable without JavaScript',async()=>{
   for(const route of routes.filter(r=>r!=='404.html')){
    await plain.goto(base+route);await plain.locator('#menu-toggle').click();assert.ok(await plain.locator('#mobile-nav').isVisible());await plain.locator('#menu-toggle').click();
    if(await plain.locator('details.signature').count()){
     await plain.locator('details.signature>summary').first().click();assert.equal(await plain.locator('details.signature').first().getAttribute('open'),'');
     assert.ok((await plain.locator('.signature-body').first().innerText()).length>40);
    }
    assert.equal(await plain.locator('.accordion-tools:not([hidden])').count(),0);
   }
  }));
  await nojs.close();await context.close();await browser.close();result.engines.push(summary);
  await fs.writeFile(path.join(out,'verification.json'),JSON.stringify(result,null,2));
  console.log(engine,summary.checks.filter(c=>c.pass).length,'checks passed;',summary.axe.reduce((s,a)=>s+a.violations.length,0),'axe violations');
 }
 await fs.writeFile(path.join(out,'verification.json'),JSON.stringify(result,null,2));
 server.kill();
 if(result.failures.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
