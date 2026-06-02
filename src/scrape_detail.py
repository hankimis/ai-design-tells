"""
scrape_detail.py, deep per-component CSS extraction across real sites.

Where scrape.py reads *aggregate signals* for the Tell-Score detector, this module
reads the *actual CSS values* designers ship, component by component, so we can
build a reference catalog: what real buttons, headings, body text, layout
containers, spacing scales and color palettes look like, in light AND dark mode.

For each URL it captures, separately for the light and the dark rendering
(via prefers-color-scheme emulation):

  - buttons    : deduped specs (bg, color, border, radius, padding, font, shadow)
                 with a primary/secondary/ghost role guess
  - typography : h1..h6 + body + small, each with size/weight/line-height/tracking
                 /family/color
  - layout     : container max-widths, section vertical rhythm, grid templates, gaps
  - spacing    : the padding / margin / gap scales actually in use
  - color      : page background, text ramp, accent, surfaces, borders (with counts)

Usage:
    python src/scrape_detail.py URL ...          # specific sites
    python src/scrape_detail.py data/list.txt    # a file of URLs (one per line)
    python src/scrape_detail.py                  # the built-in DETAIL_CORPUS
"""
from __future__ import annotations
import os, sys, json, time

# Runs inside the page. Returns the full per-component CSS snapshot for whatever
# color scheme is currently emulated, so the driver can call it twice.
EXTRACT_DETAIL_JS = r"""
() => {
  const gcs = el => getComputedStyle(el);
  const px = v => { const n = parseFloat(v); return isNaN(n) ? 0 : Math.round(n * 100) / 100; };
  const all = Array.from(document.querySelectorAll('*')).slice(0, 8000);
  const vis = el => {
    const r = el.getBoundingClientRect(); const s = gcs(el);
    return r.width > 1 && r.height > 1 && s.visibility !== 'hidden' && s.display !== 'none' &&
           parseFloat(s.opacity || '1') > 0.05;
  };
  const visible = all.filter(vis);
  const fam = ff => (ff || '').split(',')[0].replace(/["']/g, '').trim();

  // rgb(a) -> {r,g,b,a, hex, lum}
  const parseColor = (c) => {
    if (!c) return null;
    const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null;
    const p = m[1].split(',').map(x => parseFloat(x));
    const [r, g, b] = p; const a = p.length > 3 ? p[3] : 1;
    if (a === 0) return null;
    const hex = '#' + [r, g, b].map(x => Math.max(0, Math.min(255, Math.round(x))).toString(16).padStart(2, '0')).join('');
    const lum = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255;
    // saturation (for accent detection)
    const mx = Math.max(r, g, b) / 255, mn = Math.min(r, g, b) / 255;
    const l = (mx + mn) / 2, d = mx - mn;
    const sat = d === 0 ? 0 : d / (1 - Math.abs(2 * l - 1));
    let h = 0;
    if (d !== 0) {
      const rr = r/255, gg = g/255, bb = b/255;
      if (mx === rr) h = ((gg - bb)/d) % 6; else if (mx === gg) h = (bb - rr)/d + 2; else h = (rr - gg)/d + 4;
      h *= 60; if (h < 0) h += 360;
    }
    return { hex, a: Math.round(a*100)/100, lum: Math.round(lum*100)/100, sat: Math.round(sat*100)/100, h: Math.round(h) };
  };
  const tally = (map, key) => { if (key == null) return; map[key] = (map[key] || 0) + 1; };
  const topN = (map, n) => Object.entries(map).sort((a,b) => b[1]-a[1]).slice(0, n)
                            .map(([k,v]) => ({ value: isNaN(+k) ? k : +k, count: v }));

  // ---------- BUTTONS ----------
  const btnEls = visible.filter(el =>
    el.tagName === 'BUTTON' || el.getAttribute('role') === 'button' ||
    (el.tagName === 'A' && (el.className||'').toString().match(/btn|button|cta/i)));
  const sigSeen = {};
  const buttons = [];
  btnEls.slice(0, 200).forEach(el => {
    const s = gcs(el);
    const bg = parseColor(s.backgroundColor);
    const fg = parseColor(s.color);
    const bd = parseColor(s.borderTopColor);
    const hasBorder = px(s.borderTopWidth) > 0 && bd;
    // role guess: solid saturated bg = primary; border but transparent bg = secondary/outline; neither = ghost/link
    let role = 'ghost';
    if (bg && bg.a > 0.05 && (bg.sat > 0.15 || bg.lum < 0.25 || bg.lum > 0.92)) role = 'primary';
    else if (hasBorder) role = 'secondary';
    const sig = [role, bg&&bg.hex, fg&&fg.hex, s.borderTopLeftRadius, s.paddingTop, s.paddingLeft, s.fontWeight].join('|');
    if (sigSeen[sig]) { sigSeen[sig]++; return; }
    sigSeen[sig] = 1;
    buttons.push({
      role,
      text: (el.textContent||'').trim().slice(0, 28),
      bg: bg ? bg.hex : 'transparent', bg_alpha: bg ? bg.a : 0,
      color: fg ? fg.hex : null,
      border: hasBorder ? `${px(s.borderTopWidth)}px ${s.borderTopStyle} ${bd.hex}` : 'none',
      radius: s.borderTopLeftRadius,
      padding: `${s.paddingTop} ${s.paddingRight} ${s.paddingBottom} ${s.paddingLeft}`,
      height: Math.round(el.getBoundingClientRect().height),
      font_size: s.fontSize, font_weight: s.fontWeight, font_family: fam(s.fontFamily),
      letter_spacing: s.letterSpacing, line_height: s.lineHeight, text_transform: s.textTransform,
      shadow: s.boxShadow && s.boxShadow !== 'none' ? s.boxShadow.slice(0, 120) : 'none',
      transition: s.transitionProperty && s.transitionProperty !== 'all' && s.transitionProperty !== 'none'
                  ? s.transitionDuration : (s.transitionDuration !== '0s' ? s.transitionDuration : 'none'),
    });
  });
  // keep the loudest few per role
  const byRole = { primary: [], secondary: [], ghost: [] };
  buttons.forEach(b => { (byRole[b.role] = byRole[b.role] || []).push({ ...b, _n: sigSeen[[b.role,b.bg!=='transparent'?b.bg:null,b.color,b.radius,b.padding.split(' ')[0],b.padding.split(' ')[3],b.font_weight].join('|')] || 1 }); });

  // ---------- TYPOGRAPHY ----------
  const typoFor = (sel) => {
    const els = Array.from(document.querySelectorAll(sel)).filter(vis);
    if (!els.length) return null;
    // pick the most prominent instance (largest font-size) as representative
    els.sort((a,b) => parseFloat(gcs(b).fontSize) - parseFloat(gcs(a).fontSize));
    const el = els[0]; const s = gcs(el); const col = parseColor(s.color);
    return {
      count: els.length,
      font_size: s.fontSize, font_size_px: px(s.fontSize),
      font_weight: s.fontWeight, line_height: s.lineHeight,
      line_height_ratio: px(s.lineHeight) && px(s.fontSize) ? Math.round(px(s.lineHeight)/px(s.fontSize)*100)/100 : null,
      letter_spacing: s.letterSpacing, font_family: fam(s.fontFamily),
      color: col ? col.hex : null, text_transform: s.textTransform,
      margin_bottom: s.marginBottom,
    };
  };
  const typography = {};
  ['h1','h2','h3','h4','h5','h6'].forEach(t => { const v = typoFor(t); if (v) typography[t] = v; });
  // body text: the most common <p> size
  const ps = Array.from(document.querySelectorAll('p')).filter(vis);
  if (ps.length) {
    const sizes = {}; ps.forEach(p => tally(sizes, px(gcs(p).fontSize)));
    const common = topN(sizes, 1)[0].value;
    const rep = ps.find(p => px(gcs(p).fontSize) === common) || ps[0];
    const s = gcs(rep); const col = parseColor(s.color);
    typography.body = { count: ps.length, font_size: s.fontSize, font_size_px: common,
      font_weight: s.fontWeight, line_height: s.lineHeight,
      line_height_ratio: px(s.lineHeight) && common ? Math.round(px(s.lineHeight)/common*100)/100 : null,
      letter_spacing: s.letterSpacing, font_family: fam(s.fontFamily), color: col ? col.hex : null };
  }

  // ---------- LAYOUT ----------
  const containers = {};
  visible.filter(el => ['DIV','SECTION','MAIN','HEADER','ARTICLE','NAV'].includes(el.tagName)).slice(0, 3000)
    .forEach(el => { const s = gcs(el); const mw = s.maxWidth;
      if (mw && mw !== 'none' && px(mw) >= 480 && px(mw) <= 2000) tally(containers, px(mw)); });
  const grids = {}, gaps = {}; let flexCount = 0, gridCount = 0;
  visible.slice(0, 3000).forEach(el => {
    const s = gcs(el);
    if (s.display === 'flex' || s.display === 'inline-flex') flexCount++;
    if (s.display === 'grid' || s.display === 'inline-grid') {
      gridCount++;
      const t = s.gridTemplateColumns;
      if (t && t !== 'none') { const cols = t.split(' ').length; tally(grids, cols); }
    }
    if (s.gap && s.gap !== 'normal' && px(s.gap) > 0) tally(gaps, px(s.gap));
  });
  // section vertical rhythm: padding-top on large blocks
  const sectionPads = {};
  visible.filter(el => ['SECTION','DIV'].includes(el.tagName))
    .filter(el => { const r = el.getBoundingClientRect(); return r.width > window.innerWidth*0.6 && r.height > 200; })
    .slice(0, 400).forEach(el => { const p = px(gcs(el).paddingTop); if (p >= 24) tally(sectionPads, p); });

  // ---------- SPACING SCALES ----------
  const padScale = {}, marScale = {};
  visible.slice(0, 4000).forEach(el => {
    const s = gcs(el);
    [s.paddingTop, s.paddingRight, s.paddingBottom, s.paddingLeft].forEach(v => { const n = px(v); if (n > 0) tally(padScale, n); });
    [s.marginTop, s.marginBottom].forEach(v => { const n = px(v); if (n > 0) tally(marScale, n); });
  });

  // ---------- COLOR PALETTE ----------
  const bgColors = {}, textColors = {}, borderColors = {}, accents = {};
  let pageBg = parseColor(gcs(document.body).backgroundColor) || parseColor(gcs(document.documentElement).backgroundColor);
  if (!pageBg) {
    // body/html transparent: take the opaque bg of the largest viewport-covering block
    const covers = visible.filter(el => { const r = el.getBoundingClientRect();
      return r.width > window.innerWidth*0.9 && r.height > window.innerHeight*0.5 && r.top < 200; });
    for (const el of covers) { const c = parseColor(gcs(el).backgroundColor); if (c && c.a > 0.9) { pageBg = c; break; } }
  }
  visible.slice(0, 4000).forEach(el => {
    const s = gcs(el);
    const bg = parseColor(s.backgroundColor); if (bg && bg.a > 0.5) tally(bgColors, bg.hex);
    const fg = parseColor(s.color); if (fg && fg.a > 0.5) tally(textColors, fg.hex);
    const bd = parseColor(s.borderTopColor); if (bd && bd.a > 0.3 && px(s.borderTopWidth) > 0) tally(borderColors, bd.hex);
    // accents: saturated fills on interactive elements
    if ((el.tagName === 'BUTTON' || el.tagName === 'A') && bg && bg.sat > 0.25 && bg.a > 0.5) tally(accents, bg.hex);
  });

  return {
    scheme: matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light',
    buttons: { primary: byRole.primary.slice(0, 4), secondary: byRole.secondary.slice(0, 4), ghost: byRole.ghost.slice(0, 3) },
    typography,
    layout: {
      containers: topN(containers, 5), grid_columns: topN(grids, 5), gaps: topN(gaps, 8),
      section_padding_top: topN(sectionPads, 6), flex_blocks: flexCount, grid_blocks: gridCount,
    },
    spacing: { padding_scale: topN(padScale, 14), margin_scale: topN(marScale, 14) },
    color: {
      page_bg: pageBg ? pageBg.hex : null,
      backgrounds: topN(bgColors, 8), text: topN(textColors, 8),
      borders: topN(borderColors, 6), accents: topN(accents, 6),
    },
  };
}
"""


def _name_of(url):
    return url.replace("https://", "").replace("http://", "").rstrip("/").replace("/", "_")


def scrape_detail(urls, out_dir, timeout=30000, resume=True):
    from playwright.sync_api import sync_playwright
    os.makedirs(out_dir, exist_ok=True)
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True,
                                    args=["--disable-blink-features=AutomationControlled"])
        for url in urls:
            name = _name_of(url)
            if resume and os.path.exists(os.path.join(out_dir, f"{name}.json")):
                print(f"  skip {name}")
                continue
            rec = {"url": url, "name": name}
            ctx = browser.new_context(viewport={"width": 1440, "height": 900},
                                      user_agent=("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                                                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"))
            page = ctx.new_page()
            try:
                # light first
                page.emulate_media(color_scheme="light")
                page.goto(url, wait_until="domcontentloaded", timeout=timeout)
                page.wait_for_timeout(2800)
                try: page.evaluate("document.fonts && document.fonts.ready")
                except Exception: pass
                rec["light"] = page.evaluate(EXTRACT_DETAIL_JS)
                rec["title"] = page.title()
                # dark: emulate, give the page a beat to react (class/attr swaps, CSS vars)
                page.emulate_media(color_scheme="dark")
                page.wait_for_timeout(900)
                rec["dark"] = page.evaluate(EXTRACT_DETAIL_JS)
                rec["has_dark_mode"] = rec["dark"]["color"]["page_bg"] != rec["light"]["color"]["page_bg"]
                rec["ok"] = True
                lp = rec["light"]["buttons"]["primary"]
                print(f"  ok   {name:26}  primaryBtn={lp[0]['bg'] if lp else '-':9}  "
                      f"darkMode={rec['has_dark_mode']}  "
                      f"pageBg L={rec['light']['color']['page_bg']} D={rec['dark']['color']['page_bg']}")
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


# Design-led sites with strong, opinionated component systems worth cataloging.
DETAIL_CORPUS = [
    "https://stripe.com", "https://linear.app", "https://vercel.com", "https://www.framer.com",
    "https://www.raycast.com", "https://supabase.com", "https://resend.com", "https://clerk.com",
    "https://posthog.com", "https://www.prisma.io", "https://tailwindcss.com", "https://www.anthropic.com",
    "https://openai.com", "https://www.toss.im", "https://mercury.com", "https://ramp.com",
    "https://www.notion.so", "https://www.figma.com", "https://www.apple.com", "https://github.com",
    "https://arc.net", "https://www.duolingo.com", "https://www.loom.com", "https://railway.app",
]


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.join(here, "..")
    args = sys.argv[1:]
    if len(args) == 1 and os.path.exists(args[0]):
        urls = [ln.strip() for ln in open(args[0]) if ln.strip() and not ln.startswith("#")]
    elif args:
        urls = args
    else:
        urls = DETAIL_CORPUS
    out = os.path.join(root, "data", "sites_detail")
    t0 = time.time()
    res = scrape_detail(urls, out)
    ok = sum(1 for r in res.values() if r.get("ok"))
    print(f"\ndetail-scraped {ok}/{len(urls)} in {time.time()-t0:.0f}s -> {out}")
