#!/usr/bin/env bash
# tools/build_architecture.sh — rebuild public/architecture.html from the JSX source of record.
#
#   bash tools/build_architecture.sh [path/to/UCT_Architecture_Map_v4.jsx]
#
# Pipeline (per Session_Handoff_Architecture_Map_2026_06_29.md §3, extended 2026-07-16):
#   1. esbuild the map (react@18 + lucide-react, IIFE, production)
#   2. GENERATE the no-JS static block from the JSX data (gen_static_block.mjs)
#      — kernel-gloss guard runs inside the generator; 8 elements or the build dies
#   3. assemble tools/architecture_shell.html (carries the canonical tag)
#   4. verification gate (verify_architecture.mjs): cold parse + executed parse
#   5. copy to public/architecture.html
#
# NEVER hand-edit public/architecture.html. Both shell fixes live in the template;
# the static block is derived, so map-content edits propagate on rebuild.
# First run needs network for npm. jsx=automatic is REQUIRED (no React default import).
set -euo pipefail
SRC="${1:-UCT_Architecture_Map_v4.jsx}"
TOOLS="$(cd "$(dirname "$0")" && pwd)"
BUILD="$TOOLS/_arch_build"

[ -f "$SRC" ] || { echo "source JSX not found: $SRC" >&2; exit 1; }
mkdir -p "$BUILD"
cp "$SRC" "$BUILD/map.jsx"
cd "$BUILD"

if [ ! -d node_modules/react ]; then
  npm init -y >/dev/null
  npm install react@18 react-dom@18 lucide-react esbuild jsdom >/dev/null
fi

cat > entry.jsx <<'EOF'
import { createRoot } from "react-dom/client";
import Map from "./map.jsx";
createRoot(document.getElementById("root")).render(<Map />);
EOF

npx esbuild entry.jsx --bundle --minify --format=iife --jsx=automatic \
  --loader:.jsx=jsx --define:process.env.NODE_ENV='"production"' --outfile=bundle.js

cp "$TOOLS/gen_static_block.mjs" "$TOOLS/verify_architecture.mjs" .
node gen_static_block.mjs map.jsx > static_block.html

SHELL_TMPL="$TOOLS/architecture_shell.html" node - <<'EOF'
import { readFileSync, writeFileSync } from "node:fs";
const shell  = readFileSync(process.env.SHELL_TMPL, "utf-8");
const stat   = readFileSync("static_block.html", "utf-8").trimEnd();
const bundle = readFileSync("bundle.js", "utf-8").replaceAll("</script>", "<\\/script>");
let out = shell;
for (const [ph, val] of [["<!--STATIC_BLOCK-->", stat],
                         ["<!--BUNDLE_SCRIPT-->", "<script>" + bundle + "</script>"]]) {
  if (out.split(ph).length !== 2) throw new Error("placeholder count wrong: " + ph);
  out = out.replace(ph, () => val);      // function form: "$$" etc. in payload stays literal
  if (!out.includes(val)) throw new Error("payload corrupted during assembly: " + ph);
}
writeFileSync("architecture.html", out);
EOF

node verify_architecture.mjs architecture.html

PUB="$TOOLS/../public"
if [ -d "$PUB" ]; then
  cp architecture.html "$PUB/architecture.html"
  echo "BUILT + VERIFIED -> public/architecture.html"
  echo "next: git add public/architecture.html && git commit && git push"
else
  echo "BUILT + VERIFIED -> $BUILD/architecture.html  (no public/ found from tools/)"
fi
