# torgpi.com — The Office of Ross and Gibson

Static site + drip blog for GitHub Pages. Same zero-dependency engine as the other T47 / Xsatori Labs sites.

- `content.py` — all service, audience, area and FAQ copy (edit text here)
- `pages.py` — marketing page templates · `chrome.py` — shared header/footer/CSS/schema
- `posts/*.md` — blog posts; future `date:` = queued, published by the daily Action
- `site.json` — name, phone, email, address, license #, form endpoint
- Run `python3 build.py` to regenerate everything.

## Launch checklist
1. Create repo `t47group/torgpi-site`, push, enable Pages (main / root). `CNAME` = www.torgpi.com.
2. DNS at the registrar: `www` CNAME → `t47group.github.io`; apex A records → 185.199.108.153, .109.153, .110.153, .111.153. Turn on "Enforce HTTPS".
3. Contact form uses FormSubmit → hello@torgpi.com. Submit the form once after launch and click the activation email FormSubmit sends.
4. Swap the "AR" monogram for Anthony's photo: add `assets/anthony.jpg` and replace `<span class="mono">AR</span>` in pages.py with `<img src="/assets/anthony.jpg" alt="Anthony Romero">`.
5. Add the site to Google Search Console + Bing, submit sitemap.xml. Create Google Business Profile.
