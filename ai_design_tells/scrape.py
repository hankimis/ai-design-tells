"""
scrape.py, render real sites and extract computed-style design signals.

v1's detector read one self-contained HTML file; it could not audit a live SPA
whose CSS sits in external/hashed files. This module removes that limit: it drives
headless Chrome (via Playwright, system-Chrome channel), lets the page's CSS and
fonts fully apply, then reads *computed styles* off the live DOM, the ground
truth a static parse cannot see.

For each URL it returns a normalized `SiteSignals` dict (fonts, colors, gradients,
radii, shadows, spacing, tracking, focus styles, layout, emoji, copy) that the
recalibrated detector (scorer.score_signals) consumes directly. The same dict is
what we aggregate across dozens of sites to *learn* the empirical distribution of
human-crafted design and recalibrate the tells.

Usage:
    python src/scrape.py            # scrapes the built-in corpus -> data/sites/*.json
    python src/scrape.py URL ...    # scrape specific URLs
"""
from __future__ import annotations
import os, sys, json, time

# The extraction script runs *inside* the page after CSS + fonts apply.
EXTRACT_JS = r"""
() => {
  const gcs = el => getComputedStyle(el);
  const all = Array.from(document.querySelectorAll('*')).slice(0, 6000);
  const vis = el => {
    const r = el.getBoundingClientRect();
    const s = gcs(el);
    return r.width > 1 && r.height > 1 && s.visibility !== 'hidden' && s.display !== 'none';
  };
  const visible = all.filter(vis);

  // ---- helpers ----
  const firstFamily = ff => (ff || '').split(',')[0].replace(/["']/g, '').trim().toLowerCase();
  const toHexHue = (rgb) => {
    const m = (rgb || '').match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const [r, g, b] = m[1].split(',').map(x => parseFloat(x));
    const mx = Math.max(r, g, b) / 255, mn = Math.min(r, g, b) / 255;
    const l = (mx + mn) / 2; const d = mx - mn;
    let s = d === 0 ? 0 : d / (1 - Math.abs(2 * l - 1));
    let h = 0;
    if (d !== 0) {
      const rr = r/255, gg = g/255, bb = b/255;
      if (mx === rr) h = ((gg - bb) / d) % 6;
      else if (mx === gg) h = (bb - rr) / d + 2;
      else h = (rr - gg) / d + 4;
      h *= 60; if (h < 0) h += 360;
    }
    return { h, s, l };
  };
  const isPurple = c => c && c.s > 0.18 && c.h >= 238 && c.h <= 300;

  // ---- fonts ----
  const bodyFam = firstFamily(gcs(document.body).fontFamily);
  const heads = Array.from(document.querySelectorAll('h1,h2')).filter(vis);
  const headFam = heads.length ? firstFamily(gcs(heads[0]).fontFamily) : bodyFam;
  let loadedFaces = [];
  try { document.fonts.forEach(f => loadedFaces.push((f.family||'').replace(/["']/g,'').toLowerCase())); } catch(e){}

  // ---- colors / gradients on interactive + accent surfaces ----
  const inter = visible.filter(el => ['A','BUTTON'].includes(el.tagName) ||
                  el.getAttribute('role') === 'button');
  const accentColors = [];
  let purpleAccents = 0, accentSampled = 0;
  inter.slice(0, 120).forEach(el => {
    const s = gcs(el);
    [s.backgroundColor, s.color, s.borderColor].forEach(c => {
      const hh = toHexHue(c); if (hh && hh.s > 0.12) { accentColors.push(Math.round(hh.h)); accentSampled++; if (isPurple(hh)) purpleAccents++; }
    });
  });
  // gradients anywhere
  let bluePurpleGradients = 0, anyGradients = 0;
  visible.slice(0, 3000).forEach(el => {
    const bg = gcs(el).backgroundImage || '';
    if (bg.includes('gradient')) {
      anyGradients++;
      const stops = (bg.match(/rgba?\([^)]+\)/g) || []).map(toHexHue).filter(Boolean);
      const hasBlue = stops.some(c => c.s>0.15 && c.h>=200 && c.h<=255);
      const hasPurple = stops.some(c => isPurple(c));
      if (hasBlue && hasPurple) bluePurpleGradients++;
    }
  });

  // ---- radii / shadows / spacing distributions ----
  const radii = {}, shadows = {}, paddings = {}, fontSizes = {};
  const cardish = visible.filter(el => {
    const s = gcs(el); return s.borderRadius !== '0px' || s.boxShadow !== 'none';
  });
  cardish.slice(0, 1500).forEach(el => {
    const s = gcs(el);
    const r = parseFloat(s.borderTopLeftRadius) || 0;
    if (r > 0) radii[r] = (radii[r]||0)+1;
    if (s.boxShadow && s.boxShadow !== 'none') {
      const diffuse = /rgba\([^)]*0\.0?[0-9]+\)/.test(s.boxShadow) && parseFloat((s.boxShadow.match(/(\d+)px/g)||['0'])[2]||0) >= 8;
      shadows[diffuse ? 'diffuse' : 'other'] = (shadows[diffuse?'diffuse':'other']||0)+1;
    }
  });
  visible.slice(0, 3000).forEach(el => {
    const s = gcs(el);
    const p = s.paddingTop; if (p && p !== '0px') paddings[p] = (paddings[p]||0)+1;
    const fs = Math.round(parseFloat(s.fontSize)); if (fs) fontSizes[fs] = (fontSizes[fs]||0)+1;
  });

  // ---- heading tracking ----
  let bigHeads = heads.filter(h => parseFloat(gcs(h).fontSize) >= 30);
  let negTracked = bigHeads.filter(h => parseFloat(gcs(h).letterSpacing) < -0.1).length;

  // ---- focus styles (best effort; cross-origin sheets throw) ----
  let focusVisible = false, hairlineRule = false, sheetsRead = 0, sheetsBlocked = 0;
  for (const sh of Array.from(document.styleSheets)) {
    try {
      const rules = sh.cssRules; sheetsRead++;
      for (const r of Array.from(rules)) {
        const t = r.cssText || '';
        if (t.includes(':focus-visible') || t.includes(':focus')) focusVisible = true;
        if (/border[^;]*rgba\([^)]*0?\.[0-1]?\d\)/.test(t)) hairlineRule = true;
      }
    } catch(e){ sheetsBlocked++; }
  }

  // ---- layout: centered fraction of big blocks ----
  const blocks = visible.filter(el => ['SECTION','DIV','HEADER','MAIN','ARTICLE'].includes(el.tagName))
    .filter(el => { const r = el.getBoundingClientRect(); return r.width > window.innerWidth*0.5 && r.height > 80; })
    .slice(0, 200);
  let centered = 0;
  blocks.forEach(el => { if (gcs(el).textAlign === 'center') centered++; });
  const centeredFrac = blocks.length ? centered / blocks.length : 0;

  // ---- emoji in headings ----
  const emojiRe = /[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{2190}-\u{21FF}\u{2B00}-\u{2BFF}]/u;
  let emojiHeads = 0;
  Array.from(document.querySelectorAll('h1,h2,h3')).slice(0,80).forEach(h => { if (emojiRe.test(h.textContent||'')) emojiHeads++; });

  // ---- copy ----
  const h1 = (document.querySelector('h1')?.textContent || '').trim().slice(0, 200);
  const btnTexts = inter.map(el => (el.textContent||'').trim()).filter(t => t && t.length < 40).slice(0, 60);

  const dist = o => Object.entries(o).map(([k,v]) => [isNaN(+k)?k:+k, v]).sort((a,b)=>b[1]-a[1]);
  return {
    title: document.title,
    fonts: { body: bodyFam, heading: headFam, loaded_count: new Set(loadedFaces).size,
             loaded_sample: Array.from(new Set(loadedFaces)).slice(0,12) },
    color: { accent_hues: accentColors.slice(0,200), accent_sampled: accentSampled,
             purple_accents: purpleAccents, any_gradients: anyGradients, blue_purple_gradients: bluePurpleGradients },
    radii: dist(radii), shadows, paddings: dist(paddings), font_sizes: dist(fontSizes),
    heading: { big_count: bigHeads.length, neg_tracked: negTracked },
    focus: { focus_visible: focusVisible, hairline_rule: hairlineRule, sheets_read: sheetsRead, sheets_blocked: sheetsBlocked },
    layout: { blocks: blocks.length, centered_fraction: centeredFrac },
    emoji_headings: emojiHeads,
    copy: { h1, buttons: btnTexts },
  };
}
"""


def _name_of(url):
    return url.replace("https://", "").replace("http://", "").rstrip("/").replace("/", "_")


def scrape(urls, out_dir, shots_dir=None, timeout=30000, resume=True):
    from playwright.sync_api import sync_playwright
    os.makedirs(out_dir, exist_ok=True)
    if shots_dir:
        os.makedirs(shots_dir, exist_ok=True)
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True,
                                    args=["--disable-blink-features=AutomationControlled"])
        for url in urls:
            name = _name_of(url)
            if resume and os.path.exists(os.path.join(out_dir, f"{name}.json")):
                print(f"  skip {name} (already scraped)")
                continue
            ctx = browser.new_context(viewport={"width": 1440, "height": 900},
                                      user_agent=("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                                                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"))
            page = ctx.new_page()
            rec = {"url": url, "name": name}
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=timeout)
                page.wait_for_timeout(2800)  # let CSS + webfonts settle
                try:
                    page.evaluate("document.fonts && document.fonts.ready")
                except Exception:
                    pass
                sig = page.evaluate(EXTRACT_JS)
                rec.update(sig)
                rec["ok"] = True
                if shots_dir:
                    try:
                        page.screenshot(path=os.path.join(shots_dir, f"{name}.png"),
                                        clip={"x": 0, "y": 0, "width": 1440, "height": 900})
                    except Exception:
                        pass
                print(f"  ok   {name}  font={sig['fonts']['body'][:18]:18}  "
                      f"purpleAcc={sig['color']['purple_accents']}  bpGrad={sig['color']['blue_purple_gradients']}  "
                      f"focusVis={sig['focus']['focus_visible']}  center={sig['layout']['centered_fraction']:.2f}")
            except Exception as e:
                rec["ok"] = False
                rec["error"] = str(e)[:160]
                print(f"  FAIL {name}: {str(e)[:90]}")
            finally:
                ctx.close()
            with open(os.path.join(out_dir, f"{name}.json"), "w", encoding="utf-8") as f:
                json.dump(rec, f, ensure_ascii=False, indent=2)
            results[name] = rec
        browser.close()
    return results


# Curated corpus of design-led, human-crafted sites across categories.
CORPUS = [
    # dev tools / SaaS (design-led)
    "https://stripe.com", "https://linear.app", "https://vercel.com", "https://www.framer.com",
    "https://www.raycast.com", "https://supabase.com", "https://railway.app", "https://resend.com",
    "https://clerk.com", "https://posthog.com", "https://www.retool.com", "https://render.com",
    "https://sentry.io", "https://www.mintlify.com", "https://planetscale.com", "https://www.prisma.io",
    "https://tailwindcss.com", "https://www.netlify.com", "https://www.cloudflare.com",
    # AI labs / products
    "https://www.anthropic.com", "https://openai.com", "https://www.perplexity.ai", "https://elevenlabs.io",
    # fintech (incl. Toss)
    "https://www.toss.im", "https://mercury.com", "https://ramp.com", "https://www.brex.com",
    "https://stripe.com/payments",
    # design / creative / productivity
    "https://www.notion.so", "https://www.figma.com", "https://www.loom.com", "https://pitch.com",
    "https://webflow.com", "https://www.dropbox.com", "https://linear.app/method",
    # consumer / brand
    "https://www.apple.com", "https://www.airbnb.com", "https://www.nike.com", "https://www.spotify.com",
    "https://github.com", "https://www.intercom.com", "https://arc.net", "https://www.duolingo.com",
]


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.join(here, "..")
    args = sys.argv[1:]
    if len(args) == 1 and os.path.exists(args[0]):       # a file of URLs (one per line)
        urls = [ln.strip() for ln in open(args[0]) if ln.strip() and not ln.startswith("#")]
    elif args:
        urls = args
    else:
        urls = CORPUS
    out = os.path.join(root, "data", "sites")
    shots = os.path.join(root, "data", "shots")
    t0 = time.time()
    res = scrape(urls, out, shots)
    ok = sum(1 for r in res.values() if r.get("ok"))
    print(f"\nscraped {ok}/{len(urls)} sites in {time.time()-t0:.0f}s -> {out}")
