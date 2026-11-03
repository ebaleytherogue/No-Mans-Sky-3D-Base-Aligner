// Real Chromium smoke test, using its built-in DevTools protocol; no npm dependencies.
const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),{spawn,spawnSync}=require('node:child_process'),assert=require('node:assert/strict');
(async()=>{
 const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'nms-editor-'));
 const part=(id,p)=>({ObjectID:id,Position:p,Up:[0,1,0],At:[0,0,1],UserData:12});
 const before={Owner:{UID:'synthetic'},Position:[0,0,0],Forward:[0,0,1],GalacticAddress:'synthetic',Objects:[part('^BASE_FLAG',[0,0,0]),part('^FLOOR',[2,0,0]),part('^OTHER',[4,0,0])]};
 const after=structuredClone(before);after.Name='latest metadata';after.Objects[1].Position=[2,3,0];after.Objects[1].Up=[-1,0,0];
 fs.writeFileSync(path.join(tmp,'before.nmsbase'),JSON.stringify(before));fs.writeFileSync(path.join(tmp,'after.nmsbase'),JSON.stringify(after));
 const html=path.join(tmp,'preview.html');
 const build=spawnSync('py',['nms_base_align.py','3d',path.join(tmp,'before.nmsbase'),path.join(tmp,'after.nmsbase'),'-o',html],{encoding:'utf8'});assert.equal(build.status,0,build.stderr);
 const chrome=spawn('C:/Program Files/Google/Chrome/Application/chrome.exe',['--headless=new','--disable-gpu','--no-first-run','--remote-debugging-port=0',`--user-data-dir=${path.join(tmp,'profile')}`,'about:blank'],{windowsHide:true,stdio:'ignore'});
 let ws;
 try{
 const portFile=path.join(tmp,'profile','DevToolsActivePort');
 for(let n=0;n<100&&!fs.existsSync(portFile);n++)await new Promise(r=>setTimeout(r,100));
 const port=fs.readFileSync(portFile,'utf8').split('\n')[0];
 const pages=await (await fetch(`http://127.0.0.1:${port}/json`)).json();
 ws=new WebSocket(pages.find(p=>p.type==='page').webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);
 let id=0;const pending=new Map();ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){pending.get(m.id)?.(m);pending.delete(m.id)}};
 const send=(method,params={})=>new Promise((resolve,reject)=>{const n=++id;pending.set(n,m=>m.error?reject(Error(JSON.stringify(m.error))):resolve(m.result));ws.send(JSON.stringify({id:n,method,params}))});
 const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
 await send('Emulation.setDeviceMetricsOverride',{width:1280,height:900,deviceScaleFactor:1,mobile:false});await send('Runtime.enable');await send('Page.enable');await send('Page.navigate',{url:require('node:url').pathToFileURL(html).href});
 for(let n=0;n<100;n++){if(await evaluate("document.readyState==='complete' && !!document.getElementById('reference')?.options.length"))break;await new Promise(r=>setTimeout(r,100))}
 assert.equal(await evaluate("document.getElementById('reference').options.length"),1);
 assert.equal(await evaluate('result().Name'),'latest metadata');
 await evaluate("$('apply').click()");
 let out=await evaluate('result()');assert.deepEqual(out.Objects[0],before.Objects[0]);assert.deepEqual(out.Objects[1],after.Objects[1]);assert.deepEqual(out.Objects[2].Position,[2,5,0]);assert.deepEqual(out.Objects[2].Up,[-1,0,0]);
 await evaluate("$('tx').focus();$('tx').value=4;$('tx').dispatchEvent(new Event('input'))");
 out=await evaluate('result()');assert.deepEqual(out.Objects[2].Position,[6,5,0]);assert.deepEqual(out.Objects[0],before.Objects[0]);
 await evaluate("$('undo').click()");assert.deepEqual((await evaluate('result()')).Objects[2].Position,[2,5,0]);
 await evaluate("$('mode').value='rotate';$('axis').value='0';$('mode').dispatchEvent(new Event('change'));canvas.setPointerCapture=()=>{};canvas.onpointerdown({pointerId:1,button:0,clientX:100,clientY:100});canvas.onpointermove({clientX:130,clientY:100});canvas.onpointerup({clientX:130,clientY:100})");
 assert.equal(await evaluate("Number($('rx').value)"),9);
 await evaluate("$('reset').click()");assert.deepEqual((await evaluate('result()')).Objects,before.Objects);
 await evaluate("window.captured=null;URL.createObjectURL=b=>{window.captured=b;return 'blob:synthetic'};HTMLAnchorElement.prototype.click=function(){};$('download').click()");
 const downloaded=await send('Runtime.evaluate',{expression:'captured.text()',awaitPromise:true,returnByValue:true});assert.deepEqual(JSON.parse(downloaded.result.value).Objects,before.Objects);
 await evaluate("document.querySelector('aside').scrollTop=0");const screenshot=await send('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(tmp,'preview.png'),Buffer.from(screenshot.data,'base64'));
 console.log('Browser checks passed: load, correction, fixed computer, metadata, manual movement, undo, drag rotation, reset, download.');console.log('Screenshot: '+path.join(tmp,'preview.png'));
 }finally{if(ws)ws.close();chrome.kill()}
})().catch(e=>{console.error(e);process.exitCode=1});
