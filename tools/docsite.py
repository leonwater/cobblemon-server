"""docs/*.md → 문서 사이트 HTML (탭).  사용: python3 tools/docsite.py <출력.html> [play|dev]
사진은 ui/ 그대로라 docs/ui/*.jpg를 출력 옆 ui/에 두고 아티팩트 files로 같이 올림."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent.parent / 'docs'
# 파일 2개: play = 서버원에게 배포 (접속 방법·서버 안내·명령어), dev = 서버장·개발 (서버 여는 법·운영자 명령어·UI·관장·작업 규칙·스킬)
GROUPS = {'play': ('잡켓몬 서버 문서', [('접속방법', '접속 방법'), ('서버안내', '서버 안내'), ('명령어', '명령어')]),   # 서버원에게 배포
          'dev': ('잡켓몬 서버 개발 문서', [('서버_여는법', '서버 여는 법'), ('운영자_명령어', '운영자 명령어'), ('UI정리', 'UI 정리'), ('관장팀', '관장·사천왕 팀'), ('작업규칙', '작업 규칙'), ('스킬_플러그인', '스킬·플러그인')])}
TITLE, order = GROUPS[sys.argv[2] if len(sys.argv) > 2 else 'play']
order = [(f, n) for f, n in order if (D / f'{f}.md').exists()]
docs = [{'id': f, 'name': n, 'md': (D / f'{f}.md').read_text(encoding='utf-8')} for f, n in order]
html = r'''<title>@@TITLE@@</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Do+Hyeon&family=Noto+Sans+KR:wght@400;500;700&display=swap">
<style>
/* 레이아웃: 위 탭 줄(포켓몬 도감 느낌의 빨간 띠) + 가운데 읽기 칼럼 */
:root{--bg:#f5f4f1;--paper:#ffffff;--ink:#1f2328;--sub:#5c6470;--line:#e2e0da;--red:#d8343a;--red-ink:#ffffff;--code:#f1efe9;--link:#1f5fbf;
 --font-h:"Do Hyeon","Noto Sans KR",system-ui,sans-serif;--font-b:"Noto Sans KR",system-ui,sans-serif}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#15171b;--paper:#1d2026;--ink:#e8eaee;--sub:#a1a8b3;--line:#2f333b;--red:#c9353b;--red-ink:#ffffff;--code:#262a31;--link:#7fb0ff;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#15171b;--paper:#1d2026;--ink:#e8eaee;--sub:#a1a8b3;--line:#2f333b;--red:#c9353b;--red-ink:#ffffff;--code:#262a31;--link:#7fb0ff;color-scheme:dark}
body{background:var(--bg);color:var(--ink);font-family:var(--font-b);line-height:1.7}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:10;background:var(--red)}
header{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--red);color:var(--red-ink);
 padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:10px 0}
.top{max-width:900px;margin:0 auto;display:flex;align-items:center;gap:10px}
.ball{width:22px;height:22px;border-radius:50%;background:linear-gradient(#fff 0 0) center/100% 3px no-repeat,linear-gradient(var(--red-ink) 50%,#f1f1f1 50%);border:2px solid #222;flex:none}
h1.site{font-family:var(--font-h);font-weight:400;font-size:1.5rem;margin:0}
nav{max-width:900px;margin:8px auto 0;display:flex;gap:4px;overflow-x:auto}
nav button{font:inherit;font-size:.95rem;border:0;background:transparent;color:var(--red-ink);opacity:.8;padding:8px 12px;border-radius:8px 8px 0 0;cursor:pointer;white-space:nowrap}
nav button[aria-selected="true"]{background:var(--bg);color:var(--ink);opacity:1;font-weight:700}
nav button:focus-visible{outline:2px solid var(--red-ink);outline-offset:-4px}
main{padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:20px 60px}
article{max-width:900px;margin:0 auto;background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:20px clamp(16px,4vw,40px);min-width:0}
article h1,article h2,article h3{font-family:var(--font-h);font-weight:400;text-wrap:balance;line-height:1.3}
article h1{font-size:2rem;margin:.2em 0 .6em} article h2{font-size:1.45rem;margin:1.6em 0 .5em;padding-top:.6em;border-top:1px solid var(--line)} article h3{font-size:1.15rem;margin:1.2em 0 .4em}
article p,article li{max-width:68ch} article a{color:var(--link)}
article img{display:block;max-width:100%;border-radius:8px;border:1px solid var(--line);margin:10px 0}
article code{background:var(--code);padding:.1em .35em;border-radius:4px;font-size:.92em}
article pre{background:var(--code);padding:12px;border-radius:8px;overflow-x:auto} article pre code{background:none;padding:0}
.tw{overflow-x:auto} article table{border-collapse:collapse;font-size:.93rem;min-width:420px} article th,article td{border:1px solid var(--line);padding:6px 10px;text-align:left;vertical-align:top}
article th{background:var(--code)}
@media (prefers-reduced-motion:no-preference){article{animation:in .18s ease-out}@keyframes in{from{opacity:.6;transform:translateY(4px)}}}
</style>
<header><div class="top"><span class="ball" aria-hidden="true"></span><h1 class="site">@@TITLE@@</h1></div><nav id="tabs" role="tablist"></nav></header>
<main><article id="doc" role="tabpanel"></article></main>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/11.1.1/marked.min.js"></script>
<script>
const DOCS = @@DOCS@@;
const tabs = document.getElementById('tabs'), doc = document.getElementById('doc');
const linkMap = Object.fromEntries(DOCS.flatMap(d => [[d.id + '.md', d.id], ['docs/' + d.id + '.md', d.id]]));
function show(id){
  const d = DOCS.find(x => x.id === id) || DOCS[0];
  for (const b of tabs.children) b.setAttribute('aria-selected', b.dataset.id === d.id);
  doc.innerHTML = marked.parse(d.md);
  doc.querySelectorAll('table').forEach(t => { const w = document.createElement('div'); w.className = 'tw'; t.replaceWith(w); w.appendChild(t); });
  doc.querySelectorAll('a').forEach(a => { const h = a.getAttribute('href') || ''; const k = h.replace(/^\.\//,'');
    if (linkMap[k]) { a.href = '#' + linkMap[k]; } else if (/\.md$/.test(k)) { a.removeAttribute('href'); } else if (/^https?:/.test(h)) { a.target = '_blank'; a.rel = 'noopener'; } });
  window.scrollTo(0, 0);
}
for (const d of DOCS) { const b = document.createElement('button'); b.textContent = d.name; b.dataset.id = d.id; b.setAttribute('role','tab');
  b.onclick = () => { location.hash = d.id; }; tabs.appendChild(b); }
addEventListener('hashchange', () => show(decodeURIComponent(location.hash.slice(1))));
show(decodeURIComponent(location.hash.slice(1)));
</script>
'''
Path(sys.argv[1]).write_text(html.replace('@@TITLE@@', TITLE).replace('@@DOCS@@', json.dumps(docs, ensure_ascii=False).replace('</', '<\\/')), encoding='utf-8')
print('ok', len(docs))
