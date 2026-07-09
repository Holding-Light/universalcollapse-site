PHIL = {"JONUCT-2":"wp01","JONKFC":"kernel_first","JONUCT-3":"wp02","JONUCT-4":"wp03",
        "JONCMA-5":"cim_foundational","JONCRF":"collapse_reframed","JONWAN":"schrodinger",
        "JONBFS":"bfs","JONTST-4":"self_ego","JONAAS-4":"ai_synthetic","JONRAN-2":"records",
        "JONTSO-28":"soe"}
DOI  = {"DWM29":"uis","6M7VW":"soai","KZ8TP":"rice","MXYU2":"cogitate","JPXCU":"ai_sig_deployed"}
pairs = [(f"https://philarchive.org/rec/{p}", f"/{s}.html") for p,s in PHIL.items()] + \
        [(f"https://doi.org/10.17605/OSF.IO/{d}", f"/{s}.html") for d,s in DOI.items()]
path="public/roadmap/index.html"
html=open(path,encoding="utf-8").read()
n=0
for old,new in pairs:
    for q in ('"',"'"):
        needle=f'href={q}{old}{q}'
        c=html.count(needle)
        if c: html=html.replace(needle,f'href={q}{new}{q}'); n+=c
open(path,"w",encoding="utf-8").write(html)
print(f"roadmap links repointed: {n}")
