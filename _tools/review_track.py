"""LocalLift lead tracking standard (Nov 24 2026) for the review/<prop> pages. Idempotent.
Keeps review_link_open exactly as it was, and adds one review_google_open event when Google actually opens:
  review_google_open {property, staff, src, moment, method: tap|auto}
property uses the LocalLift Live slug (montage, stillwater, lura, fora, coya), the same as lead_action and app_action.
No resident names or details are sent. transport_type beacon so the event survives the jump to Google.
Usage: python3 _tools/review_track.py"""
import os,re
R=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
SLUG={'montage':'montage','stillwater-lakes':'stillwater','lura':'lura','fora':'fora','coya':'coya'}
JS=("function rg(m){try{gtag('event','review_google_open',{property:'__P__',staff:cl(q.get('by')),src:cl(q.get('src'))||'text',"
    "moment:cl(q.get('m')),method:m,transport_type:'beacon'})}catch(e){}}/*llrg*/")
for d,sl in SLUG.items():
    p=os.path.join(R,'review',d,'index.html');s=open(p).read();n0=s
    s=re.sub(r"function rg\(m\)\{.*?\}/\*llrg\*/\n?","",s)
    js=JS.replace('__P__',sl)
    old="function go(){if(!done){done=true;location.replace(G)}}"
    new="function go(){if(!done){done=true;rg('auto');setTimeout(function(){location.replace(G)},250)}}"
    s=s.replace(old,new)
    assert new in s,p
    # rg is defined after q and cl exist; function declarations hoist, q and cl are read only when rg runs
    s=s.replace("if(!bot){gtag('event','review_link_open'",js+"\nif(!bot){gtag('event','review_link_open'",1) if '/*llrg*/' not in s else s
    s=s.replace('onclick="done=true"','onclick="if(!done&&!bot)rg(\'tap\');done=true"')
    assert s.count('/*llrg*/')==1 and "rg('tap')" in s,p
    if s!=n0: open(p,'w').write(s)
    print(d,'changed' if s!=n0 else 'unchanged')
