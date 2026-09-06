const http=require('http'),fs=require('fs'),os=require('os'),path=require('path'),{spawn}=require('child_process'),assert=require('assert');
const root=fs.mkdtempSync(path.join(os.tmpdir(),'walo-responsive-test-'));
const server=http.createServer((req,res)=>{res.setHeader('Content-Type','text/html');res.end('<html><body style="margin:0"><img src="https://example.invalid/test.png" style="display:block;width:min(60vw,900px);height:200px"><div style="height:1400px"></div><img src="https://example.invalid/lazy.png" style="width:100px;height:80px"></body></html>');});
server.listen(0,'127.0.0.1',()=>{
 fs.mkdirSync(path.join(root,'inventory'));
 fs.writeFileSync(path.join(root,'inventory/pages.json'),JSON.stringify({pages:[{slug:'fixture',url:`http://127.0.0.1:${server.address().port}/`}]}));
 const child=spawn(process.execPath,[path.join(__dirname,'responsive.cjs'),root],{env:process.env});let output='',error='';
 child.stdin.end('{}');child.stdout.on('data',d=>output+=d);child.stderr.on('data',d=>error+=d);
 child.on('close',code=>{
  try{assert.equal(code,0,error);const rows=output.trim().split('\n').map(JSON.parse).filter(r=>r.type==='measurement');assert.equal(rows.length,6,output);assert(rows.every(r=>r.assets.some(a=>a.url.endsWith('lazy.png'))),'scroll lazy asset');const small=rows.find(r=>r.width===390).assets.find(a=>a.url.endsWith('test.png'));const large=rows.find(r=>r.width===2560).assets.find(a=>a.url.endsWith('test.png'));assert.equal(Math.round(small.w),234);assert.equal(large.w,900);console.log('PASS: six real viewports, 900px max, capture after scroll');}
  catch(e){console.error(e);process.exitCode=1;}finally{server.close();fs.rmSync(root,{recursive:true,force:true});}
 });
});
