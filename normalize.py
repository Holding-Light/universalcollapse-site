import re, glob
pat = re.compile(r'(https://universalcollapse\.com/[A-Za-z0-9_./-]+?)\.html')
total = 0
for path in sorted(glob.glob("public/*.html")) + ["public/sitemap.xml"]:
    s = open(path, encoding="utf-8").read()
    new, n = pat.subn(r'\1', s)
    if n:
        open(path, "w", encoding="utf-8").write(new)
        total += n
print(f"URLs de-.html'd: {total}")
