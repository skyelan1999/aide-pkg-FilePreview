const fs = require("fs"),
  esbuild = require("esbuild");
(async () => {
  await esbuild.build({
    entryPoints: ["src/plugin.js"],
    bundle: true,
    platform: "node",
    target: "node18",
    outfile: "index.js",
  });
  fs.writeFileSync(
    "viewer.html",
    fs
      .readFileSync("src/viewer.html", "utf8")
      .replace(
        "<!--BRIDGE-->",
        "<script>" +
          fs.readFileSync("src/host-client.js", "utf8") +
          "</script>",
      ),
  );
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
