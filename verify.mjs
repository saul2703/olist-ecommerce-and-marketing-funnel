import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const html = fs.readFileSync(path.join(root, "index.html"), "utf8");
const summary = JSON.parse(fs.readFileSync(path.join(root, "data/summary.json"), "utf8"));

const checks = [
  ["overview.total_orders == 99441", summary.overview.total_orders === 99441],
  ["overview.mql_leads == 8000", summary.overview.mql_leads === 8000],
  ["overview.closed_deals == 842", summary.overview.closed_deals === 842],
  ["overview.active_funnel_sellers == 380", summary.overview.active_funnel_sellers === 380],
  ["index.html uses IBM Plex Sans", html.includes("IBM Plex Sans")],
  ["index.html uses portfolio accent #0f52ba", html.includes("#0f52ba")],
  ["index.html has Dark/Light theme toggle", html.includes("btnTheme") && html.includes('data-theme="dark"')],
  ["index.html has EN/ES toggle", html.includes("btnLang")],
  ["index.html has inline SUMMARY_DATA", html.includes("const SUMMARY_DATA")],
];

let ok = true;
for (const [label, pass] of checks) {
  console.log((pass ? "PASS: " : "FAIL: ") + label);
  if (!pass) ok = false;
}
if (!ok) process.exit(1);
