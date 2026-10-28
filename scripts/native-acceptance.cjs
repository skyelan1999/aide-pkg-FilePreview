"use strict";
// Explicitly targets an isolated, labelled test container. Never targets 9999.
const fs = require("node:fs"),
  https = require("node:https"),
  http = require("node:http"),
  cp = require("node:child_process"),
  crypto = require("node:crypto"),
  assert = require("node:assert/strict");
const container = "aide-file-preview-host";
const inspect = JSON.parse(
  cp.execFileSync("docker", ["inspect", container]),
)[0];
assert.equal(
  inspect.Config.Labels?.["aide.file-preview.acceptance"],
  "true",
  "Refusing a non-fixture Aide container",
);
const ca = cp.execFileSync("docker", [
  "exec",
  container,
  "cat",
  "/data/certs/cert.pem",
]);
const token = cp
  .execFileSync("docker", ["exec", container, "cat", "/data/auth/access-token"])
  .toString()
  .trim();
const root = ".agent-state/native-host";
fs.mkdirSync(root, { recursive: true });
function request(route, method = "GET", value, headers = {}) {
  const data = Buffer.isBuffer(value)
    ? value
    : value === undefined
      ? undefined
      : Buffer.from(JSON.stringify(value));
  return new Promise((resolve, reject) => {
    const req = https.request(
      "https://127.0.0.1:18499" + route,
      {
        method,
        ca,
        headers: {
          Authorization: "Bearer " + token,
          ...(data
            ? {
                "Content-Type": "application/json",
                "Content-Length": data.length,
              }
            : {}),
          ...headers,
        },
      },
      (res) => {
        const parts = [];
        res.on("data", (c) => parts.push(c));
        res.on("end", () => {
          const bytes = Buffer.concat(parts);
          let result;
          try {
            result = JSON.parse(bytes);
          } catch (_) {
            result = bytes.toString();
          }
          resolve({ status: res.statusCode, value: result, bytes });
        });
      },
    );
    req.setTimeout(20000, () => req.destroy(Error("Native host timeout")));
    req.on("error", reject);
    req.end(data);
  });
}
async function open() {
  const r = await request("/api/plugins/file-preview/workbench/open", "POST", {});
  assert.equal(r.status, 200, JSON.stringify(r.value));
  const page = await request(r.value.url);
  assert.equal(page.status, 200);
  return { ...r.value, html: page.bytes, calls: 0, sequence: 0 };
}
async function invoke(bridge, tool, args) {
  if (bridge.calls >= 90) {
    const r = await request(
      "/api/plugins/file-preview/workbench/" + bridge.bridge.instanceId + "/renew",
      "POST",
      {},
    );
    assert.equal(r.status, 200);
    bridge.bridge.instanceId = r.value.instanceId;
    bridge.calls = 0;
  }
  bridge.calls++;
  const r = await request(
    "/api/plugins/file-preview/workbench/" + bridge.bridge.instanceId + "/call",
    "POST",
    {
      protocol: 1,
      requestId: "native_" + ++bridge.sequence,
      method: "tool.call",
      tool,
      arguments: args,
    },
  );
  if (r.status !== 200) throw Error(JSON.stringify(r.value));
  return r.value;
}
async function install() {
  const version = JSON.parse(fs.readFileSync("manifest.json")).version,
    zip = fs.readFileSync("dist/file-preview-" + version + "-preview.zip"),
    b = "file-preview-" + crypto.randomBytes(10).toString("hex");
  const body = Buffer.concat([
    Buffer.from(
      "--" +
        b +
        '\r\nContent-Disposition: form-data; name="bundle"; filename="file-preview.zip"\r\nContent-Type: application/zip\r\n\r\n',
    ),
    zip,
    Buffer.from("\r\n--" + b + "--\r\n"),
  ]);
  const exists = await request("/api/plugins");
  const plugins = Array.isArray(exists.value)
    ? exists.value
    : exists.value.plugins || [];
  const route = plugins.some((p) => p.id === "file-preview")
    ? "/api/plugins/file-preview/upgrade"
    : "/api/plugins/bundle";
  const r = await request(route, "POST", body, {
    "Content-Type": "multipart/form-data; boundary=" + b,
  });
  assert.ok([200, 201].includes(r.status), JSON.stringify(r.value));
  const engineToken=fs.readFileSync('.file-preview-engine.env','utf8').trim().split('=')[1];
  const configured=await request('/api/plugins/file-preview/settings','PUT',{settings:{engineURL:'http://host.docker.internal:18510',engineToken}});
  assert.equal(configured.status,200,configured.value?.error);
  console.log("Native ZIP install/upgrade and isolated settings: PASS");
}
async function test() {
 const bridge=await open();const receipts=[];
 try{
  const health=(await invoke(bridge,'file_preview_status',{})).result;
  assert.equal(health.ok,true);assert.match(health.hostImageResults,/ready/);
  for(const name of ['two-pages.pdf','sample.docx','sample.pptx','sample.xlsx','quadrants.png','sample.md','sample.html']){
   const result=(await invoke(bridge,'file_preview_render',{fileSource:'workspace',path:name,pages:[1],dpi:120})).result;
   assert.equal(result.source.sha256,crypto.createHash('sha256').update(fs.readFileSync('.agent-state/fixtures/'+name)).digest('hex'));
   assert.equal(result.images.length,1);assert.equal(result.images[0].page,1);
   assert.equal(crypto.createHash('sha256').update(Buffer.from(result.images[0].dataBase64,'base64')).digest('hex'),result.images[0].sha256);
   receipts.push({name,totalPages:result.totalPages,hostSource:true,imageBytes:Buffer.from(result.images[0].dataBase64,'base64').length});
  }
  const crop=(await invoke(bridge,'file_preview_render',{path:'two-pages.pdf',pages:[2],crop:{x:.5,y:0,width:.5,height:.5},dpi:180})).result;
  assert.equal(crop.coverageComplete,false);assert.equal(crop.images[0].crop.x,.5);
  fs.writeFileSync(root+'/acceptance.json',JSON.stringify({nativeInstall:'PASS',sourceReads:'PASS',formats:receipts,crop:'PASS',hostImageCapability:'PASS',hostImage:inspect.Config.Image,hostBinarySha256:crypto.createHash('sha256').update(cp.execFileSync('docker',['exec',container,'cat','/usr/local/bin/aide'],{maxBuffer:400*1024*1024})).digest('hex')},null,2));
  console.log('Native installed plugin: seven formats, authorized source hashes, real image bytes and crop PASS');
 }finally{await request('/api/plugins/file-preview/workbench/'+bridge.bridge.instanceId,'DELETE')}
}
async function serve() {
  let bridge;
  const server = http.createServer(async (req, res) => {
    try {
      if (req.method === "GET" && req.url === "/") {
        if (bridge)
          await request(
            "/api/plugins/file-preview/workbench/" + bridge.bridge.instanceId,
            "DELETE",
          );
        bridge = await open();
        res.setHeader("Content-Type", "text/html; charset=utf-8");
        return res.end(
          `<!doctype html><html><style>html,body,iframe{margin:0;width:100%;height:100%;border:0;overflow:hidden}#proposal{position:absolute;bottom:0;left:0;right:0;background:#34485d;color:white;padding:10px;font:12px system-ui}</style><iframe src="/viewer" sandbox="allow-scripts"></iframe><div id="proposal" hidden></div><script>const frame=document.querySelector('iframe');window.addEventListener('message',e=>{if(e.source!==frame.contentWindow||e.data?.type!=='aide.workbench.ready')return;const c=new MessageChannel();c.port1.onmessage=async e=>{const m=e.data;try{const r=await fetch('/call',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(m)}),v=await r.json();if(v.status==='proposal_pending'){document.querySelector('#proposal').hidden=false;document.querySelector('#proposal').textContent='真实 Aide 已生成待审批提案；测试页不会自动批准。在实际 Aide 主窗口处理审批。';}c.port1.postMessage({...v,requestId:m.requestId})}catch(err){c.port1.postMessage({status:'error',requestId:m.requestId,error:err.message})}};frame.contentWindow.postMessage({type:'aide.workbench.connect',protocol:1,pluginId:'file-preview',tools:${JSON.stringify(bridge.bridge.tools)},capabilities:[]},'*',[c.port2])});</script></html>`,
        );
      }
      if (req.method === "GET" && req.url === "/viewer" && bridge) {
        res.setHeader("Content-Type", "text/html; charset=utf-8");
        res.setHeader(
          "Content-Security-Policy",
          "default-src 'none'; script-src 'unsafe-inline' blob:; style-src 'unsafe-inline'; img-src data: blob:; connect-src 'none'; worker-src blob:; frame-ancestors 'self'",
        );
        return res.end(bridge.html);
      }
      if (req.method === "POST" && req.url === "/call" && bridge) {
        if (
          req.headers.origin !== "http://127.0.0.1:18511" ||
          req.headers["content-type"] !== "application/json"
        )
          throw Error("Test origin rejected");
        let body = "";
        for await (const c of req) {
          body += c;
          if (body.length > 32768) throw Error("Request budget");
        }
        const m = JSON.parse(body);
        if (m.method !== "tool.call" || !bridge.bridge.tools.includes(m.tool))
          throw Error("Undeclared test method");
        const result = await invoke(bridge, m.tool, m.arguments);
        res.setHeader("Content-Type", "application/json");
        return res.end(JSON.stringify({ ...result, requestId: m.requestId }));
      }
      res.writeHead(404);
      res.end();
    } catch (e) {
      res.writeHead(400, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ status: "error", error: e.message }));
    }
  });
  server.listen(18511, "127.0.0.1", () =>
    console.log(
      "Native workbench test page: http://127.0.0.1:18511 (HTTPS upstream certificate pinned; no real user data)",
    ),
  );
  const close = async () => {
    if (bridge)
      await request(
        "/api/plugins/file-preview/workbench/" + bridge.bridge.instanceId,
        "DELETE",
      ).catch(() => {});
    server.close();
  };
  process.on("SIGTERM", () => void close());
  process.on("SIGINT", () => void close());
}
(async () => {
  await install();
  await test();
  if (process.argv.includes("--serve")) await serve();
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
