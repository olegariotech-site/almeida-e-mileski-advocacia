const fs=require('node:fs/promises');
const path=require('node:path');
const {spawn}=require('node:child_process');
(async()=>{
 const out=process.argv[2];if(!out)throw Error('Pass output directory');await fs.mkdir(out,{recursive:true});
 const {default:lighthouse}=await import(require.resolve('lighthouse'));
 const {launch}=await import(require.resolve('chrome-launcher'));
 const mod=require('@sparticuz/chromium'),chromium=mod.default||mod;
 const server=spawn('python3',[path.join(__dirname,'serve.py')],{stdio:['ignore','pipe','pipe']});
 process.on('exit',()=>server.kill());
 await new Promise((resolve,reject)=>{server.stdout.once('data',resolve);server.once('error',reject)});
 const chrome=await launch({chromePath:await chromium.executablePath(),chromeFlags:[...chromium.args,'--headless','--no-sandbox']});
 const areas=JSON.parse(await fs.readFile(path.join(__dirname,'../content/areas.json'),'utf8'));
 const routes=['','o-escritorio/','as-advogadas/',...areas.map(a=>'areas/'+a.slug+'/'),'conteudos/','contato/','politica-de-privacidade/','404.html'];
 const summary={at:new Date().toISOString(),conditions:'localhost; Lighthouse simulated mobile default throttling; one cold navigation per route; no field data; preview noindex retained',runs:[]};
 try{
  for(const route of routes.filter(route=>!process.env.PERFORMANCE_ROUTES||JSON.parse(process.env.PERFORMANCE_ROUTES).includes(route))){
   const name=(route||'home').replaceAll('/','-').replace(/-$/,'');
   const {lhr,report}=await lighthouse('http://127.0.0.1:8765/'+route,{port:chrome.port,output:['json','html'],logLevel:'error',onlyCategories:['performance','accessibility','best-practices','seo']});
   await fs.writeFile(path.join(out,name+'.json'),report[0]);await fs.writeFile(path.join(out,name+'.html'),report[1]);
   const entry={route,scores:Object.fromEntries(Object.entries(lhr.categories).map(([k,v])=>[k,Math.round(v.score*100)])),lcp_ms:lhr.audits['largest-contentful-paint'].numericValue,cls:lhr.audits['cumulative-layout-shift'].numericValue,tbt_ms:lhr.audits['total-blocking-time'].numericValue,failed:Object.values(lhr.audits).filter(a=>a.score!==null&&a.score<1&&a.details?.type!=='debugdata').map(a=>({id:a.id,title:a.title,score:a.score,displayValue:a.displayValue}))};
   summary.runs.push(entry);await fs.writeFile(path.join(out,'summary.json'),JSON.stringify(summary,null,2));
   console.log(name,JSON.stringify(entry.scores),'LCP',Math.round(entry.lcp_ms),'CLS',entry.cls);
  }
 }finally{await chrome.kill();server.kill();}
})().catch(e=>{console.error(e);process.exit(1)});
