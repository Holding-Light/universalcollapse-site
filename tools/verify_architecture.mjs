// verify_architecture.mjs — gate for the built architecture.html (run from tools/ or build dir)
// Usage: node verify_architecture.mjs path/to/architecture.html
import { readFileSync } from "node:fs";
import { JSDOM } from "jsdom";
const path = process.argv[2] ?? "architecture.html";
const html = readFileSync(path, "utf-8");

// --- no-JS view (crawler) ---
const cold = new JSDOM(html);
const cd = cold.window.document;
const canon = cd.querySelectorAll('link[rel="canonical"]');
if (canon.length !== 1) throw new Error("canonical count " + canon.length);
if (canon[0].href !== "https://universalcollapse.com/architecture") throw new Error("canonical href: " + canon[0].href);
const staticEl = cd.querySelector("#root .static-map");
if (!staticEl) throw new Error("static block missing from #root in cold parse");
const words = staticEl.textContent.split(/\s+/).filter(Boolean).length;
if (words < 1200) throw new Error("static words only " + words);
for (const w of ["possibility","constraint","collapse","resolution","record","residue","record-time","update"])
  if (!staticEl.textContent.includes(w)) throw new Error("kernel gloss word missing: " + w);
if (!staticEl.querySelector("sup")) throw new Error("no <sup> typesetting — C^K lost");
console.log("no-JS view : PASS — canonical exact & unique; static block " + words + " words; 8-element gloss + C^K typesetting intact");

// --- executed view (browser) ---
const errors = [];
const live = new JSDOM(html, { runScripts: "dangerously", url: "https://universalcollapse.com/architecture" });
live.window.addEventListener("error", (e) => errors.push(e.message));
await new Promise((r) => setTimeout(r, 1500));
const d = live.window.document;
if (errors.length) throw new Error("runtime errors: " + errors.join(" | "));
const root = d.getElementById("root");
if (d.querySelector(".static-map")) throw new Error("static block survived render — should be replaced");
if (root.children.length < 1) throw new Error("app did not mount");
for (const marker of ["Constraint as Law", "sorting grammar"])
  if (!root.textContent.includes(marker)) throw new Error("default view missing marker: " + marker);
console.log("jsdom e2e  : PASS — zero runtime errors; app mounted; static block replaced by the interactive map");
