#!/usr/bin/env bash
# build_paper.sh — convert a UCT paper (.docx) to a styled HTML page.
#
#   ./build_paper.sh config.env
#
# Requires: pandoc >= 3.0
# Emits:    $OUT (an .html file) and exits nonzero on any lint failure.

set -euo pipefail

CONFIG="${1:?usage: build_paper.sh <config.env>}"
# shellcheck disable=SC1090
source "$CONFIG"

: "${SRC:?}" "${OUT:?}" "${TITLE:?}" "${DOI:?}" "${PUBLIC_URL:?}" "${TIER:?}" "${DATE:?}"
TEMPLATE="${TEMPLATE:-tools/uct-paper.html}"
FROM="${FROM:-docx}"

echo "→ $SRC"

# ---- source pin -----------------------------------------------------------
# Guards against the HTML silently diverging from the deposited record.
if [[ -n "${SRC_SHA256:-}" ]]; then
  actual="$(shasum -a 256 "$SRC" | cut -d' ' -f1)"
  if [[ "$actual" != "$SRC_SHA256" ]]; then
    echo "  FAIL  source hash mismatch — this docx is not the one that produced the deposit."
    echo "        expected $SRC_SHA256"
    echo "        actual   $actual"
    echo "        Adjudicate before building. Do not override."
    exit 2
  fi
  echo "  source pinned: ${SRC_SHA256:0:16}…"
fi

# ---- atomic write ---------------------------------------------------------
# Build to a scratch path and only move it into place on a clean lint. A failed
# lint used to leave the broken file on disk for `git add -A` to find.
FINAL="$OUT"
OUT="${OUT}.building"
trap 'rm -f "$OUT"' EXIT

pandoc "$SRC" \
  --from "$FROM" \
  --to html5 \
  --wrap=none \
  --mathml \
  --toc --toc-depth=2 \
  --section-divs \
  --template="$TEMPLATE" \
  --metadata title="$TITLE" \
  --metadata subtitle="${SUBTITLE:-}" \
  --metadata tier="$TIER" \
  --metadata citation_title="${CITATION_TITLE:-$TITLE}" \
  --metadata citation_date="$DATE" \
  --metadata citation_doi="$DOI" \
  --metadata citation_pdf_url="${PDF_URL:-}" \
  --metadata public_url="$PUBLIC_URL" \
  --metadata landing_url="${LANDING_URL:-$PUBLIC_URL}" \
  --metadata short_title="${SHORT_TITLE:-Library}" \
  --metadata description="${DESCRIPTION:-}" \
  -o "$OUT"

# ---- anchor aliases -------------------------------------------------------
# Pandoc slugs are faithful but unmailable. Inject short aliases.
# Format: ALIASES="short-name=pandoc-generated-id short2=id2"
if [[ -n "${ALIASES:-}" ]]; then
  for pair in $ALIASES; do
    short="${pair%%=*}"; long="${pair#*=}"
    python3 - "$OUT" "$short" "$long" <<'PY'
import sys, re
out, short, long = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(out, encoding="utf-8").read()
if f'id="{short}"' in s:
    sys.exit(0)
pat = f'id="{long}"'
if pat not in s:
    sys.stderr.write(f"  !! alias target missing: {long}\n"); sys.exit(1)
s = s.replace(pat, f'id="{long}"', 1)
m = re.search(r'<section\s+id="' + re.escape(long) + r'"', s)
if not m:
    sys.stderr.write("  !! section tag not found\n"); sys.exit(1)
s = s[:m.start()] + f'<span id="{short}"></span>' + s[m.start():]
open(out, "w", encoding="utf-8").write(s)
PY
    echo "  alias #$short → #$long"
  done
fi

# ---- lint (MathML-aware) --------------------------------------------------
python3 - "$OUT" <<'PY'
import sys, re, json
out = sys.argv[1]
h = open(out, encoding="utf-8").read()
fail = 0

# Forbidden: C_K in MathML. Canonical is C^K_t; bare C^K is licensed shorthand
# (Symbols & Formulas Reference v1.6) and is NOT an error.
bad = re.findall(r'<msub>\s*<mi>C</mi>\s*<mi>K</mi>\s*</msub>', h)
if bad:
    print(f"  FAIL  forbidden C_K in MathML ×{len(bad)}"); fail = 1

# Forbidden: literal C_K in prose
prose = re.sub(r'<[^>]+>', ' ', h)
lit = re.findall(r'\bC_K\b', prose)
if lit:
    print(f"  FAIL  literal 'C_K' in text ×{len(lit)}"); fail = 1

# Placeholders that must never ship
for ph in ("XXXX", "TKTK", "citation_pdf_url\" content=\"\""):
    if ph in h:
        print(f"  FAIL  placeholder present: {ph}"); fail = 1

# Required tags
for tag in ('rel="canonical"', 'name="citation_doi"', 'name="citation_title"'):
    if tag not in h:
        print(f"  FAIL  missing: {tag}"); fail = 1

# JSON-LD must exist and must parse. This is the attribution surface: a model
# that retrieves the full text reads this to learn whose work it is.
m = re.search(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
if not m:
    print("  FAIL  missing JSON-LD block"); fail = 1
else:
    try:
        json.loads(m.group(1))
    except Exception as e:
        print(f"  FAIL  JSON-LD does not parse: {e}"); fail = 1

# A non-UTF-8 locale turns every em-dash into three U+FFFD and STILL emits valid
# JSON. json.loads() passes on that. This is the only check that catches it.
if "\ufffd" in h:
    n = h.count("\ufffd")
    print(f"  FAIL  U+FFFD replacement char x{n} — pandoc ran without a UTF-8 locale"); fail = 1

n_math = h.count("<math")
print(f"  math blocks: {n_math}")
print("  lint: " + ("FAILED" if fail else "clean"))
sys.exit(fail)
PY

mv "$OUT" "$FINAL"
echo "✓ $FINAL  ($(wc -c < "$FINAL") bytes)"
