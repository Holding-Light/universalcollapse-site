import glob
SCRIPT = '''<script>/*backlink-nav*/
(function(){
  var ref=document.referrer; if(!ref) return;
  var a=document.querySelector('.home-link'); if(!a) return;
  try{
    var u=new URL(ref), h=u.hostname, p=u.pathname;
    if(h!=='universalcollapse.com' && h!=='www.universalcollapse.com') return;
    if(p==='/'||p==='/index.html'){a.href='/';a.innerHTML='&larr; Home';}
    else if(p.slice(0,8)==='/roadmap'){a.href='/roadmap/';a.innerHTML='&larr; Reading Roadmap';}
    else if(p.slice(0,8)==='/library'){a.href='/library.html';a.innerHTML='&larr; The Library';}
  }catch(e){}
})();
</script>'''
n=0
for path in sorted(glob.glob("public/*.html")):
    html=open(path,encoding="utf-8").read()
    if 'class="home-link"' not in html: continue
    if '/*backlink-nav*/' in html: continue
    if '</body>' not in html: continue
    html=html.replace('</body>', SCRIPT+'\n</body>', 1)
    open(path,"w",encoding="utf-8").write(html)
    n+=1
print(f"pages updated: {n}")
