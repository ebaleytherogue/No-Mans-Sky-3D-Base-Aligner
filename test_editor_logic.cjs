const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const template=fs.readFileSync(path.join(__dirname,'nms_base_editor.html'),'utf8').match(/<script>([\s\S]*)<\/script>/)[1];
const part=(id,p)=>({ObjectID:id,Position:p,Up:[0,2,0],At:[0,0,3],UserData:{keep:42}});
const fixture=()=>({Owner:{UID:'synthetic'},Position:[1,2,3],Forward:[0,0,1],GalacticAddress:'test',Objects:[part('^BASE_FLAG',[0,0,0]),part('^FLOOR',[2,3,4]),part('^FLOOR',[8,9,10]),part('^OTHER',[-2,0,4])]});
function load(before=fixture(),after=null){const els={},ctx=new Proxy({},{get:()=>()=>{}});let blob;
 const el=id=>els[id]??={value:['mode'].includes(id)?'orbit':0,checked:true,disabled:false,options:[],append(o){this.options.push(o)},replaceChildren(){this.options=[]},clientWidth:900,clientHeight:700,getContext:()=>ctx};
 const s={document:{getElementById:el,createElement:()=>({click(){},append(){}})},window:{devicePixelRatio:1,addEventListener(){}},Blob,URL:{createObjectURL(b){blob=b;return 'test'},revokeObjectURL(){}},setTimeout(){},console};vm.createContext(s);vm.runInContext(template.replace('/*BASE_DATA*/null',JSON.stringify({before,after})),s);return {e:expr=>vm.runInContext(expr,s),els,getBlob:()=>blob};}
const json=x=>JSON.parse(JSON.stringify(x));const near=(a,b)=>{if(Array.isArray(a)){assert.equal(a.length,b.length);a.forEach((v,i)=>near(v,b[i]))}else assert.ok(Math.abs(a-b)<1e-9,`${a} != ${b}`)};
(async()=>{
 let b=fixture(),t=load(b);assert.equal(t.els.apply.disabled,true);assert.deepEqual(json(t.e('result()')),b);assert.match(t.els.status.textContent,/No meaningful/);
 t.e("$('rz').value=17;draw()");let edited=json(t.e('result()'));t.e('select(selected)');assert.deepEqual(json(t.e('result()')),edited);t.e('select(2)');near(t.e('result().Objects.map(o=>o.Position)'),edited.Objects.map(o=>o.Position));t.e("$('undo').onclick()");near(t.e('result().Objects.map(o=>o.Position)'),edited.Objects.map(o=>o.Position));
 t.e("$('download').onclick()");assert.deepEqual(JSON.parse(await t.getBlob().text()),json(t.e('result()')));
 t.e("$('reset').onclick()");assert.deepEqual(json(t.e('result()')),b);
 let after=structuredClone(b);after.Objects[1].Position=[7,13,24];after.Objects[1].Up=[-2,0,0];after.Objects[2].UserData={color:'changed'};after.Name='latest';after.Objects.reverse();t=load(b,after);assert.equal(t.e('calibrationIndex'),1);assert.equal(t.e('pair()[0]'),1);assert.equal(t.els.apply.disabled,false);assert.match(t.els.calibrationInfo.textContent,/Unrelated/);
 for(let mask=0;mask<8;mask++){t.e("$('reset').onclick()");t.e(`setOptions({axes:[${!!(mask&1)},${!!(mask&2)},${!!(mask&4)}],rotate:false});$('apply').onclick()`);const out=t.e('result()');near(out.Objects[2].Position,b.Objects[2].Position.map((v,k)=>v+((mask&(1<<k))?[5,10,20][k]:0)));assert.deepEqual(json(out.Objects[2].Up),b.Objects[2].Up);assert.deepEqual(json(out.Objects[0]),b.Objects[0]);assert.deepEqual(json(out.Objects[1]),after.Objects[2]);assert.deepEqual(json(out.Objects[2].UserData),{color:'changed'});}
 for(let mask=0;mask<8;mask++){t.e("$('reset').onclick()");t.e(`setOptions({axes:[${!!(mask&1)},${!!(mask&2)},${!!(mask&4)}],rotate:true});$('apply').onclick()`);near(t.e('result().Objects[2].Position'),[-4,9,10].map((v,k)=>v+((mask&(1<<k))?[5,10,20][k]:0)));near(t.e('result().Objects[2].Up'),[-2,0,0]);}
 t.e("$('reset').onclick();setOptions({axes:[true,true,true],rotate:true});$('rz').value=11;$('tx').value=4;draw();$('apply').onclick()");const once=json(t.e('result()'));assert.equal(t.e("Number($('rz').value)"),11);t.e("$('apply').onclick()");assert.deepEqual(json(t.e('result()')),once);t.e("$('download').onclick()");assert.deepEqual(JSON.parse(await t.getBlob().text()),once);
 t.e('select(2)');near(t.e('result().Objects.map(o=>o.Position)'),once.Objects.map(o=>o.Position));
 const noise=structuredClone(b);noise.Objects[2].Position[0]+=5e-7;t=load(b,noise);assert.equal(t.els.apply.disabled,true);t.e("$('apply').onclick()");assert.deepEqual(json(t.e('result().Objects[1]')),b.Objects[1]);
 const metadata=structuredClone(b);metadata.Objects[2].UserData={color:'new'};t=load(b,metadata);assert.equal(t.els.apply.disabled,true);assert.match(t.els.calibrationInfo.textContent,/Unrelated/);
 const multiple=structuredClone(b);multiple.Objects[1].Position[1]+=2;multiple.Objects[2].Position[1]+=2;assert.throws(()=>load(b,multiple),/Multiple parts/);
 const scaled=structuredClone(b);scaled.Objects[1].Up=[0,4,0];assert.throws(()=>load(b,scaled),/scale/);
 t=load(b);t.e("$('rz').value=8;draw()");const pre=json(t.e('result()'));t.e(`initialize(${JSON.stringify(after)})`);near(t.e('result().Objects.map(o=>o.Position)'),pre.Objects.map(o=>o.Position));assert.equal(t.e('calibrationIndex'),1);t.e("$('apply').onclick()");assert.equal(t.e("Number($('rz').value)"),8);t.e("$('undo').onclick();$('undo').onclick()");assert.equal(t.e('DATA.after'),null);
 // Exercise the actual upload handler, including rejection without losing edits.
 t=load(b);t.els.afterFile.files=[{text:async()=>JSON.stringify(after)}];await t.els.afterFile.onchange();assert.equal(t.els.apply.disabled,false);const good=json(t.e('result()'));t.els.afterFile.files=[{text:async()=>JSON.stringify(multiple)}];await t.els.afterFile.onchange();assert.match(t.els.calibrationInfo.textContent,/Multiple parts/);assert.deepEqual(json(t.e('result()')),good);
 // Moved wiring must not become a reference or receive the incidental After movement twice.
 const wired=fixture();wired.Objects.push(part('^U_POWERLINE',[10,20,30]),part('^U_POWERLINE',[-4,8,12]));
 wired.Objects[4].Up=[1,2,3];wired.Objects[4].At=[4,5,6];
 const wireAfter=structuredClone(wired);wireAfter.Objects[1].Position=[7,13,24];wireAfter.Objects[1].Up=[-2,0,0];
 wireAfter.Objects[4].Position=[999,888,777];wireAfter.Objects[4].At=[9,9,9];wireAfter.Objects[4].UserData={latest:true};wireAfter.Objects.reverse();
 t=load(wired,wireAfter);assert.equal(t.e('calibrationIndex'),1);assert.equal(t.e('DATA.pairs.some(([i])=>isWiring(DATA.before.Objects[i]))'),false);
 t.e("$('apply').onclick()");let wireOut=json(t.e('result()'));
 for(const i of [4,5]){const [x,y,z]=wired.Objects[i].Position;near(wireOut.Objects[i].Position,[10-y,x+11,z+20]);for(const k of ['Up','At']){const [u,v,w]=wired.Objects[i][k];near(wireOut.Objects[i][k],[-v,u,w])}}
 assert.deepEqual(wireOut.Objects[4].UserData,{latest:true});assert.deepEqual(wireOut.Objects[0],wired.Objects[0]);
 t.e("$('apply').onclick()");assert.deepEqual(json(t.e('result()')),wireOut);t.e("$('download').onclick()");assert.deepEqual(JSON.parse(await t.getBlob().text()),wireOut);
 const wireOnly=structuredClone(wired);wireOnly.Objects[4].Position[0]+=3;t=load(wired,wireOnly);assert.equal(t.els.apply.disabled,true);assert.deepEqual(json(t.e('result()')),wired);
 t=load(wired);t.els.afterFile.files=[{text:async()=>JSON.stringify(wireAfter)}];await t.els.afterFile.onchange();assert.equal(t.e('calibrationIndex'),1);t.e("$('apply').onclick()");near(t.e('result().Objects[4].Position'),wireOut.Objects[4].Position);
 const badWired=structuredClone(wireAfter);badWired.Objects[3].Position[0]+=2;assert.throws(()=>load(wired,badWired),/Multiple parts/);
 const addedWire=structuredClone(wireAfter);addedWire.Objects.push(part('^U_POWERLINE',[0,0,0]));t=load(wired,addedWire);assert.equal(t.e('calibrationIndex'),1);t.e("$('apply').onclick()");assert.deepEqual(json(t.e('result()')),wireOut);
 const removedWires=structuredClone(wireAfter);removedWires.Objects=removedWires.Objects.filter(o=>o.ObjectID!=='^U_POWERLINE');t=load(wired,removedWires);assert.equal(t.e('calibrationIndex'),1);t.e("$('apply').onclick()");near(t.e('result().Objects[4].Position'),wireOut.Objects[4].Position);assert.equal(t.e('result().Objects.length'),wired.Objects.length);
 // Optional private reproduction: never require or embed the user's exports.
 if(fs.existsSync('Before.nmsbase')&&fs.existsSync('After.nmsbase')){const original=JSON.parse(fs.readFileSync('Before.nmsbase')),latest=JSON.parse(fs.readFileSync('After.nmsbase'));t=load(original,latest);assert.equal(t.e('DATA.before.Objects[calibrationIndex].ObjectID'),'^U_MINIPORTAL');t.e("$('apply').onclick()");assert.equal(t.e('result().Objects.length'),original.Objects.length);near(t.e('result().Objects[calibrationIndex].Position'),latest.Objects[0].Position);console.log('Private Before/After reproduction passed.');}

 // Selective mode must preserve all unselected geometry and fixed computer.
 t=load(fixture());t.e("$('selective').checked=true;changeScope()");assert.equal(t.els.download.disabled,true);
 t.e("changeMembers(new Set([1]));$('ty').value=5;draw()");let selective=json(t.e('result()'));
 near(selective.Objects[1].Position,[2,8,4]);assert.deepEqual(selective.Objects[2],fixture().Objects[2]);
 t.e("$('undo').onclick()");assert.equal(t.e('members.size'),0);
 t.e("$('selective').checked=false;changeScope();$('ty').value=5;draw()");near(t.e('result().Objects[2].Position'),[8,14,10]);

 t=load(fixture(),after);t.e("$('selective').checked=true;changeScope();changeMembers(new Set([2]));$('apply').onclick()");
 assert.deepEqual(json(t.e('result().Objects[1]')),fixture().Objects[1]);
 near(t.e('result().Objects[2].Position'),[1,19,30]);
 t.e("$('undo').onclick()");assert.equal(t.e('applied'),false);
 // Both wire types, shared junctions, crossing endpoints, rotation, unresolved export guard.
 for(const id of ['^U_POWERLINE','^U_PORTALLINE']){
 const b=fixture();b.Objects[1].Position=[2,0,0];b.Objects[2].Position=[12,0,0];
 b.Objects.push(part(id,[2,0,0]));b.Objects[4].At=[11,0,0];b.Objects[4].Up=[0,1,0];
 t=load(b);t.e("$('selective').checked=true;changeScope();changeMembers(new Set([1]));$('ty').value=5;draw()");
 let out=json(t.e('result()'));near(out.Objects[4].Position,[2,5,0]);near(t.e('wireEnd(result().Objects[4])'),[12,0,0]);assert.equal(t.e('connectionReport.crossing'),1);assert.equal(t.els.download.disabled,false);
 assert.deepEqual(out.Objects[2],b.Objects[2]);assert.deepEqual(out.Objects[0],b.Objects[0]);
 t.e("$('rz').value=35;draw()");near(t.e('wireEnd(result().Objects[4])'),[12,0,0]);
 t.e("bindings[0]='unresolved';draw()");assert.equal(t.els.download.disabled,true);
 const previous=t.getBlob();t.e("$('download').onclick()");assert.equal(t.getBlob(),previous);
 t.e("bindings[0]='1';changeMembers(new Set([1,2]));$('rz').value=0;draw()");near(t.e('wireEnd(result().Objects[4])'),[12,5,0]);assert.equal(t.e('connectionReport.internal'),1);
 }
 // Offset sockets, scaled/rotated owner, shared socket precision, and free ends.
 {
 const b=fixture();b.Objects[1]=part('^U_BATTERY_S',[2,0,0]);
 b.Objects[1].Up=[-2,0,0];b.Objects[1].At=[0,0,1];
 const start=[2-.4816,0,1.5516],end=[20,5,3];
 const wire=(a,z)=>{const o=part('^U_POWERLINE',a),v=z.map((x,k)=>x-a[k]),n=Math.hypot(...v);o.At=v.map(x=>x*(n+1)/n);o.Up=[0,1,0];return o};
 b.Objects.push(wire(start,end),wire(start.map((x,k)=>x+(k===0?.00002:0)),[23,2,5]));
 t=load(b);assert.equal(t.e('junctions.length'),3);
 assert.equal(t.e("junctions.filter(n=>n.owner===1).length"),1);
 t.e("$('selective').checked=true;changeScope();changeMembers(new Set([1]));$('ty').value=5;draw()");
 assert.equal(t.e('connectionReport.unresolved'),0);assert.equal(t.els.download.disabled,false);
 near(t.e('result().Objects[4].Position'),start.map((x,k)=>x+(k===1?5:0)));
 near(t.e('wireEnd(result().Objects[4])'),end);
 near(t.e('result().Objects[4].Position'),t.e('result().Objects[5].Position'));
 t.e("$('rz').value=37;draw()");near(t.e('wireEnd(result().Objects[4])'),end);
 t.e("changeMembers(new Set([2]));draw()");
 assert.deepEqual(json(t.e('result().Objects[4]')),b.Objects[4]);
 }
 console.log('Socket checks passed: rotated/scaled owner, shared socket, fixed free ends, unaffected wire preservation.');
 console.log('Selective checks passed: scope, empty selection, undo, unselected geometry, electrical/teleporter endpoints, crossing rotation, export guard.');
 console.log('Editor regression checks passed: manual mode, detection, 8 movement combinations, optional rotation, metadata, pivot, undo/reset, upload, Z export, repeated alignment.');
})();

