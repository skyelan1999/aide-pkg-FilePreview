const { test } = require("node:test"),
  assert = require("node:assert/strict"),
  fs = require("fs"),
  os = require("os"),
  path = require("path"),
  http = require("http"),
  crypto = require("crypto");
const plugin = require("../src/plugin");
test("paths, page bounds and crop cannot silently widen coverage", () => {
  const safe = plugin._test.safe;
  assert.deepEqual(safe({ path: "doc.pdf" }), { pages: [1], dpi: 120 });
  for (const args of [
    { path: "../secret" },
    { path: "/etc/passwd" },
    { path: "a\\b" },
    { path: "a", pages: [1, 1] },
    { path: "a", pages: [0] },
    { path: "a", pages: [1, 2, 3, 4, 5] },
    { path: "a", dpi: 1000 },
    { path: "a", crop: { x: 0.9, y: 0, width: 0.5, height: 1 } },
  ])
    assert.throws(() => safe(args));
});
test("all tools are source-backed read-only; renderer credentials never come from model arguments", () => {
  const tools = [];
  plugin.apply({ tool: (t) => tools.push(t) });
  assert.equal(tools.length, 4);
  for (const t of tools) {
    assert.deepEqual(t.scheduling, { resources: [] });
    assert.equal(t.parameters.additionalProperties, false);
    assert.ok(!t.parameters.properties.engineToken);
  }
});
test("renders authorized snapshot bytes, returns fingerprint, rejects revocation and escapes", async (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "preview-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const raw = Buffer.from("synthetic");
  fs.writeFileSync(path.join(root, "doc.pdf"), raw);
  let seen,
    revoked = false;
  const server = http.createServer(async (req, res) => {
    const chunks = [];
    for await (const b of req) chunks.push(b);
    seen = JSON.parse(Buffer.concat(chunks));
    res.setHeader("Content-Type", "application/json");
    res.end(JSON.stringify({ images: [{ page: 1 }], pagesRead: [1] }));
  });
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  t.after(() => server.close());
  const settings = {
    engineURL: "http://127.0.0.1:" + server.address().port,
    engineToken: "x".repeat(40),
  };
  let n = 0;
  const api = {
    sources: async (a) =>
      a.operation === "sources"
        ? {
            sources: [
              { id: "workspace", origin: revoked && n++ ? "changed" : "same" },
            ],
          }
        : { workspace: root, path: "doc.pdf" },
  };
  let result = await plugin._test.render({ path: "doc.pdf" }, api, settings);
  assert.equal(
    result.source.sha256,
    crypto.createHash("sha256").update(raw).digest("hex"),
  );
  assert.equal(seen.dataBase64, raw.toString("base64"));
  revoked = true;
  n = 0;
  await assert.rejects(
    plugin._test.render({ path: "doc.pdf" }, api, settings),
    /changed/,
  );
  api.sources = async (a) =>
    a.operation === "sources" ? {} : { workspace: root, path: "../outside" };
  await assert.rejects(plugin._test.render({ path: "doc.pdf" }, api, settings));
});
