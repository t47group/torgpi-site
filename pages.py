"""Renders the marketing pages (home, services, about, etc.). Called by build.py."""
import os, html
from chrome import CFG, U, E, icon, head, header, footer, cta_band, ROOT
from content import SERVICES, AUDIENCES, AREAS, FAQ

PAGES = []  # paths written, for the sitemap


def write(path, doc):
    PAGES.append(path)
    out = os.path.join(ROOT, path.strip("/"), "index.html") if path != "/404.html" else os.path.join(ROOT, "404.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(doc)


def page(path, title, desc, body, active="", ld=None):
    write(path, head(title, desc, path, ld) + header(active) + body + footer(SERVICES))


def crumbs(*items):
    parts = ['<a href="/">Home</a>'] + [f'<a href="{h}">{E(n)}</a>' if h else E(n) for n, h in items]
    return '<div class="crumbs">' + " / ".join(parts) + "</div>"


def crumb_ld(*items):
    li = [{"@type": "ListItem", "position": 1, "name": "Home", "item": U + "/"}]
    for i, (n, h) in enumerate(items, 2):
        li.append({"@type": "ListItem", "position": i, "name": n, "item": U + h})
    return {"@type": "BreadcrumbList", "itemListElement": li}


def svc_card(s):
    return f"""<a class="card" href="/services/{s['slug']}/"><div class="ib">{icon(s['icon'])}</div>
<h3>{E(s['name'])}</h3><p>{E(s['short'])}</p><span class="more">Learn more {icon('arrow',16)}</span></a>"""


def post_cards(posts, n=3):
    if not posts:
        return ""
    cards = "".join(f"""<a class="post-card" href="/blog/{p['slug']}/"><div class="d">{p['date'].strftime('%B %-d, %Y')} · {p['readtime']} min read</div>
<h3>{E(p['title'])}</h3><p>{E(p['description'])}</p><span class="more">Read article →</span></a>""" for p in posts[:n])
    return f"""<section class="alt"><div class="container">
<div class="sh"><span class="kicker">Insights</span><h2>Straight answers from a licensed investigator.</h2></div>
<div class="grid g3">{cards}</div>
<p style="margin-top:28px"><a class="btn ghost" href="/blog/">All articles {icon('arrow',18)}</a></p>
</div></section>"""


def faq_html(items):
    return "".join(f"<details><summary>{E(q)}</summary><div class=a>{''.join(f'<p>{E(p)}</p>' for p in a)}</div></details>" for q, a in items)


def faq_ld(items):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": " ".join(a)}} for q, a in items]}


# ------------------------------------------------------------------ home
def home(posts):
    trust = [("shield", "Licensed by Arizona DPS", f"Agency #{CFG['agency_license']}"),
             ("star", "Veteran-Led", "U.S. Air Force veteran founder"),
             ("lock", "100% Confidential", "Discreet from first call to final report"),
             ("doc", "Documented Results", "Time-stamped photo, video & reports")]
    trust_html = "".join(f"<div>{icon(i,26)}<span><b>{a}</b>{b}</span></div>" for i, a, b in trust)
    aud = "".join(f"""<div class="card"><div class="ib">{icon(ic)}</div><h3>{E(n)}</h3><p>{E(d)}</p>
<a class="more" href="/who-we-serve/#{k}">How we help {icon('arrow',16)}</a></div>""" for k, n, ic, d, _ in AUDIENCES) + f"""<div class="card" style="background:var(--navy);border-color:var(--navy)"><div class="ib" style="background:rgba(255,255,255,.08);border-color:rgba(255,255,255,.15);color:var(--brass2)">{icon('phone')}</div>
<h3 style="color:#fff">Not sure where you fit?</h3><p style="color:#b9c4d4">Call us. A five-minute conversation is usually enough to know whether we can help.</p>
<a class="more" style="color:var(--brass2)" href="tel:{CFG['phone_tel']}">{CFG['phone']} {icon('arrow',16)}</a></div>"""
    body = f"""
<section class="hero"><div class="container">
  <div>
    <span class="kicker">Phoenix Private Investigators · Veteran-Led</span>
    <h1>The truth, <span>documented.</span></h1>
    <p class="lead">The Office of Ross and Gibson is a licensed Arizona private investigation agency in Phoenix. Surveillance, skip tracing, background checks, infidelity, custody, fraud and more — handled with military discipline and complete discretion.</p>
    <div class="ctas"><a class="btn brass" href="/contact/">{icon('lock',18)}Free Confidential Consultation</a>
    <a class="btn ghost light" href="tel:{CFG['phone_tel']}">{icon('phone',18)}{CFG['phone']}</a></div>
    <p class="note">No job too small. No job too big.</p>
  </div>
  <div class="hcard">
    <h3>Talk to an investigator</h3><p>Tell us what's going on. We'll tell you honestly what an investigation can do.</p>
    <ul>
      <li>{icon('check')}Free, no-obligation consultation</li>
      <li>{icon('check')}Clear scope and written quote before work begins</li>
      <li>{icon('check')}Licensed agency · AZ DPS #{CFG['agency_license']}</li>
      <li>{icon('check')}Everything you share stays confidential</li>
    </ul>
    <a class="btn brass" href="/contact/">Start a Confidential Inquiry</a>
  </div>
</div></section>
<div class="trust"><div class="container">{trust_html}</div></div>

<section><div class="container">
  <div class="sh"><span class="kicker">What we do</span><h2>Full-service private investigations.</h2>
  <p>From a single address verification to multi-week surveillance operations, every case gets the same standard: lawful methods, careful documentation and honest answers.</p></div>
  <div class="grid g3">{''.join(svc_card(s) for s in SERVICES[:9])}</div>
  <p style="margin-top:28px"><a class="btn ghost" href="/services/">View all {len(SERVICES)} services {icon('arrow',18)}</a></p>
</div></section>

<section class="alt"><div class="container split">
  <div><p class="big-quote">No job too small.<br><span>No job too big.</span></p>
  <p class="lead" style="margin-top:22px">Some clients need one fact confirmed. Others need a team in the field for weeks. We scope every case to what you actually need — and nothing you don't.</p></div>
  <ul class="examples">
    <li>{icon('check')}<span><b>Small:</b> confirm a current address, verify someone's employment, or run a pre-date background check.</span></li>
    <li>{icon('check')}<span><b>Medium:</b> a few days of surveillance, a witness locate and interview, or a hidden-asset search.</span></li>
    <li>{icon('check')}<span><b>Large:</b> multi-week claim investigations, internal theft cases, and litigation support for law firms.</span></li>
  </ul>
</div></section>

<section><div class="container">
  <div class="sh"><span class="kicker">How it works</span><h2>A clear process, start to finish.</h2></div>
  <div class="steps">
    <div class="step"><h3>Confidential consultation</h3><p>Tell us what's happening. We listen, ask the right questions and tell you honestly whether we can help.</p></div>
    <div class="step"><h3>Plan &amp; written quote</h3><p>We agree on objectives, scope, timeline and cost in writing before any work begins.</p></div>
    <div class="step"><h3>Investigation</h3><p>Licensed investigators work the case using lawful methods, with updates as it progresses.</p></div>
    <div class="step"><h3>Documented report</h3><p>You receive a clear written report with time-stamped photos, video and findings you can share with your attorney.</p></div>
  </div>
</div></section>

<section class="alt"><div class="container">
  <div class="sh"><span class="kicker">Who we serve</span><h2>Trusted by people who need facts.</h2></div>
  <div class="grid g3">{aud}</div>
</div></section>

<section><div class="container founder">
  <div class="portrait"><span class="mono">AR</span><span class="tag">Anthony Romero · Founder &amp; Licensed Qualifying Party</span></div>
  <div><span class="kicker">Leadership</span><h2>Led by a veteran. Built on discipline.</h2>
  <p class="lead" style="margin-top:16px">Anthony Romero served in the United States Air Force and went on to build businesses and co-found Credit4Vets, a veteran-founded nonprofit helping Arizona veterans with credit, housing and financial stability.</p>
  <p style="margin-top:14px;color:var(--muted)">He founded The Office of Ross and Gibson to bring the same mission-first standards — attention to detail, integrity and follow-through — to private investigations.</p>
  <div class="creds"><span class="chip">{icon('star')}U.S. Air Force Veteran</span><span class="chip">{icon('shield')}AZ DPS Licensed Qualifying Party</span><span class="chip">{icon('family')}Co-Founder, Credit4Vets</span></div>
  <a class="btn ghost" href="/about/">About our agency {icon('arrow',18)}</a></div>
</div></section>
{post_cards(posts)}
<section><div class="container" style="max-width:860px">
  <div class="sh center" style="text-align:center"><span class="kicker">FAQ</span><h2>Common questions</h2></div>
  {faq_html(FAQ[:5])}
  <p style="margin-top:24px;text-align:center"><a class="btn ghost" href="/faq/">More questions {icon('arrow',18)}</a></p>
</div></section>
{cta_band()}"""
    page("/", "Phoenix Private Investigator | The Office of Ross and Gibson (TORG PI)",
         "Veteran-led, Arizona-licensed private investigators in Phoenix. Surveillance, skip tracing, background checks, infidelity, custody, insurance fraud and more. Free confidential consultation: (602) 499-3230.",
         body, "", [faq_ld(FAQ[:5])])


# ------------------------------------------------------------------ services
def services_hub():
    body = f"""<section class="phero"><div class="container">{crumbs(("Services", None))}
<span class="kicker">Services</span><h1>Private investigation services in Phoenix &amp; across Arizona.</h1>
<p class="lead">Whatever you need to find out, we can likely help — and if we can't, we'll tell you. No job too small, no job too big.</p>
<div class="ctas"><a class="btn brass" href="/contact/">Free Consultation</a><a class="btn ghost light" href="tel:{CFG['phone_tel']}">{icon('phone',18)}{CFG['phone']}</a></div></div></section>
<section><div class="container"><div class="grid g3">{''.join(svc_card(s) for s in SERVICES)}</div>
<div class="callout" style="margin-top:36px">Don't see your situation? Most cases don't fit neatly into one box. <a href="/contact/" style="color:var(--navy);font-weight:700">Tell us what's going on</a> and we'll recommend the right approach.</div>
</div></section>{cta_band()}"""
    ld = [crumb_ld(("Services", "/services/")),
          {"@type": "OfferCatalog", "name": "Private Investigation Services", "itemListElement": [
              {"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["name"], "url": f"{U}/services/{s['slug']}/"}} for s in SERVICES]}]
    page("/services/", "Private Investigation Services in Phoenix, AZ | The Office of Ross and Gibson",
         "Surveillance, skip tracing, background investigations, infidelity, child custody, asset searches, insurance fraud, corporate, due diligence, litigation support and more.",
         body, "/services/", ld)


def service(s):
    lis = lambda xs: "<ul>" + "".join(f"<li>{E(x)}</li>" for x in xs) + "</ul>"
    others = [o for o in SERVICES if o["slug"] != s["slug"]]
    side_links = "".join(f'<li><a href="/services/{o["slug"]}/">{E(o["name"])}</a></li>' for o in others)
    body = f"""<section class="phero"><div class="container">{crumbs(("Services", "/services/"), (s['name'], None))}
<span class="kicker">{E(s['name'])}</span><h1>{E(s['title'])}</h1>
<p class="lead">{E(s['short'])}</p></div></section>
<section><div class="container svc-layout">
  <div class="prose">
    <p style="font-size:18px">{E(s['intro'])}</p>
    <h2>What we handle</h2>{lis(s['what'])}
    <h2>When clients call us</h2>{lis(s['when'])}
    <h2>What you receive</h2>
    <ul><li>A free, confidential consultation to understand your goals</li><li>A written scope, timeline and quote before work begins</li>
    <li>Regular updates while the investigation is active</li><li>A clear written report with supporting photos, video or records</li></ul>
    <div class="callout"><b>Good to know:</b> {E(s['note'])}</div>
    <h2>Why The Office of Ross and Gibson</h2>
    <p>We're a licensed Arizona private investigation agency (AZ DPS #{CFG['agency_license']}) led by a U.S. Air Force veteran. That means disciplined planning, lawful methods, careful documentation and honest communication — whether your case takes an afternoon or a month.</p>
  </div>
  <aside class="side">
    <div class="box dark"><h3>Get a confidential consultation</h3><p>Free and no obligation. Tell us what's going on.</p>
    <a class="btn brass" href="/contact/?service={s['slug']}">Request Consultation</a>
    <a class="btn ghost light" href="tel:{CFG['phone_tel']}">{icon('phone',18)}{CFG['phone']}</a></div>
    <div class="box"><h4>Other services</h4><ul>{side_links}</ul></div>
  </aside>
</div></section>{cta_band()}"""
    path = f"/services/{s['slug']}/"
    ld = [crumb_ld(("Services", "/services/"), (s["name"], path)),
          {"@type": "Service", "name": s["name"], "serviceType": s["name"], "description": s["intro"], "url": U + path,
           "provider": {"@id": U + "/#org"}, "areaServed": {"@type": "State", "name": "Arizona"}}]
    page(path, f"{s['title']} | The Office of Ross and Gibson", s["short"] + " Licensed, veteran-led. Free consultation.", body, "/services/", ld)


# ------------------------------------------------------------------ who we serve
def who():
    blocks = ""
    for i, (k, n, ic, d, pts) in enumerate(AUDIENCES):
        alt = ' class="alt"' if i % 2 else ""
        blocks += f"""<section id="{k}"{alt}><div class="container split">
<div><div class="card" style="display:inline-grid;padding:0;border:none;background:none"><div class="ib">{icon(ic,24)}</div></div>
<h2>{E(n)}</h2><p class="lead" style="margin-top:14px">{E(d)}</p>
<p style="margin-top:24px"><a class="btn" href="/contact/">Talk to an investigator</a></p></div>
<ul class="examples">{''.join(f'<li>{icon("check")}<span>{E(p)}</span></li>' for p in pts)}</ul>
</div></section>"""
    body = f"""<section class="phero"><div class="container">{crumbs(("Who We Serve", None))}
<span class="kicker">Who we serve</span><h1>Investigations for attorneys, businesses, insurers and families.</h1>
<p class="lead">Different clients need different things. Here's how we help each of them.</p></div></section>{blocks}{cta_band()}"""
    page("/who-we-serve/", "Who We Serve | Attorneys, Businesses, Insurers & Families | Ross and Gibson",
         "Private investigation services for attorneys, employers, insurance carriers, individuals, families and veterans across Arizona.",
         body, "/who-we-serve/", [crumb_ld(("Who We Serve", "/who-we-serve/"))])


# ------------------------------------------------------------------ about
def about():
    a = CFG["author"]
    body = f"""<section class="phero"><div class="container">{crumbs(("About", None))}
<span class="kicker">About us</span><h1>Veteran-led. Licensed. Discreet.</h1>
<p class="lead">The Office of Ross and Gibson is a licensed Arizona private investigation agency headquartered in Phoenix.</p></div></section>
<section><div class="container founder" id="anthony">
  <div class="portrait"><span class="mono">AR</span><span class="tag">Anthony Romero · Founder</span></div>
  <div class="prose"><span class="kicker">Our founder</span><h2 style="margin-top:0">Anthony Romero</h2>
  <div class="creds"><span class="chip">{icon('star')}U.S. Air Force Veteran</span><span class="chip">{icon('shield')}AZ DPS Licensed Qualifying Party</span><span class="chip">{icon('family')}Co-Founder &amp; CEO, Credit4Vets</span></div>
  <p>Anthony Romero is a United States Air Force veteran with a background in small business and tax finance. After his service he built businesses and co-founded <a href="https://credit4vets.org/" rel="noopener">Credit4Vets</a>, a veteran-founded nonprofit in Tempe that helps veterans with credit, housing, business and financial stability.</p>
  <p>Anthony founded The Office of Ross and Gibson to bring the standards he learned in uniform — preparation, attention to detail, integrity and follow-through — to people who need the truth. He serves as the agency's licensed qualifying party with the Arizona Department of Public Safety.</p>
  <p>Whether a client is an attorney on deadline, a business owner facing internal theft or a parent worried about their child, Anthony's approach is the same: listen carefully, tell the truth about what's possible, work within the law, and document everything.</p></div>
</div></section>
<section class="alt"><div class="container">
  <div class="sh"><span class="kicker">How we work</span><h2>Our standards.</h2></div>
  <div class="grid g4">
    <div class="card"><div class="ib">{icon('lock')}</div><h3>Discretion</h3><p>Your inquiry, your case and your results stay between us and the people you authorize.</p></div>
    <div class="card"><div class="ib">{icon('scale')}</div><h3>Lawful methods</h3><p>We follow Arizona and federal law — evidence gathered the wrong way can hurt your case.</p></div>
    <div class="card"><div class="ib">{icon('doc')}</div><h3>Documentation</h3><p>Time-stamped photo, video and written reports you can hand to your attorney.</p></div>
    <div class="card"><div class="ib">{icon('check2')}</div><h3>Honesty</h3><p>Clear quotes, realistic expectations and the truth — even when it isn't what you hoped.</p></div>
  </div>
</div></section>
<section><div class="container split">
  <div><span class="kicker">Licensing</span><h2>Licensed by the Arizona Department of Public Safety.</h2>
  <p class="lead" style="margin-top:14px">Private investigation is a licensed profession in Arizona. Always verify an investigator before you hire them.</p></div>
  <ul class="examples">
    <li>{icon('shield')}<span><b>Agency:</b> The Office of Ross and Gibson</span></li>
    <li>{icon('id')}<span><b>AZ DPS PI Agency License:</b> #{CFG['agency_license']}</span></li>
    <li>{icon('star')}<span><b>Qualifying Party:</b> Anthony Romero</span></li>
    <li>{icon('pin')}<span><b>Office:</b> {CFG['street']}, {CFG['city']}, {CFG['region']} {CFG['zip']}</span></li>
  </ul>
</div></section>{cta_band()}"""
    person = {"@type": "Person", "@id": U + "/about/#anthony", "name": a["name"], "jobTitle": a["jobTitle"],
              "url": a["url"], "sameAs": a["sameAs"], "worksFor": {"@id": U + "/#org"},
              "description": a["bio"]}
    page("/about/", "About The Office of Ross and Gibson | Veteran-Led Phoenix PI Agency",
         "Founded by U.S. Air Force veteran Anthony Romero, The Office of Ross and Gibson is an Arizona DPS-licensed private investigation agency in Phoenix.",
         body, "/about/", [crumb_ld(("About", "/about/")), person])


# ------------------------------------------------------------------ faq
def faq():
    body = f"""<section class="phero"><div class="container">{crumbs(("FAQ", None))}
<span class="kicker">FAQ</span><h1>Questions about hiring a private investigator.</h1>
<p class="lead">Straight answers. If yours isn't here, call us — the consultation is free.</p></div></section>
<section><div class="container" style="max-width:860px">{faq_html(FAQ)}</div></section>{cta_band()}"""
    page("/faq/", "Private Investigator FAQ | Cost, Legality & What to Expect | Ross and Gibson",
         "How much does a private investigator cost in Phoenix? Is it legal? What can't a PI do? Answers from a licensed Arizona agency.",
         body, "/faq/", [crumb_ld(("FAQ", "/faq/")), faq_ld(FAQ)])


# ------------------------------------------------------------------ areas
def areas():
    chips = "".join(f"<span>{E(a)}</span>" for a in AREAS)
    body = f"""<section class="phero"><div class="container">{crumbs(("Areas We Serve", None))}
<span class="kicker">Areas we serve</span><h1>Private investigators serving Phoenix and all of Arizona.</h1>
<p class="lead">Our office is in Phoenix at {CFG['street']}. We work throughout the Valley and travel statewide.</p></div></section>
<section><div class="container">
<div class="sh"><span class="kicker">Phoenix metro &amp; statewide</span><h2>Where we work</h2>
<p>Surveillance, locates, interviews and field work across Maricopa and Pinal counties, with statewide travel for the right case.</p></div>
<div class="areas">{chips}</div>
<div class="callout" style="margin-top:34px">Have a case outside Arizona? Contact us — we'll tell you honestly whether we can help or point you in the right direction.</div>
<iframe class="map" loading="lazy" title="Office location" src="https://www.google.com/maps?q=4015+N+15th+Ave,+Phoenix,+AZ+85015&output=embed"></iframe>
</div></section>{cta_band()}"""
    page("/areas-we-serve/", "Areas We Serve | Phoenix, Scottsdale, Mesa & Arizona Private Investigator",
         "Licensed private investigators serving Phoenix, Scottsdale, Tempe, Mesa, Chandler, Gilbert, Glendale, Peoria and communities across Arizona.",
         body, "", [crumb_ld(("Areas We Serve", "/areas-we-serve/"))])


# ------------------------------------------------------------------ contact
def contact():
    opts = "".join(f'<option value="{s["slug"]}">{E(s["name"])}</option>' for s in SERVICES)
    body = f"""<section class="phero"><div class="container">{crumbs(("Contact", None))}
<span class="kicker">Confidential consultation</span><h1>Let's talk about what's going on.</h1>
<p class="lead">Consultations are free and confidential. Prefer to talk now? Call <a href="tel:{CFG['phone_tel']}" style="color:#fff;border-bottom:1px solid var(--brass2)">{CFG['phone']}</a>.</p></div></section>
<section><div class="container svc-layout">
  <form class="form" action="{CFG['form_action']}" method="POST">
    <input type="hidden" name="_subject" value="New consultation request — torgpi.com">
    <input type="hidden" name="_next" value="{U}/contact/thanks/">
    <input type="hidden" name="_template" value="table">
    <input type="text" name="_honey" class="hp" tabindex="-1" autocomplete="off">
    <div class="row"><div><label for="n">Full name *</label><input id="n" name="name" required autocomplete="name"></div>
    <div><label for="p">Phone *</label><input id="p" name="phone" type="tel" required autocomplete="tel"></div></div>
    <div class="row"><div><label for="e">Email</label><input id="e" name="email" type="email" autocomplete="email"></div>
    <div><label for="c">Best way to reach you</label><select id="c" name="contact_preference"><option>Phone call</option><option>Text message</option><option>Email</option></select></div></div>
    <div class="row"><div><label for="s">Type of case</label><select id="s" name="case_type"><option value="">Select one…</option>{opts}<option value="other">Other / not sure</option></select></div>
    <div><label for="l">City / area</label><input id="l" name="location" placeholder="e.g., Scottsdale"></div></div>
    <div><label for="m">Briefly, how can we help?</label><textarea id="m" name="message" placeholder="A sentence or two is plenty."></textarea>
    <p class="hint">Please don't include sensitive details here — we'll discuss specifics privately by phone.</p></div>
    <div><button class="btn brass" type="submit">{icon('lock',18)}Send Confidential Request</button></div>
  </form>
  <aside class="side">
    <div class="box">
      <div class="cbox">{icon('phone')}<div><b>Call or text</b><a href="tel:{CFG['phone_tel']}">{CFG['phone']}</a></div></div>
      <div class="cbox">{icon('mail')}<div><b>Email</b><a href="mailto:{CFG['email']}">{CFG['email']}</a></div></div>
      <div class="cbox">{icon('pin')}<div><b>Office</b><span>{CFG['street']}<br>{CFG['city']}, {CFG['region']} {CFG['zip']}</span></div></div>
      <div class="cbox" style="border:none">{icon('clock')}<div><b>Meetings</b><span>By appointment</span></div></div>
    </div>
    <div class="box" style="font-size:13.5px;color:var(--muted)">{icon('shield',20)}<p style="margin-top:8px">Licensed by the Arizona Department of Public Safety, PI Agency #{CFG['agency_license']}. If someone is in immediate danger, call 911.</p></div>
  </aside>
</div></section>
<script>(function(){{var q=new URLSearchParams(location.search).get('service');if(q){{var s=document.getElementById('s');if(s)s.value=q;}}}})();</script>"""
    page("/contact/", "Contact a Phoenix Private Investigator | Free Confidential Consultation",
         "Request a free, confidential consultation with The Office of Ross and Gibson. Call (602) 499-3230 or email hello@torgpi.com.",
         body, "", [crumb_ld(("Contact", "/contact/")), {"@type": "ContactPage", "url": U + "/contact/"}])
    thanks = f"""<section class="phero" style="padding:110px 0"><div class="container" style="max-width:760px">
<span class="kicker">Received</span><h1>Thank you. We'll be in touch shortly.</h1>
<p class="lead">Your request was sent confidentially. If your matter is urgent, call <a href="tel:{CFG['phone_tel']}" style="color:#fff">{CFG['phone']}</a>.</p>
<div class="ctas"><a class="btn brass" href="/">Back to home</a><a class="btn ghost light" href="/blog/">Read our insights</a></div></div></section>"""
    write("/contact/thanks/", head("Thank you | The Office of Ross and Gibson", "Your consultation request was received.", "/contact/thanks/").replace(
        "<meta name=\"description\"", "<meta name=\"robots\" content=\"noindex\" />\n<meta name=\"description\"", 1) + header() + thanks + footer(SERVICES))
    PAGES.remove("/contact/thanks/")


# ------------------------------------------------------------------ privacy / 404
def privacy():
    body = f"""<section class="phero"><div class="container">{crumbs(("Privacy", None))}<h1>Privacy Policy</h1>
<p class="lead">Last updated November 2026</p></div></section>
<section><div class="wrap prose">
<p>The Office of Ross and Gibson ("we," "us") respects your privacy. Confidentiality is central to what we do.</p>
<h2>What we collect</h2><ul><li>Information you choose to send us through our contact form, by email or by phone, such as your name, phone number, email address and a description of your matter.</li>
<li>Basic, non-identifying website analytics such as pages visited and general location, if analytics are enabled.</li></ul>
<h2>How we use it</h2><ul><li>To respond to your inquiry and provide the services you request.</li><li>To meet our legal and licensing obligations.</li></ul>
<p>We do not sell your information. We do not share your inquiry or case information with anyone except as you authorize, as needed to deliver services (for example, to your attorney at your direction), or as required by law.</p>
<h2>Form processing</h2><p>Our contact form is delivered to us by a third-party form-forwarding service. Please don't include sensitive details in the form; we'll discuss specifics privately.</p>
<h2>Contact</h2><p>Questions? Email <a href="mailto:{CFG['email']}">{CFG['email']}</a> or call {CFG['phone']}.</p>
</div></section>"""
    page("/privacy/", "Privacy Policy | The Office of Ross and Gibson", "How The Office of Ross and Gibson handles information you share with us.", body)
    nf = f"""<section class="phero" style="padding:120px 0"><div class="container" style="max-width:760px">
<span class="kicker">404</span><h1>We investigated. That page doesn't exist.</h1>
<p class="lead">Try our services or get in touch.</p>
<div class="ctas"><a class="btn brass" href="/services/">View services</a><a class="btn ghost light" href="/contact/">Contact us</a></div></div></section>"""
    write("/404.html", head("Page not found | The Office of Ross and Gibson", "Page not found.", "/404.html") + header() + nf + footer(SERVICES))
    PAGES.remove("/404.html")


def render_all(posts):
    PAGES.clear()
    home(posts); services_hub()
    for s in SERVICES:
        service(s)
    who(); about(); faq(); areas(); contact(); privacy()
    return list(PAGES)
