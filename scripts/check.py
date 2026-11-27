#!/usr/bin/env python3
"""Check deploy surface, references and complete institutional service content."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from collections import Counter
import json
import hashlib

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
class Page(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.links=[];self.assets=[];self.text=[];self.h1=0;self.robots=[];self.scripts=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='h1':self.h1+=1
        if tag=='a' and 'href' in a:self.links.append(a['href'])
        if tag in ['link','img','script']:
            key='href' if tag=='link' else 'src'
            if key in a:self.assets.append(a[key])
        if tag=='meta' and a.get('name')=='robots':self.robots.append(a['content'])
        if tag=='script':self.scripts.append(a)
    def handle_data(self,data):self.text.append(data)

pages={}
for p in DIST.rglob('*.html'):
    parsed=Page();parsed.feed(p.read_text());pages[p]=parsed
    assert parsed.h1==1,(p,'h1')
    assert parsed.robots==['noindex,nofollow'],(p,'robots')
    assert not [id for id,c in Counter(parsed.ids).items() if c>1],(p,'duplicate IDs')
    for href in parsed.links+parsed.assets:
        u=urlsplit(href)
        if u.scheme or u.netloc:continue
        if p.name=='404.html' and u.path in ['/','/almeida-e-mileski-advocacia/']:continue
        dest=(p.parent/unquote(u.path)).resolve() if u.path else p
        if dest.is_dir():dest=dest/'index.html'
        assert dest.is_relative_to(DIST),(p,href,'escapes site')
        assert dest.exists(),(p,href,'missing file')
        if u.fragment and dest.suffix=='.html':
            target=Page();target.feed(dest.read_text());assert unquote(u.fragment) in target.ids,(p,href,'missing anchor')
    for script in parsed.scripts:
        assert script.get('src') in [None,'assets/js/site.js','../assets/js/site.js','../../assets/js/site.js'],(p,'unauthorized script')
assert len(pages)==12,len(pages)
areas=json.loads((ROOT/'content/areas.json').read_text())
assert hashlib.sha256((ROOT/'content/areas.json').read_bytes()).hexdigest() == 'b75f9befcbc67793abb17b8a657cb27205409cd02fbadedceba4adc242d9072c', 'Approved legal content changed'
items=0
for area in areas:
    file=DIST/'areas'/area['slug']/'index.html'
    text=' '.join(' '.join(pages[file].text).split())
    for group in area['groups']:
        assert group['title'] in text,(area['slug'],group['title'])
        for item in group['items']:
            assert item in text,(area['slug'],item)
            items+=1
    assert area['help'] in text,(area['slug'],'missing help')
assert items==123,items
assert sum(len(a['groups']) for a in areas)==26
files=list(DIST.rglob('*'))
assert not any(p.suffix in ['.md','.docx','.pdf','.json','.py','.png'] for p in files),'internal/source material in deploy output'
assert not any(p.name in ['ESCOPO-REUNIAO.md','escopo-reuniao.html','sitemap.xml'] for p in files)
assert not any('gtag(' in p.read_text() or 'fbq(' in p.read_text() or 'googletagmanager.com' in p.read_text() for p in DIST.rglob('*.html'))
themed=list((DIST/'assets/images').glob('area-*.webp'))
assert len(themed)==15, len(themed)
assert max(p.stat().st_size for p in themed)<=160000, 'Thematic image budget exceeded'
print(json.dumps({'status':'PASS','html_pages':len(pages),'legal_areas':len(areas),'legal_groups':26,'legal_activities':items,'links_assets_anchors':'PASS','preview_indexing':'noindex,nofollow','deploy_surface':'allowlist; no internal documents'},ensure_ascii=False,indent=2))
