#!/usr/bin/env python3
"""Build MoveInLocal answer pages from _answers/<prop>.json, in each guide page's own design.
Usage: python3 _tools/answers_gen.py  (run from repo root). Folders starting with _ are not published by GitHub Pages."""
import html, json, os, re, glob, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://moveinlocal.com'
CHECKED = os.environ.get('ANS_DATE', datetime.date.today().isoformat())
NICE = datetime.date.fromisoformat(CHECKED).strftime('%b %-d, %Y')
e = html.escape

PROPS = {
  'coya':      dict(name='COYA', city='Las Vegas', guide='las-vegas/coya/roommate-2-bedroom'),
  'lura':      dict(name='Lura', city='Las Vegas', guide='las-vegas/lura/apartments-near-the-strip'),
  'fora':      dict(name='Fora', city='Las Vegas', guide='las-vegas/fora/roommate-2-bedroom'),
  'montage':   dict(name='Montage', city='Tigard', guide='tigard/montage/roommate-2-bedroom'),
  'stillwater':dict(name='Stillwater Lakes', city='Kissimmee', guide='kissimmee/stillwater-lakes/lakefront-apartments'),
  'village':   dict(name='Village of Chandler', city='Chandler', guide='chandler/village-of-chandler/townhome-style-apartments'),
}

EXTRA_CSS = '''
.ans-hero{min-height:440px}
.ans-hero h1{font-size:clamp(32px,4.8vw,54px)}
.crumbs{font-size:13px;color:rgba(255,255,255,.75);margin-bottom:6px}
.crumbs a{color:rgba(255,255,255,.85);text-decoration:none}
.art{max-width:760px}
.ansbox{background:var(--sand);border-left:4px solid var(--gold);padding:24px 26px;border-radius:16px;margin-bottom:38px}
.ansbox .eyebrow{color:var(--gold)}
.ansbox p{font-size:19px;line-height:1.6;margin-top:10px;color:var(--ink)}
.art h2{font-family:var(--serif);font-weight:500;font-size:clamp(24px,3vw,32px);line-height:1.2;margin:40px 0 12px}
.art p{font-size:17px;color:var(--ink2);margin-top:12px}
.art ul{margin:14px 0 0 20px}
.art li{font-size:17px;color:var(--ink2);margin-top:8px}
.art .note{font-size:13.5px;color:var(--muted);margin-top:34px;padding-top:18px;border-top:1px solid var(--line)}
.related{background:var(--sand)}
.qlist{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}
@media(max-width:760px){.qlist{grid-template-columns:1fr}}
.qlist a{display:block;background:var(--paper);border:1.5px solid var(--line);border-radius:16px;padding:20px 22px;text-decoration:none;color:var(--ink);transition:.2s}
.qlist a:hover{border-color:var(--gold)}
.qlist b{display:block;font-family:var(--serif);font-weight:600;font-size:18px;line-height:1.3}
.qlist span{display:block;font-size:14.5px;color:var(--muted);margin-top:8px}
.qlist .go{color:var(--gold);font-weight:600;font-size:13px;letter-spacing:.08em;text-transform:uppercase;margin-top:12px}
.final h2{max-width:780px;margin-left:auto;margin-right:auto}
'''

def grab(t, pat, flags=re.S):
    m = re.search(pat, t, flags)
    if not m: raise SystemExit('pattern not found: ' + pat[:60])
    return m

def build(key, data):
    P = PROPS[key]; g = P['guide']; gurl = f'/{g}/'
    t = open(f'{ROOT}/{g}/index.html').read()
    head_top = t[:t.index('<meta charset')]                     # Google tag
    icons = grab(t, r'(<link rel="icon".*?<meta name="theme-color"[^>]*>)').group(1)
    fonts = ''.join(re.findall(r'<link rel="preconnect"[^>]*>|<link href="https://fonts.googleapis.com[^>]*>', t))
    style = grab(t, r'<style>(.*?)</style>').group(1)
    brand = grab(t, r'(<div class="brand">.*?</div>)').group(1)
    tour = grab(t, r'data-track="tour_click" data-plan="nav" href="([^"]+)"').group(1)
    camp = re.search(r'utm_campaign=([a-z_]+)', tour).group(1)
    hero_bg = grab(t, r'<header class="hero">\s*<div class="photo[^>]*style="([^"]+)"').group(1)
    final_bg = grab(t, r'<section class="final">\s*<div class="photo[^>]*style="([^"]+)"').group(1)
    og_img = grab(t, r'<meta property="og:image" content="([^"]+)"').group(1)
    footer = grab(t, r'(<footer>.*?</footer>)').group(1)
    mobile = grab(t, r'(<div class="mobilebar">.*?</div>)').group(1)
    mobile = re.sub(r'<small[^>]*>.*?</small>', '', mobile)
    mobile = mobile.replace('flex-direction:column;gap:0;line-height:1.15', 'line-height:1.15')
    phone = re.search(r'href="tel:([^"]+)"', t).group(1)
    _d = re.sub(r'\D', '', phone)[-10:]; pdisp = f'{_d[:3]} {_d[3:6]} {_d[6:]}'
    tour_a = tour.replace('utm_content=tour', 'utm_content=answers_tour')
    hubp = f'/{g}/answers/'
    pages = data['pages']
    script = ('<script>window.dataLayer=window.dataLayer||[];'
              f'function track(ev,plan){{window.dataLayer.push({{event:ev,plan:plan,page:"{camp}_answers"}});if(window.gtag)gtag("event",ev,{{plan:plan||"",guide:"{camp}_answers"}});}}'
              'document.addEventListener("click",e=>{const a=e.target.closest("[data-track]");if(a)track(a.dataset.track,a.dataset.plan);});</script>')

    def nav():
        return (f'<nav><div class="wrap">{brand}<div class="navlinks"><a href="{gurl}">{e(P["name"])} guide</a>'
                f'<a href="{hubp}">All answers</a><a href="{gurl}#specials">Specials</a><a href="{gurl}#faq">FAQ</a></div>'
                f'<a class="btn btn-gold" data-track="tour_click" data-plan="answers_nav" href="{tour_a}">Book a tour</a></div></nav>')

    def final():
        return (f'<section class="final"><div class="photo has-img" role="img" aria-label="{e(P["name"])}" style="{final_bg}"></div><div class="wrap">'
                f'<div class="eyebrow">{e(P["name"])}, {e(P["city"])}</div><h2>See today\'s pricing and specials at {e(P["name"])}.</h2>'
                f'<p>Prices and specials change often. The {e(P["name"])} guide shows what we checked most recently, and the leasing team can confirm today\'s numbers.</p>'
                f'<div class="ctas"><a class="btn btn-gold" data-track="guide_click" data-plan="answers_final" href="{gurl}">Open the {e(P["name"])} guide</a>'
                f'<a class="btn btn-light" data-track="tour_click" data-plan="answers_final" href="{tour_a}">Book a tour</a></div></div></section>')

    def head(title, desc, canon, ld):
        return (f'<!DOCTYPE html>\n<html lang="en">\n<head>\n{head_top}<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n{icons}\n'
                f'<title>{e(title)}</title>\n<meta name="description" content="{e(desc)}">\n<meta name="robots" content="index,follow">\n<link rel="canonical" href="{canon}">\n'
                f'<meta property="og:type" content="article"><meta property="og:site_name" content="MoveInLocal"><meta property="og:title" content="{e(title)}">'
                f'<meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{canon}"><meta property="og:image" content="{og_img}">'
                f'<meta name="twitter:card" content="summary_large_image"><meta name="format-detection" content="telephone=no,address=no,email=no">\n{fonts}\n'
                + ''.join('<script type="application/ld+json">' + json.dumps(b, ensure_ascii=False) + '</script>' for b in ld)
                + f'\n<style>{style}{EXTRA_CSS}</style>\n</head>\n<body>\n')

    def tail():
        return f'\n{footer}\n{mobile}\n{script}\n</body>\n</html>\n'

    def crumbs_ld(extra):
        items = [('MoveInLocal', SITE + '/'), (f'{P["name"]} guide', SITE + gurl), (f'{P["name"]} answers', SITE + hubp)] + extra
        return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(items)]}

    urls = []
    for i, a in enumerate(pages):
        canon = f'{SITE}{hubp}{a["slug"]}/'
        body_txt = ' '.join([a['short']] + [' '.join(s.get('p', []) + s.get('bullets', [])) for s in a['sections']])
        ld = [{'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
                {'@type': 'Question', 'name': a['q'], 'acceptedAnswer': {'@type': 'Answer', 'text': a['short']}}]},
              crumbs_ld([(a['q'], canon)]),
              {'@context': 'https://schema.org', '@type': 'Article', 'headline': a['q'], 'description': a['desc'], 'datePublished': CHECKED, 'dateModified': CHECKED,
               'mainEntityOfPage': canon, 'image': og_img, 'author': {'@type': 'Organization', 'name': 'MoveInLocal by LocalLift', 'url': SITE + '/'},
               'publisher': {'@type': 'Organization', 'name': 'MoveInLocal', 'url': SITE + '/'}, 'about': {'@type': 'ApartmentComplex', 'name': P['name']}}]
        secs = ''
        for s in a['sections']:
            secs += f'<h2>{e(s["h"])}</h2>' + ''.join(f'<p>{e(p)}</p>' for p in s.get('p', []))
            if s.get('bullets'): secs += '<ul>' + ''.join(f'<li>{e(b)}</li>' for b in s['bullets']) + '</ul>'
        others = [pages[(i + k) % len(pages)] for k in range(1, 5)]
        rel = ''.join(f'<a href="{hubp}{o["slug"]}/"><b>{e(o["q"])}</b><span class="go">Read the answer</span></a>' for o in others)
        title = f'{a["q"]} | {P["name"]} {P["city"]}'
        if len(title) > 70: title = a['q']
        out = (head(title, a['desc'], canon, ld) + nav() +
               f'<header class="hero ans-hero"><div class="photo has-img" role="img" aria-label="{e(P["name"])}" style="{hero_bg}"></div><div class="wrap">'
               f'<div class="crumbs"><a href="{gurl}">{e(P["name"])} guide</a> &rsaquo; <a href="{hubp}">Answers</a></div>'
               f'<div class="eyebrow">{e(P["name"])}, {e(P["city"])}</div><h1>{e(a["q"])}</h1>'
               f'<div class="stamp">From the MoveInLocal guide to {e(P["name"])}. Checked {NICE}.</div></div></header>'
               f'<section><div class="wrap art"><div class="ansbox"><div class="eyebrow">Short answer</div><p>{e(a["short"])}</p></div>{secs}'
               f'<p class="note">Pricing, specials and availability change often. For today\'s numbers, see the <a href="{gurl}">{e(P["name"])} guide</a> or call the leasing team at <a data-track="call_tap" data-plan="answers_note" href="tel:{phone}">{pdisp}</a>.</p></div></section>'
               f'<section class="related"><div class="wrap"><div class="sec-head"><div class="eyebrow" style="color:var(--gold)">Keep reading</div><h2>More questions renters ask about {e(P["name"])}</h2></div>'
               f'<div class="qlist">{rel}</div><p style="margin-top:22px"><a class="btn btn-ghost" href="{hubp}">See all {len(pages)} answers</a></p></div></section>'
               + final() + tail())
        os.makedirs(f'{ROOT}{hubp}{a["slug"]}', exist_ok=True)
        open(f'{ROOT}{hubp}{a["slug"]}/index.html', 'w').write(out)
        urls.append(canon)

    # hub
    canon = SITE + hubp
    cards = ''.join(f'<a href="{hubp}{a["slug"]}/"><b>{e(a["q"])}</b><span>{e(a["short"])}</span><span class="go">Read the answer</span></a>' for a in pages)
    ld = [{'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': a['q'], 'acceptedAnswer': {'@type': 'Answer', 'text': a['short']}} for a in pages]},
          crumbs_ld([])]
    desc = f'Straight answers to the questions renters ask about {P["name"]} in {P["city"]}: the area, the apartments, pets, fees, leases and move in.'
    out = (head(f'{P["name"]} {P["city"]} questions renters ask | MoveInLocal', desc, canon, ld) + nav() +
           f'<header class="hero ans-hero"><div class="photo has-img" role="img" aria-label="{e(P["name"])}" style="{hero_bg}"></div><div class="wrap">'
           f'<div class="crumbs"><a href="{gurl}">{e(P["name"])} guide</a> &rsaquo; Answers</div>'
           f'<div class="eyebrow">{e(P["name"])}, {e(P["city"])}</div><h1>Questions renters ask about <em>{e(P["name"])}</em>.</h1>'
           f'<p class="lead">Straight answers about the area, the apartments and moving in. Checked {NICE}.</p></div></header>'
           f'<section class="related"><div class="wrap"><div class="qlist">{cards}</div></div></section>' + final() + tail())
    open(f'{ROOT}{hubp}index.html', 'w').write(out)
    urls.insert(0, canon)
    return urls

def link_guides(allpages):
    """Add an Answers link to each guide's nav and a short list under its FAQ (idempotent)."""
    for key, P in PROPS.items():
        if key not in allpages: continue
        f = f'{ROOT}/{P["guide"]}/index.html'; t = open(f).read(); hubp = f'/{P["guide"]}/answers/'
        t = re.sub(r'\s*<a href="[^"]*/answers/" class="ans-nav">Answers</a>', '', t)
        t = t.replace('<a href="#faq">FAQ</a>', f'<a href="#faq">FAQ</a>\n   <a href="{hubp}" class="ans-nav">Answers</a>', 1)
        t = re.sub(r'<!--answers-->.*?<!--/answers-->', '', t, flags=re.S)
        qcss = EXTRA_CSS[EXTRA_CSS.index('.related'):EXTRA_CSS.index('.final h2')]
        cards = ''.join(f'<a href="{hubp}{a["slug"]}/"><b>{e(a["q"])}</b><span class="go">Read the answer</span></a>' for a in allpages[key][:6])
        block = (f'<!--answers--><style>{qcss}</style><section class="related" id="answers"><div class="wrap"><div class="sec-head"><div class="eyebrow" style="color:var(--gold)">More answers</div>'
                 f'<h2>More questions renters ask about {e(P["name"])}</h2></div><div class="qlist">{cards}</div>'
                 f'<p style="margin-top:22px"><a class="btn btn-ghost" href="{hubp}">See all {len(allpages[key])} answers</a></p></div></section><!--/answers-->\n\n')
        t = t.replace('<section class="final">', block + '<section class="final">', 1)
        open(f, 'w').write(t)

if __name__ == '__main__':
    allurls, allpages = [], {}
    for f in sorted(glob.glob(f'{ROOT}/_answers/*.json')):
        d = json.load(open(f)); key = d['property']
        allpages[key] = d['pages']; allurls += build(key, d)
    link_guides(allpages)
    # home page: list each community's answers hub (idempotent)
    h = open(f'{ROOT}/index.html').read()
    h = re.sub(r'<!--answers-->.*?<!--/answers-->', '', h, flags=re.S)
    links = ''.join(f'<a class="c" href="/{PROPS[k]["guide"]}/answers/"><b>{e(PROPS[k]["name"])} questions</b><span>{len(v)} answers renters ask about {e(PROPS[k]["name"])} and {e(PROPS[k]["city"])}</span></a>' for k, v in allpages.items())
    h = h.replace('<p style="font-size:13px;margin-top:40px">', f'<!--answers--><h2 style="font-family:Montserrat,sans-serif;font-weight:500;font-size:28px;margin:56px 0 0">Questions renters ask</h2>{links}<!--/answers-->\n<p style="font-size:13px;margin-top:40px">', 1)
    open(f'{ROOT}/index.html', 'w').write(h)
    # sitemap: keep existing entries, add answers
    sm = open(f'{ROOT}/sitemap.xml').read()
    sm = re.sub(r'<url><loc>[^<]*/answers/[^<]*</loc>.*?</url>\n?', '', sm)
    add = ''.join(f'<url><loc>{u}</loc><lastmod>{CHECKED}</lastmod></url>\n' for u in allurls)
    sm = sm.replace('</urlset>', add + '</urlset>')
    open(f'{ROOT}/sitemap.xml', 'w').write(sm)
    open(f'{ROOT}/_answers/urls.txt', 'w').write('\n'.join(allurls) + '\n')
    print(len(allurls), 'urls')
