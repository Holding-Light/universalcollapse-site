import os, sys
PHIL = {"JONUCT-2":"wp01","JONKFC":"kernel_first","JONUCT-3":"wp02","JONUCT-4":"wp03",
        "JONCMA-5":"cim_foundational","JONCRF":"collapse_reframed","JONWAN":"schrodinger",
        "JONBFS":"bfs","JONTST-4":"self_ego","JONAAS-4":"ai_synthetic","JONRAN-2":"records",
        "JONTSO-28":"soe"}
DOI  = {"DWM29":"uis","6M7VW":"soai","KZ8TP":"rice","MXYU2":"cogitate","JPXCU":"ai_sig_deployed"}
pairs = []
for pid, slug in PHIL.items():
    pairs.append((f"https://philarchive.org/rec/{pid}", f"/{slug}.html"))
for did, slug in DOI.items():
    pairs.append((f"https://doi.org/10.17605/OSF.IO/{did}", f"/{slug}.html"))
grand = 0
for path in ["public/library.html", "public/index.html"]:
    if not os.path.exists(path):
        print(f"  SKIP (not found): {path}"); continue
    html = open(path, encoding="utf-8").read()
    n = 0
    for old, new in pairs:
        for q in ('"', "'"):
            needle = f'href={q}{old}{q}'
            c = html.count(needle)
            if c:
                html = html.replace(needle, f'href={q}{new}{q}'); n += c
    open(path, "w", encoding="utf-8").write(html)
    print(f"  {path}: {n} links repointed")
    grand += n
print(f"TOTAL: {grand}")
