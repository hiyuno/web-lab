// Actual browser measurements; JSON-lines progress on stdout.
const fs = require('fs');
const { chromium } = require('playwright');
const audit = process.argv[2];
const pages = JSON.parse(fs.readFileSync(audit + '/inventory/pages.json')).pages;
const widths = [390, 768, 1024, 1440, 1920, 2560];
const {password = ''} = JSON.parse(fs.readFileSync(0,'utf8') || '{}');
const emit = value => process.stdout.write(JSON.stringify(value) + '\n');
(async () => {
  const browser = await chromium.launch({headless: true, channel: process.env.WALO_BROWSER_CHANNEL || 'chrome'});
  const context = await browser.newContext({deviceScaleFactor: 1, reducedMotion: 'reduce'});
  const login = await context.newPage();
  const initial = await login.goto(pages[0].url,{waitUntil:'domcontentloaded',timeout:45000});
  if(initial?.status() === 401) {
    if(!password) {await browser.close();throw Error('The site is password-protected. Enter the password in Measure the site.');}
    await login.locator('#password').fill(password);
    try {
      await Promise.all([login.waitForNavigation({waitUntil:'domcontentloaded',timeout:15000}),login.locator('button[type="submit"]').click()]);
    } catch {await browser.close();throw Error('Could not access. Check the site password.');}
  }
  await login.close();
  // Media metadata is sufficient; do not stream all videos during the audit.
  await context.route('**/*', route => route.request().resourceType() === 'media' ? route.abort() : route.continue());
  let completed = 0;
  for (const entry of pages) {
    for (const width of widths) {
      const page = await context.newPage({viewport: {width, height: 1000}});
      try {
        await page.setViewportSize({width, height:1000});
        const response = await page.goto(entry.url, {waitUntil:'domcontentloaded', timeout:45000});
        if (!response || !response.ok()) throw Error('HTTP ' + response?.status());
        await page.waitForTimeout(900);
        const measures = new Map();
        const collect = async () => {
          const items = await page.evaluate(() => {
            const entries = [];
            for (const el of document.querySelectorAll('img, video, [style*="background-image"]')) {
              const r=el.getBoundingClientRect(), css=getComputedStyle(el);
              if (r.width<1 || r.height<1 || r.top>=innerHeight || r.bottom<=0 || css.visibility==='hidden' || css.display==='none' || Number(css.opacity)===0) continue;
              if(el.checkVisibility && !el.checkVisibility({checkOpacity:true,checkVisibilityCSS:true})) continue;
              const urls=[el.currentSrc,el.src,el.poster, ...Array.from(el.querySelectorAll('source')).map(s=>s.src)];
              for (const match of css.backgroundImage.matchAll(/url\(["']?(.*?)["']?\)/g)) urls.push(match[1]);
              for (const url of urls.filter(Boolean)) entries.push({url,w:r.width,h:r.height,fit:css.objectFit || css.backgroundSize});
            }
            return entries;
          });
          for (const m of items) measures.set(m.url+'|'+Math.round(m.w)+'|'+Math.round(m.h),m);
        };
        let pos=0, finished=false;
        for(let step=0;step<160;step++) {
          await collect();
          const height=await page.evaluate(()=>document.documentElement.scrollHeight);
          if(pos+1000>=height){finished=true;break;}
          pos=Math.min(pos+800,height-1000);
          await page.evaluate(y=>scrollTo(0,y),pos);
          await page.waitForTimeout(100);
        }
        if(!finished) throw Error('Page too long: incomplete traversal');
        emit({type:'measurement',page:entry.slug,url:entry.url,width,height:1000,assets:[...measures.values()]});
      } catch(error) { emit({type:'failure',page:entry.slug,width,error:error.message}); }
      finally {await page.close();emit({type:'progress',completed:++completed,total:pages.length*widths.length});}
    }
  }
  await browser.close(); emit({type:'done'});
})().catch(error=>{process.stderr.write(error.stack+'\n');process.exitCode=1;});
