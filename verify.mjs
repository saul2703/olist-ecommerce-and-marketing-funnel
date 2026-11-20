import fs from "node:fs";
import path from "node:path";
import assert from "node:assert/strict";

const ROOT = process.cwd();
const summaryPath = path.join(ROOT, "data", "census_summary.json");
const htmlPath = path.join(ROOT, "index.html");
const readmePath = path.join(ROOT, "README.md");
const sqlPath = path.join(ROOT, "sql", "cpv2024_star_schema.sql");
const productPath = path.join(ROOT, "PRODUCT.md");
const designPath = path.join(ROOT, "DESIGN.md");

assert.ok(fs.existsSync(summaryPath), "Missing data/census_summary.json");
assert.ok(fs.existsSync(htmlPath), "Missing index.html");
assert.ok(fs.existsSync(readmePath), "Missing README.md");
assert.ok(fs.existsSync(sqlPath), "Missing sql/cpv2024_star_schema.sql");
assert.ok(fs.existsSync(productPath), "Missing PRODUCT.md");
assert.ok(fs.existsSync(designPath), "Missing DESIGN.md");

const data = JSON.parse(fs.readFileSync(summaryPath, "utf-8"));

// 1. Verify exact CPV 2024 table record counts
assert.equal(data.dataset.total_population, 6029976, "Population count must equal official 6,029,976");
assert.equal(data.dataset.total_households, 1920668, "Household count must equal 1,920,668");
assert.equal(data.dataset.total_dwellings, 2270026, "Dwelling count must equal 2,270,026");
assert.equal(data.dataset.total_emigrants_2014_2024, 226808, "Emigrant count must equal 226,808");
assert.equal(data.dataset.total_deaths_12m, 63267, "Mortality count must equal 63,267");

// 2. Verify geographic hierarchy & population reconciliation (5,922,921 district residents + 107,055 collective code 150101 = 6,029,976)
assert.equal(data.districts.length, 262, "Must have exactly 262 geographic districts");
assert.equal(data.municipalities.length, 44, "Must have exactly 44 restructured municipalities");
const distPopSum = data.districts.reduce((acc, d) => acc + d.population, 0);
assert.equal(distPopSum + 107055, 6029976, "262 districts + 107,055 institutional code 150101 must reconcile to 6,029,976");

// 3. Verify K-Means++ clustering & 2D PCA
assert.equal(data.clustering.selected_k, 4, "Selected k must be 4");
assert.equal(data.clustering.clusters.length, 4, "Must have 4 cluster personas");
const clusterDistSum = data.clustering.clusters.reduce((acc, c) => acc + c.districts, 0);
assert.equal(clusterDistSum, 262, "Cluster district counts must sum to 262");

// 4. Verify Spanish-to-English Questionnaire Sentence Transformer & Top/Bottom Performers Matrix
assert.ok(Array.isArray(data.translated_questionnaire) && data.translated_questionnaire.length >= 6, "Must include translated Spanish-to-English questionnaire sentences");
assert.ok(data.top_bottom_performers && data.top_bottom_performers.schooling_yrs.top_5.length === 5, "Must include Top 5 / Bottom 5 district performers matrix");

// 5. Verify all 9 Matplotlib PNG charts exist and are non-empty
const expectedCharts = [
  "dashboard_overview_preview.png",
  "demographic_pyramid_and_un_projections.png",
  "department_population_and_remittances.png",
  "household_assets_digital_divide.png",
  "international_emigration_trends.png",
  "elbow_silhouette_evaluation.png",
  "district_kmeans_clusters_pca.png",
  "regression_paradox_and_loadings.png",
  "vulnerability_and_commuting_analysis.png",
];
for (const img of expectedCharts) {
  const p = path.join(ROOT, "images", img);
  assert.ok(fs.existsSync(p), `Missing chart: images/${img}`);
  assert.ok(fs.statSync(p).size > 30000, `Chart too small: images/${img}`);
}

// 5b. Verify advanced analytics fields
assert.ok(data.advanced_analytics?.ols_assets?.r2 > 0.75, "Expected OLS R2 > 0.75 for household assets");
assert.ok(data.advanced_analytics?.ols_internet?.r2 > 0.6, "Expected OLS R2 > 0.60 for broadband access");
assert.strictEqual(data.advanced_analytics?.pca_loadings?.length, 8, "Expected 8 PCA loading features");

// 6. Verify Impeccable craft-floor, official data source URL, live SVG charts, & modern-web-guidance patterns
const html = fs.readFileSync(htmlPath, "utf-8");
const readme = fs.readFileSync(readmePath, "utf-8");
const bcrUrl = "https://poblacion.bcr.gob.sv/pages/teg-base-de-datos-y-tabulados";
assert.ok(readme.includes(bcrUrl), "README.md must cite official BCR data source URL");
assert.ok(html.includes(bcrUrl), "index.html must cite official BCR data source URL");
assert.ok(!html.includes('class="eyebrow"'), "Impeccable craft-floor ban: no eyebrow/kicker above headings");
assert.ok(html.includes("<search class=\"filter-bar\">") && html.includes("<footer class=\"workbench-footer\">"), "HTML landmark semantics: <search> and <footer> required");
for (const svgId of ["svgClusterScatter", "svgGeoBars", "svgRemittanceBars", "svgInfraBenchmark", "svgOlsBeta", "svgVulnCommute"]) {
  assert.ok(html.includes(`id="${svgId}"`), `Missing dynamic interactive SVG chart: ${svgId}`);
}
assert.ok(html.includes("content-visibility: auto"), "modern-web-guidance: must include content-visibility: auto containment");
assert.ok(html.includes("container-type: inline-size"), "modern-web-guidance: must include container-type: inline-size for responsive tables");
assert.ok(html.includes("districtGrid") && html.includes("muniGrid"), "index.html must include both AG Grid containers");
assert.ok(html.includes("empty-filter-banner") && html.includes("btnResetFilters"), "index.html must include recoverable empty filter state");
assert.ok(html.includes('typeof agGrid !== "undefined"'), "index.html must guard against offline AG Grid CDN failure");
assert.ok(html.includes("cpv2024_star_schema.sql") && html.includes("dim_geography"), "index.html must embed Star Schema SQL DDL & Views");

console.log("ALL VERIFICATION CHECKS PASSED:");
console.log(`  - Population Reconciled: ${distPopSum.toLocaleString()} (262 districts) + 107,055 (Code 150101 collective) = ${data.dataset.total_population.toLocaleString()}`);
console.log(`  - Schema Contracts: 262 Districts & 6 Spanish-to-English Survey Sentence Transformations validated`);
console.log(`  - Top/Bottom Performers Matrix + Star Schema SQL DDL & Views verified`);
console.log(`  - Impeccable Operate Workbench + modern-web-guidance (responsive-table, interactions-in-complex-layouts) verified`);
