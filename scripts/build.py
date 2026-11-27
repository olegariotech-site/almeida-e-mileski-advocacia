#!/usr/bin/env python3
"""Generate a portable, JS-independent static preview. No network or runtime deps."""
from pathlib import Path
from html import escape
from urllib.parse import quote
import argparse
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
AREAS = json.loads((ROOT / 'content/areas.json').read_text())
NAME = 'Almeida e Mileski Advocacia'
PHONE = '5519996837596'  # Existing V0.3 contact; final institutional validation pending.
WA = f'https://wa.me/{PHONE}?text=' + quote('Olá! Vim pelo site Almeida e Mileski Advocacia e gostaria de solicitar um atendimento.')
MAPS = 'https://www.google.com/maps/search/?api=1&query=' + quote('Rua Paulo Setúbal, 302, Vila Angeli, Valinhos - SP')

def icon(kind='arrow', cls=''):
    paths = {
        'arrow': '<path d="M5 12h14m-6-6 6 6-6 6"/>',
        'down': '<path d="m6 9 6 6 6-6"/>',
        'plus': '<path d="M12 5v14M5 12h14"/>',
        'menu': '<path d="M4 7h16M4 12h16M4 17h16"/>',
        'home': '<path d="m3 10 9-7 9 7v10H3Zm6 10v-7h6v7"/>',
        'family': '<circle cx="8" cy="7" r="3"/><circle cx="17" cy="8" r="2.5"/><path d="M2 21v-3a6 6 0 0 1 12 0v3m1-8a5 5 0 0 1 7 5v3"/>',
        'bank': '<path d="m3 8 9-5 9 5H3Zm2 3v7m7-7v7m7-7v7M3 21h18"/>',
        'consumer': '<path d="M5 7h14l1 14H4L5 7Zm4 0V5a3 3 0 0 1 6 0v2"/>',
        'pension': '<path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3Z"/><path d="m8 12 3 3 5-6"/>',
    }
    if kind == 'whatsapp':
        return '<svg class="wa-icon" viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><path d="M20.5 3.5A11.8 11.8 0 0 0 12 0 11.9 11.9 0 0 0 1.7 17.9L0 24l6.3-1.7A11.9 11.9 0 0 0 24 12a11.8 11.8 0 0 0-3.5-8.5ZM12 21.9a9.8 9.8 0 0 1-5-1.4l-.4-.2-3.7 1 1-3.7-.2-.4A9.9 9.9 0 1 1 12 21.9Zm5.4-7.5-2-.9c-.3-.1-.5-.2-.7.1l-.9 1.2c-.2.2-.4.2-.7.1a8.1 8.1 0 0 1-4-3.5c-.2-.3 0-.5.1-.6l.5-.5.3-.5c.1-.2 0-.4 0-.5l-.9-2.2c-.3-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4S7 8 7 9.4s1.1 2.9 1.2 3.1a11.2 11.2 0 0 0 5.1 4.5l1.7.6a4 4 0 0 0 1.9.1c.6-.1 1.8-.7 2-1.4s.2-1.3.2-1.4c-.1-.1-.3-.2-.6-.4Z"/></svg>'
    return f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths[kind]}</svg>'

def internal(path, label, prefix='', cls='', current=False):
    return f'<a data-internal href="{prefix}{path}"' + (f' class="{cls}"' if cls else '') + (' aria-current="page"' if current else '') + f'>{label}</a>'

def whatsapp(label='Contato pelo WhatsApp', cls='btn whatsapp'):
    return f'<a class="{cls}" href="{escape(WA)}" target="_blank" rel="noopener noreferrer" aria-label="{escape(label)} — (19) 99683-7596, abre em nova aba">{icon("whatsapp")}<span>{label}</span></a>'

def controls(id):
    return f'<div class="accordion-tools" hidden><button type="button" data-expand="true" aria-controls="{id}">Expandir todas</button><button type="button" data-expand="false" aria-controls="{id}">Recolher todas</button></div><span class="sr-only" role="status" aria-live="polite"></span>'

def accordion(prefix=''):
    rows = []
    for i, area in enumerate(AREAS):
        groups = ''.join(f'<li>{escape(g["title"])}</li>' for g in area['groups'])
        rows.append(f'''<details class="signature" id="area-{i+1}"><summary><span class="number">0{i+1}</span>{icon(['home','family','bank','consumer','pension'][i], 'area-icon')}<span class="summary-title">{escape(area['title'])}<span class="summary-description">{escape(area['description'])}</span></span><span class="plus">{icon('plus')}</span></summary><div class="signature-body"><p>{escape(area['intro'])}</p><ul class="group-overview">{groups}</ul><span class="attribution">Atuação: {escape(area['professional'])}.</span>{internal('areas/'+area['slug']+'/', 'Conhecer a área completa '+icon(), prefix, 'text-link')}</div></details>''')
    return f'<div data-accordion-group>{controls("areas-list")}<div class="signature-list" id="areas-list">{"".join(rows)}</div></div>'

def photo(prefix='', hero=False):
    if hero:
        return f'''<figure><div class="hero-photo"><img src="{prefix}assets/images/socias-1200.webp" srcset="{prefix}assets/images/socias-480.webp 480w, {prefix}assets/images/socias-768.webp 768w, {prefix}assets/images/socias-1200.webp 1200w" sizes="(max-width: 900px) 90vw, 46vw" width="1200" height="800" alt="Composição de apresentação das duas advogadas no escritório" fetchpriority="high" decoding="async"></div><figcaption>Composição digital de apresentação, sujeita à aprovação.</figcaption></figure>'''
    return ''

def partners(prefix='', full=False):
    bios = [
        ('cintia', 'Cíntia Pereira Almeida Gomes', 'OAB/SP 541.172',
         'Cíntia Pereira Almeida Gomes é advogada, com experiência nas áreas jurídica, contratual e de gestão. Sua trajetória profissional reúne vivência prática em análise e gestão de contratos, relações imobiliárias e condução de demandas extrajudiciais.',
         'Atualmente, está em formação de pós-graduação pela EBRADI em Direito de Família e Sucessões, Direito Imobiliário e Direito Civil. É membro do IBDFAM — Instituto Brasileiro de Direito de Família.',
         'Família e Sucessões · Imobiliário e Condominial · Bancário',
         'Sua atuação é orientada pelo conhecimento técnico, pela escuta atenta e pela análise individualizada de cada situação, buscando oferecer orientação clara, acolhimento e segurança jurídica aos clientes.'),
        ('mileski', 'Sócia Mileski', 'OAB/PR 59.635 · OAB/SP 452.260 (suplementar)',
         'Advogada, com pós-graduação em Direito do Consumidor. Desenvolve sua atuação com dedicação à orientação jurídica e à defesa dos direitos e interesses de seus clientes.',
         'Atua nas áreas de Direito Bancário, Direito do Consumidor e Direito Previdenciário, com análise criteriosa de cada demanda e busca por soluções jurídicas adequadas às necessidades apresentadas.',
         'Bancário · Consumidor · Previdenciário e Assistencial',
         'Sua prática profissional é pautada pela ética, responsabilidade, atualização jurídica e atendimento próximo, com o compromisso de proporcionar clareza e segurança ao longo do acompanhamento jurídico.'),
    ]
    cards=[]
    for stem, name, oab, intro, education, areas, closing in bios:
        heading='h2' if full else 'h3'
        extra=f'<p>{education}</p><p>{closing}</p>' if full else '<p>'+ ('Pós-graduações em andamento pela EBRADI. Membro do IBDFAM.' if stem=='cintia' else 'Atendimento pautado pela ética e pela responsabilidade.')+'</p>'
        cards.append(f'''<article class="partner reveal"><div class="portrait"><img src="{prefix}assets/images/{stem}-800.webp" srcset="{prefix}assets/images/{stem}-480.webp 480w, {prefix}assets/images/{stem}-672.webp 672w, {prefix}assets/images/{stem}-800.webp 800w" sizes="(max-width: 560px) 90vw, 43vw" alt="Retrato de {name}" width="800" height="1067" loading="{'eager' if full else 'lazy'}" {'fetchpriority="high"' if full and stem=='cintia' else ''} decoding="async"></div><div class="profile-copy"><{heading}>{name}</{heading}><div class="oab">Advogada · {oab}</div><span class="profile-label">Trajetória profissional</span><p>{intro}</p>{extra}<span class="partner-area">{areas}</span></div></article>''')
    return '<div class="partners-grid">'+''.join(cards)+'</div>'

def values():
    return '<div class="values reveal">'+''.join(f'<div class="value"><h3>{title}</h3><p>{copy}</p></div>' for title,copy in [('Escuta','Compreender o contexto e as particularidades de cada demanda.'),('Estratégia','Análise criteriosa dos fatos, dos documentos e dos caminhos possíveis.'),('Proximidade','Orientação clara e acompanhamento responsável de cada caso.')])+'</div>'

def contact(prefix='', compact=False):
    return f'''<section class="section dark" id="contato"><div class="wrap contact-grid"><div class="reveal"><span class="kicker">Contato institucional</span><h2>O primeiro passo é compreender sua necessidade.</h2><p>Entre em contato para solicitar uma análise jurídica da sua situação. A orientação depende da avaliação individual dos fatos e documentos apresentados.</p><div class="actions">{whatsapp()}</div><p class="fine" style="margin-top:22px">O atendimento é realizado diretamente pelas profissionais.</p></div><dl class="contact-data reveal"><div><dt>WhatsApp</dt><dd><a href="{escape(WA)}" target="_blank" rel="noopener noreferrer">(19) 99683-7596 <span class="sr-only">(abre em nova aba)</span></a></dd></div><div><dt>Endereço de atendimento</dt><dd>Rua Paulo Setúbal, 302 · Sala 03<br>Espaço Lacarzi · Vila Angeli · Valinhos/SP</dd></div><div><dt>Localização</dt><dd><a href="{escape(MAPS)}" target="_blank" rel="noopener noreferrer">Ver endereço no Google Maps <span class="sr-only">(abre em nova aba)</span></a></dd></div><div><dt>Informações sobre privacidade</dt><dd>{internal('politica-de-privacidade/', 'Conhecer a política desta prévia', prefix)}</dd></div></dl></div></section>'''

def page_intro(title, desc, prefix, section=''):
    bread=internal('', 'Início', prefix)
    if section: bread+=f'<span aria-hidden="true">/</span><span>{section}</span>'
    return f'<section class="page-intro"><div class="wrap"><nav class="breadcrumb" aria-label="Caminho da página">{bread}</nav><h1>{title}</h1><p class="lead">{desc}</p></div></section>'

def shell(title, description, body, route='', depth=0):
    prefix='../'*depth
    nav=internal('o-escritorio/','O escritório',prefix,current=route=='o-escritorio')
    nav+=internal('as-advogadas/','As advogadas',prefix,current=route=='as-advogadas')
    dropdown=''.join(internal('areas/'+a['slug']+'/',escape(a['title']),prefix,current=route==a['slug']) for a in AREAS)
    nav+=f'<details class="nav-disclosure"><summary>Áreas de atuação {icon("down")}</summary><div class="nav-dropdown">{dropdown}</div></details>'
    nav+=internal('conteudos/','Conteúdos',prefix,current=route=='conteudos')
    nav+=internal('contato/','Contato',prefix,current=route=='contato')
    footlinks=''.join(internal(path,label,prefix) for path,label in [('o-escritorio/','O escritório'),('as-advogadas/','As advogadas'),('conteudos/','Conteúdos e orientações'),('contato/','Contato'),('politica-de-privacidade/','Privacidade')])
    schema=json.dumps({'@context':'https://schema.org','@type':'WebPage','name':title+' | '+NAME,'description':description,'inLanguage':'pt-BR'},ensure_ascii=False)
    return f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="#201e1e"><meta name="description" content="{escape(description)}"><meta name="referrer" content="strict-origin-when-cross-origin"><title>{escape(title)} | {NAME}</title><link rel="icon" type="image/webp" href="{prefix}assets/monograma-oficial.webp"><link rel="preload" href="{prefix}assets/fonts/bodoni-moda-latin.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="{prefix}assets/css/site.css"><script src="{prefix}assets/js/site.js" defer></script><script type="application/ld+json">{schema}</script></head><body id="topo"><a class="skip" href="#principal">Ir para o conteúdo</a><div class="progress" aria-hidden="true"></div><p class="preview">Prévia institucional · Conteúdo sujeito à aprovação das profissionais</p><header class="site-header"><div class="wrap header-inner">{internal('', f'<img src="{prefix}assets/marca-oficial.webp" alt="Almeida e Mileski Advocacia — início" width="219" height="90">',prefix,'brand',current=route=='')}<nav class="nav desktop-nav" id="main-nav" aria-label="Navegação principal">{nav}</nav><details class="mobile-menu" id="mobile-menu"><summary class="menu-toggle" id="menu-toggle" aria-label="Abrir menu" aria-controls="mobile-nav">{icon('menu')}</summary><nav class="nav" id="mobile-nav" aria-label="Navegação principal no celular">{nav}</nav></details></div></header><main id="principal" tabindex="-1">{body}</main>{footer(prefix)}<a class="wa-float" href="{escape(WA)}" target="_blank" rel="noopener noreferrer" aria-label="Contato no WhatsApp — abre em nova aba">{icon('whatsapp')}</a></body></html>'''

AREA_VISUALS = {
 'direito-imobiliario-e-condominial': ('imobiliario', 'Arquitetura contemporânea, luz natural e patrimônio'),
 'direito-de-familia-e-sucessoes': ('familia', 'Encontro entre gerações em um ambiente acolhedor'),
 'direito-bancario': ('bancario', 'Documentos sem dados pessoais organizados sobre uma mesa'),
 'direito-do-consumidor': ('consumidor', 'Uma entrega cuidadosa em uma relação de comércio'),
 'direito-previdenciario-e-assistencial': ('previdenciario', 'Pessoas maduras caminhando com autonomia em um jardim'),
}

def area_photo(area, prefix='', eager=True):
    stem,alt = AREA_VISUALS[area['slug']]
    return f'''<figure class="area-figure"><div class="area-photo"><img src="{prefix}assets/images/area-{stem}-768.webp" srcset="{prefix}assets/images/area-{stem}-400.webp 400w, {prefix}assets/images/area-{stem}-768.webp 768w, {prefix}assets/images/area-{stem}-1200.webp 1200w" sizes="(max-width: 900px) 90vw, 46vw" width="1200" height="800" alt="{alt}" loading="{'eager' if eager else 'lazy'}" {'fetchpriority="high"' if eager else ''} decoding="async"></div><figcaption>Imagem ilustrativa gerada por IA. Pessoas e cenários fictícios.</figcaption></figure>'''

def area_intro(area, prefix):
    return f'''<section class="practice-hero dark"><div class="wrap"><nav class="breadcrumb" aria-label="Caminho da página">{internal('', 'Início', prefix)}<span aria-hidden="true">/</span>{internal('#areas', 'Áreas de atuação', prefix)}<span aria-hidden="true">/</span><span aria-current="page">{escape(area['title'])}</span></nav><div class="practice-hero-grid"><div class="practice-copy"><span class="kicker">Áreas de atuação · 0{AREAS.index(area)+1}</span><h1>{escape(area['title'])}</h1><p class="lead">{escape(area['description'])}</p><span class="practice-attribution">Atuação: {escape(area['professional'])}.</span><a class="text-link" href="#possibilidades">Explorar os temas {icon('down')}</a></div>{area_photo(area,prefix)}</div></div></section>'''

def footer(prefix):
    nav=''.join(internal(path,label,prefix) for path,label in [('o-escritorio/','O escritório'),('as-advogadas/','As advogadas'),('conteudos/','Conteúdos e orientações'),('contato/','Contato'),('politica-de-privacidade/','Privacidade')])
    areas=''.join(internal('areas/'+a['slug']+'/',escape(a['title']),prefix) for a in AREAS)
    return f'''<footer class="footer"><div class="wrap"><div class="footer-grid"><div class="footer-brand"><img src="{prefix}assets/monograma-oficial.webp" alt="Monograma CK" width="64" height="64" loading="lazy"><strong>{NAME}</strong><p>Direito com estratégia,<br>compromisso e proximidade.</p></div><div><h2>O escritório</h2><nav aria-label="Navegação do rodapé">{nav}<a href="#topo">Voltar ao início da página</a></nav></div><div><h2>Áreas de atuação</h2><nav aria-label="Áreas jurídicas no rodapé">{areas}</nav></div><div><h2>Contato institucional</h2><a class="footer-contact" href="{escape(WA)}" target="_blank" rel="noopener noreferrer">(19) 99683-7596<span class="sr-only"> (abre em nova aba)</span></a><p>Rua Paulo Setúbal, 302 · Sala 03<br>Espaço Lacarzi · Vila Angeli<br>Valinhos/SP</p><a class="footer-contact" href="{escape(MAPS)}" target="_blank" rel="noopener noreferrer">Ver localização<span class="sr-only"> (abre em nova aba)</span></a></div></div><div class="footer-registers"><p>Cíntia Pereira Almeida Gomes · OAB/SP 541.172</p><p>Sócia Mileski · OAB/PR 59.635 · OAB/SP 452.260 (suplementar)</p></div><div class="footer-legal"><p>Informações institucionais sujeitas à revisão. Cada situação exige análise individualizada. Este conteúdo não constitui orientação jurídica específica ou promessa de resultado.</p><p>Projeto e desenvolvimento · <a href="https://olegariotech.com.br/" target="_blank" rel="noopener noreferrer">OLEGARIO TECH<span class="sr-only"> (abre em nova aba)</span></a></p></div></div></footer>'''


def pages(base_path="/almeida-e-mileski-advocacia/"):
    result={}
    home=f'''<section class="hero dark"><div class="wrap"><div class="hero-grid"><div class="hero-copy"><span class="kicker">Almeida e Mileski · Advocacia</span><h1>O Direito exige conhecimento. <em>A confiança exige proximidade.</em></h1><p class="lead">Orientação jurídica com estratégia, responsabilidade e proximidade, em questões imobiliárias, familiares, bancárias, consumeristas e previdenciárias.</p><div class="actions">{whatsapp('Falar pelo WhatsApp')}<a class="btn" href="#areas">Nossas áreas {icon('down')}</a></div></div>{photo(hero=True)}</div><div class="hero-bottom"><span>Direito com estratégia, compromisso e proximidade.</span><a href="#escritorio">Conheça o escritório {icon('down')}</a></div></div></section>
<section class="section" id="escritorio"><div class="wrap"><div class="intro-grid reveal"><div><span class="kicker">O escritório</span><h2>Cada decisão jurídica envolve pessoas, histórias e patrimônios.</h2></div><div><p>A Almeida e Mileski Advocacia atua com compromisso ético, responsabilidade e atenção às particularidades de cada cliente.</p><p>Nossa proposta é oferecer orientação jurídica clara e atendimento próximo, construindo estratégias adequadas à realidade de cada demanda.</p>{internal('o-escritorio/','Conheça nossa forma de atuar '+icon(),cls='text-link')}</div></div>{values()}</div></section>
<section class="section areas-section" id="areas"><div class="wrap"><div class="section-heading reveal"><div><span class="kicker">Áreas de atuação</span><h2>Orientação para os diferentes momentos da vida.</h2></div><p>Explore cada área e conheça as possibilidades de atuação, sempre sujeitas à análise individual dos fatos e documentos.</p></div>{accordion()}</div></section>
<section class="section" id="socias"><div class="wrap"><div class="partners-intro reveal"><span class="kicker">As advogadas</span><h2>Duas trajetórias.<br>Um compromisso em comum.</h2><p class="lead">Ética, responsabilidade e atenção às particularidades de cada pessoa.</p></div>{partners()}<div class="actions">{internal('as-advogadas/','Conheça as trajetórias completas '+icon(),cls='text-link')}</div></div></section>
<section class="section dark"><div class="wrap approach-grid"><div class="reveal"><span class="kicker">Forma de atuação</span><h2>Clareza em cada etapa. Respeito em cada decisão.</h2><p>Escuta atenta, análise individualizada e comunicação transparente para esclarecer os caminhos jurídicos possíveis.</p></div><ol class="steps reveal"><li><span class="number">01</span><div><strong>Primeiro contato</strong><p>Compreender o contexto e a necessidade de orientação.</p></div></li><li><span class="number">02</span><div><strong>Análise da situação</strong><p>Avaliar os fatos e os documentos pertinentes.</p></div></li><li><span class="number">03</span><div><strong>Orientação jurídica</strong><p>Esclarecer direitos, deveres e alternativas adequadas ao caso.</p></div></li><li><span class="number">04</span><div><strong>Acompanhamento responsável</strong><p>Comunicação clara ao longo do atendimento profissional.</p></div></li></ol></div></section>
<section class="section"><div class="wrap"><div class="section-heading reveal"><div><span class="kicker">Conteúdos e orientações</span><h2>Informação para compreender seus direitos.</h2></div><p>Conheça os temas abordados pelo escritório e encontre informações institucionais sobre cada área.</p></div><div class="editorial-entry">{internal("conteudos/", "Explorar conteúdos e orientações "+icon(), cls="text-link")}</div></div></section>{contact()}'''
    result['index.html']=shell('Início','Orientação jurídica com estratégia, compromisso e proximidade. Conheça as advogadas e as cinco áreas de atuação do escritório.',home)
    pref='../'
    about=page_intro('Direito com estratégia, compromisso e proximidade.','Orientação clara, atendimento próximo e atenção às particularidades de cada cliente.',pref,'O escritório')
    about+=f'''<section class="section"><div class="wrap"><div class="intro-grid"><div><h2>Um caminho jurídico mais claro para cada pessoa.</h2>{photo(pref,True)}</div><div class="prose"><p>A Almeida e Mileski Advocacia atua com compromisso ético, responsabilidade e atenção às particularidades de cada cliente. Nossa proposta é oferecer orientação jurídica clara e atendimento próximo, construindo estratégias adequadas à realidade de cada demanda.</p><p>Reunimos diferentes áreas do Direito para oferecer suporte jurídico tanto na prevenção de conflitos quanto na defesa de direitos e interesses. Trabalhamos com análise individualizada, transparência na comunicação e acompanhamento responsável de cada caso.</p><p>Nosso propósito é tornar o caminho jurídico mais claro para cada pessoa, com escuta atenta, estratégia e compromisso com a proteção de seus direitos.</p>{internal('as-advogadas/','Conheça as advogadas '+icon(),pref,'text-link')}</div></div>{values()}</div></section>{contact(pref)}'''
    result['o-escritorio/index.html']=shell('O escritório','Conheça a proposta institucional, os valores e a forma de atuação da Almeida e Mileski Advocacia.',about,'o-escritorio',1)
    team=page_intro('As advogadas','Trajetórias profissionais apresentadas com clareza, responsabilidade e compromisso com a orientação jurídica.',pref,'As advogadas')
    team+=f'<section class="section"><div class="wrap">{partners(pref,True)}</div></section>{contact(pref)}'
    result['as-advogadas/index.html']=shell('As advogadas','Conheça Cíntia Pereira Almeida Gomes e a sócia Mileski, seus registros profissionais e suas áreas de atuação.',team,'as-advogadas',1)
    for area in AREAS:
        prefix='../../'
        intro=area_intro(area,prefix)
        toc=''.join(f'<a href="#tema-{i+1}">{escape(g["title"])}</a>' for i,g in enumerate(area['groups']))
        groups=[]
        for i,g in enumerate(area['groups']):
            lis=''.join(f'<li>{escape(item)}</li>' for item in g['items'])
            groups.append(f'<details class="signature" id="tema-{i+1}"><summary><span class="number">0{i+1}</span><span class="summary-title">{escape(g["title"])}</span><span class="plus">{icon("plus")}</span></summary><div class="signature-body"><ul>{lis}</ul></div></details>')
        related=''.join(internal('areas/'+a['slug']+'/',escape(a['title']),prefix) for a in AREAS if a!=area)
        body=intro+f'''<section class="section"><div class="wrap legal-layout"><aside class="context-nav"><h2>Nesta área</h2><nav aria-label="Tópicos de {escape(area['title'])}">{toc}<a href="#orientacao">Como podemos ajudar</a></nav><span class="attribution">Atuação: {escape(area['professional'])}.</span>{internal('as-advogadas/','Conheça as profissionais '+icon(),prefix,'text-link')}</aside><div class="legal-content"><p class="lead">{escape(area['intro'])}</p><h2 id="possibilidades">Possibilidades de atuação</h2><div data-accordion-group>{controls('topics-list')}<div class="signature-list" id="topics-list">{''.join(groups)}</div></div><section class="help" id="orientacao"><h2>Como podemos ajudar</h2><p>{escape(area['help'])}</p></section><aside class="related"><h2>Outras áreas de atuação</h2>{related}</aside></div></div></section>{contact(prefix)}'''
        result['areas/'+area['slug']+'/index.html']=shell(area['title'],area['description']+' Conheça os temas e as possibilidades de orientação jurídica.',body,area['slug'],2)
    content=page_intro('Conteúdos e orientações','Informações institucionais organizadas por tema para facilitar a compreensão das possibilidades de atuação.',pref,'Conteúdos')
    content+=f'<section class="section"><div class="wrap"><p class="lead narrow">As páginas a seguir apresentam os assuntos abordados pelo escritório. A orientação aplicável depende sempre da análise individualizada da situação e dos documentos.</p>{editorial_list(pref, 2)}</div></section>{contact(pref)}'
    result['conteudos/index.html']=shell('Conteúdos e orientações','Explore os temas de Imobiliário, Família, Bancário, Consumidor e Previdenciário e Assistencial.',content,'conteudos',1)
    contactbody=page_intro('Contato','Canais institucionais para solicitar informações sobre o atendimento jurídico.',pref,'Contato')+contact(pref)
    result['contato/index.html']=shell('Contato','Fale pelo WhatsApp e consulte o endereço de atendimento do escritório em Valinhos/SP.',contactbody,'contato',1)
    privacy=page_intro('Política de Privacidade','Informações sobre as funcionalidades efetivamente utilizadas nesta prévia institucional.',pref,'Privacidade')
    privacy+=f'''<section class="section"><div class="wrap narrow prose"><p class="fine">Versão para revisão pelas profissionais · 26 de novembro de 2026.</p><h2>1. Escopo desta prévia</h2><p>Esta página descreve o funcionamento da prévia institucional de Almeida e Mileski Advocacia. A identificação definitiva da sociedade responsável e dos seus canais de privacidade deve ser aprovada antes da publicação institucional.</p><h2>2. Navegação e infraestrutura</h2><p>O site apresenta conteúdo estático e não possui cadastro, formulário de contato, área de cliente ou envio de documentos. O provedor que vier a hospedar a versão publicada poderá tratar dados técnicos de conexão, como endereço IP e informações do navegador, conforme sua configuração e política. O provedor e os respectivos prazos de retenção deverão ser informados na versão final.</p><h2>3. Cookies, fontes e medição</h2><p>Esta versão não instala cookies, não utiliza armazenamento local e não carrega ferramentas de análise de audiência ou publicidade. As fontes e imagens são servidas junto com o site. Qualquer implantação futura de medição ou recursos opcionais exige revisão desta política e definição dos mecanismos de consentimento aplicáveis antes da ativação.</p><h2>4. Parâmetros de navegação</h2><p>Quando um link de entrada contém parâmetros de campanha UTM, esses parâmetros podem acompanhar a navegação entre páginas do próprio site, somente na URL. O site não os armazena em cookies, não os registra por conta própria e não os acrescenta aos links externos de contato.</p><h2>5. WhatsApp e serviços externos</h2><p>O contato pelo WhatsApp e a consulta de localização no Google Maps dependem de ação voluntária. Esses links abrem serviços externos, sujeitos às políticas de seus respectivos responsáveis. O site não envia automaticamente informações do visitante para esses serviços. A mensagem inicial do WhatsApp é um texto institucional fixo e não contém dados inseridos pelo visitante.</p><h2>6. Atendimento e informações pessoais</h2><p>A finalidade, as bases legais, a necessidade, a segurança e os prazos de retenção dos dados utilizados durante eventual atendimento jurídico deverão ser esclarecidos pelas profissionais no canal de atendimento. Evite enviar documentos pessoais, dados financeiros, de saúde ou outras informações sensíveis antes de receber orientação sobre o meio adequado.</p><h2>7. Solicitações e direitos</h2><p>Para esclarecer o tratamento de informações durante o atendimento ou apresentar uma solicitação relacionada aos seus dados pessoais, utilize o canal institucional de contato. O exercício dos direitos previstos na legislação depende da identificação do tratamento realizado, da verificação de identidade quando necessária e das obrigações legais aplicáveis.</p>{internal('contato/','Acessar o canal institucional '+icon(),pref,'text-link')}<h2>8. Atualizações</h2><p>Esta política deve ser revista antes da publicação e sempre que novas funcionalidades, fornecedores, formas de coleta ou finalidades de tratamento forem introduzidos.</p></div></section>'''
    result['politica-de-privacidade/index.html']=shell('Política de Privacidade','Entenda como esta prévia funciona: sem cookies opcionais, rastreadores ou formulários de coleta de dados.',privacy,'politica-de-privacidade',1)
    # A standalone 404 deliberately avoids relative assets, which fail at arbitrary depths.
    result['404.html']='''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="description" content="Página não encontrada. Retorne ao início da Almeida e Mileski Advocacia."><title>Página não encontrada | Almeida e Mileski Advocacia</title><style>body{margin:0;background:#201e1e;color:#f6f6f6;font:18px/1.7 Georgia,serif;min-height:100vh;display:grid;place-items:center}main{max-width:650px;padding:35px}span{color:#c9a66e;font-size:85px}h1{font-weight:400;font-size:40px}a{color:#c9a66e;display:inline-block;padding:15px 0}a:focus-visible{outline:3px solid #c9a66e;outline-offset:5px}</style></head><body><main><span>404</span><h1>Este caminho não foi encontrado.</h1><p>Você pode voltar ao início para conhecer o escritório e suas áreas de atuação.</p><a id="home-link" href="__BASE_PATH__">Ir para a página inicial</a><script>if(!location.pathname.startsWith('/almeida-e-mileski-advocacia/'))document.getElementById('home-link').href='/';</script></main></body></html>'''
    result['404.html']=result['404.html'].replace('__BASE_PATH__',escape(base_path,quote=True))
    return result

def editorial_list(prefix='', level=3):
    return '<div class="editorial-list">'+''.join(f'<a data-internal class="editorial-item" href="{prefix}areas/{a["slug"]}/"><span class="number">0{i+1}</span><div><h{level}>{escape(a["title"])}</h{level}><p>{escape(a["description"])}</p></div><span class="text-link">Explorar os temas {icon()}</span></a>' for i,a in enumerate(AREAS))+'</div>'

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=ROOT/'dist')
    parser.add_argument('--base-path',default='/almeida-e-mileski-advocacia/',help='Absolute deployment prefix used by the JavaScript-free 404 return link')
    args=parser.parse_args()
    if not args.base_path.startswith('/') or not args.base_path.endswith('/') or '..' in args.base_path or '?' in args.base_path or '#' in args.base_path:
        parser.error('base-path must be an absolute directory path without query or fragment')
    output=args.output.resolve()
    if output==ROOT:
        raise SystemExit('Use a separate output directory; source files must never be deployed.')
    output.mkdir(parents=True,exist_ok=True)
    generated=pages(args.base_path)
    for path,html in generated.items():
        dest=output/path
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(html,encoding='utf-8')
    # Allowlist: no internal documents, sources, original photos or review material.
    for source in (ROOT/'assets').rglob('*'):
        if not source.is_file(): continue
        relative=source.relative_to(ROOT/'assets')
        if relative.as_posix().startswith('images/') and not source.stem.rsplit('-',1)[-1].isdigit(): continue
        if source.suffix not in {'.css','.js','.woff2','.webp'} and source.name!='OFL.txt': continue
        target=output/'assets'/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
    (output/'.nojekyll').write_text('')
    # No robots disallow here: crawlers must be able to observe the noindex directive.
    print(json.dumps({'output':str(output),'pages':len(generated),'areas':len(AREAS)},ensure_ascii=False))

if __name__=='__main__': main()
