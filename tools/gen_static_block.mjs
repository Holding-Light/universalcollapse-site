// gen_static_block.mjs — generate the no-JS static summary for architecture.html
// FROM the JSX source of record. Never hand-edit the static block: it is derived.
// Usage: node gen_static_block.mjs UCT_Architecture_Map_v4.jsx > static_block.html
import { readFileSync, writeFileSync } from "node:fs";
import { pathToFileURL } from "node:url";

const src = readFileSync(process.argv[2] ?? "UCT_Architecture_Map_v4.jsx", "utf-8");

// ---- slice the pure-data constants (no JSX, no imports) ------------------
const start = src.indexOf("const C = {");
const end = src.indexOf("// UTILITIES");
if (start < 0 || end < 0) throw new Error("data slice markers not found — JSX layout changed; update gen_static_block.mjs");
const dataJs = src.slice(start, end)
  + "\nexport { LAYERS, HANDOFFS, SCHOOLS, METHODOLOGY, NEIGHBORS };\n";
if (/<[A-Za-z]/.test(dataJs)) throw new Error("JSX detected inside data slice — refusing to eval");
writeFileSync("_data_extract.mjs", dataJs);
const { LAYERS, HANDOFFS, SCHOOLS, METHODOLOGY, NEIGHBORS } =
  await import(pathToFileURL("_data_extract.mjs").href);

// ---- helpers ---------------------------------------------------------------
const esc = (s) => String(s).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
// Mirror of the map's KernelMath: ^run -> <sup>, _run -> <sub>, run = [A-Za-z0-9+]+
const km = (s) =>
  esc(s).replace(/([\^_])([A-Za-z0-9+]+)/g, (_, op, run) =>
    op === "^" ? `<sup>${run}</sup>` : `<sub>${run}</sub>`);

// ---- kernel-gloss guard (8 elements, "collapse" must be present) -----------
const gloss = METHODOLOGY.posture;
const required = ["possibility", "constraint", "collapse", "resolution", "record", "residue", "record-time", "update"];
for (const w of required) if (!gloss.includes(w)) throw new Error(`kernel gloss guard: "${w}" missing from METHODOLOGY.posture`);
if (!METHODOLOGY.kernelNote.includes("C^K")) throw new Error("kernel gloss guard: C^K missing from kernelNote");

// ---- counts (computed, never hard-coded) ------------------------------------
const schools = Object.values(SCHOOLS);
const nSorted = schools.filter((s) => s.register === "sorted").length;
const nApplied = schools.filter((s) => s.register === "applied").length;

// ---- build ------------------------------------------------------------------
const H = [];
H.push(`<section class="static-map" aria-label="Architecture map — static summary">`);
H.push(`<h1>Architecture Map</h1>`);
H.push(`<p class="sm-sub">Universal Collapse Theory — an orientation map. Interactive version requires JavaScript; the summary below carries the full structure.</p>`);
H.push(`<p>${km(METHODOLOGY.posture)}</p>`);
H.push(`<p class="sm-kernel">${km(METHODOLOGY.kernelNote)}</p>`);

// Phase stack with handoffs interleaved
H.push(`<h2>The Phase Stack — six domain layers</h2>`);
LAYERS.forEach((l, i) => {
  H.push(`<h3>${esc(l.label)} — ${esc(l.subtitle)}</h3>`);
  H.push(`<p class="sm-kernel">${km(l.kernel)}</p>`);
  H.push(`<p>${km(l.description)}</p>`);
  const papers = l.uctPapers.map((p) => esc(p.t) + (p.soon ? " · forthcoming" : "")).join("; ");
  H.push(`<p class="sm-papers">UCT papers: ${papers}.</p>`);
  const names = Object.values(SCHOOLS).filter((s) => s.layerId === l.id)
    .map((s) => esc(s.name) + (s.register === "applied" ? " (UCT-derived)" : ""));
  if (names.length) H.push(`<p class="sm-schools">Sorted here: ${names.join("; ")}.</p>`);
  const h = HANDOFFS[i];
  if (h) H.push(`<p class="sm-handoff">Handoff — ${esc(h.label)}: ${km(h.description)}</p>`);
});

// Registers
H.push(`<h2>Three registers</h2>`);
for (const r of METHODOLOGY.registers) {
  const count = r.key === "sorted" ? ` (${nSorted} entries)` : r.key === "applied" ? ` (${nApplied} entries)` : "";
  H.push(`<p><strong>${esc(r.label)}${count}.</strong> ${km(r.desc)}</p>`);
}

// Neighbors
H.push(`<h2>Neighbors — where UCT itself sits</h2>`);
H.push(`<p>${km(NEIGHBORS.intro)}</p>`);
for (const g of NEIGHBORS.groups) {
  H.push(`<h3>${esc(g.title)}</h3>`);
  H.push(`<p>${km(g.blurb)}</p>`);
  for (const m of g.members) {
    const attr = m.attribution ? ` (${esc(m.attribution)})` : "";
    H.push(`<p><strong>${esc(m.name)}${attr} — ${esc(m.stance)}.</strong> Shares: ${km(m.shares)} Diverges: ${km(m.diverges)}</p>`);
  }
}
H.push(`<p>${km(NEIGHBORS.note)}</p>`);

// Operating posture
H.push(`<h2>Operating posture</h2>`);
H.push(`<p><strong>Tier 0 — assumed and cleared first.</strong> ${METHODOLOGY.operatingPosture.t0.map(km).join(" ")}</p>`);
H.push(`<p><strong>Tier 30 — Primes (ground-clearing).</strong> ${METHODOLOGY.operatingPosture.t30.map(km).join(" ")}</p>`);

// Claim-level firewall + identity
H.push(`<h2>Claim level</h2>`);
H.push(`<p>${km(METHODOLOGY.claimLevel)}</p>`);
H.push(`<p class="sm-id">${km(METHODOLOGY.identity)} ${km(METHODOLOGY.updates)}</p>`);
H.push(`</section>`);

process.stdout.write(H.join("\n") + "\n");
