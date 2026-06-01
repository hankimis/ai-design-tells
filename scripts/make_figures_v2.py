#!/usr/bin/env python3
"""
v2 figures from the real-site corpus (202 human-crafted top-tier sites).

  fig6_realworld.png   THE v2 result: 202 real sites cluster near 0; AI defaults don't
  fig7_empirical.png   the learned distributions (radii, font sizes, centering) vs AI default
  fig8_gallery.png     a montage of real-site folds, the diversity AI collapses
  fig9_credits.png     the craft-credit mechanism (Stripe scores 0 despite 123 purple accents)
"""
import os, sys, json, glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
FIGS = os.path.join(ROOT, "paper", "figs")
DATA = os.path.join(ROOT, "data")
os.makedirs(FIGS, exist_ok=True)
sys.path.insert(0, os.path.join(ROOT, "src"))
from scorer import score_signals, _load_calib  # noqa: E402

INK="#16181d"; SOFT="#5b6066"; FAINT="#9aa0a6"; LINE="#e7e4de"; BG="#fbfaf8"
SLOP="#6d5cf6"; GOOD="#0f6f63"; CLAY="#9a3b1f"

def _serif():
    for c in ["Charter","Iowan Old Style","Georgia","Palatino"]:
        try:
            p=fm.findfont(fm.FontProperties(family=c),fallback_to_default=False)
            if p and os.path.exists(p): fm.fontManager.addfont(p); return fm.FontProperties(fname=p).get_name()
        except Exception: pass
    return "DejaVu Serif"
SERIF=_serif()
plt.rcParams.update({"figure.facecolor":BG,"axes.facecolor":BG,"savefig.facecolor":BG,
    "font.sans-serif":["Avenir Next","Helvetica Neue","Arial","DejaVu Sans"],"font.family":"sans-serif",
    "text.color":INK,"axes.labelcolor":INK,"xtick.color":SOFT,"ytick.color":SOFT,
    "axes.edgecolor":LINE,"axes.linewidth":1.0,"font.size":12,
    "axes.spines.top":False,"axes.spines.right":False})

def title(ax,t,sub=None):
    ax.text(0,1.16,t,transform=ax.transAxes,va="bottom",fontproperties=fm.FontProperties(family=SERIF,size=19),color=INK)
    if sub: ax.text(0,1.045,sub,transform=ax.transAxes,va="bottom",color=SOFT,fontsize=10.5)
def save(fig,n):
    fig.savefig(os.path.join(FIGS,n),dpi=200,bbox_inches="tight",pad_inches=0.25); plt.close(fig); print(n)

SITE_SCORES=json.load(open(os.path.join(DATA,"site_scores.json"),encoding="utf-8"))
CALIB=_load_calib()

def _fixture_scores():
    out={}
    for fp in glob.glob(os.path.join(DATA,"fixtures_signals","*.json")):
        d=json.load(open(fp,encoding="utf-8"))
        if d.get("ok"):
            out[d["url"].split("/")[-1].replace(".html","")]=score_signals(d,CALIB).score
    return out
FIX=_fixture_scores()

# --------------------------------------------------------------------------
def fig_realworld():
    scores=sorted(r["score"] for r in SITE_SCORES)
    n=len(scores)
    fig,ax=plt.subplots(figsize=(10.5,4.6))
    # histogram of real sites
    ax.hist(scores,bins=np.arange(0,70,3.5),color=GOOD,alpha=.85,zorder=3,label=f"{n} real top-tier sites")
    med=np.median(scores)
    ax.axvline(med,color=INK,lw=2,zorder=4)
    ax.text(med+1,ax.get_ylim()[1]*0.92,f"real-site median {med:.0f}",color=INK,fontsize=11,fontweight="bold")
    # AI-default fixtures as markers
    ai=[("ai-default",FIX.get("ai-default",0)),("slop-pricing",FIX.get("slop-pricing",0)),
        ("slop-dashboard",FIX.get("slop-dashboard",0))]
    for nm,sc in ai:
        ax.axvline(sc,color=SLOP,lw=2,ls=(0,(3,2)),zorder=4)
        ax.text(sc,ax.get_ylim()[1]*0.62,f" {nm}\n {sc:.0f}",color=SLOP,fontsize=9.5,fontweight="bold",rotation=0,va="top")
    ax.set_xlabel("Tell Score  (lower is better)"); ax.set_ylabel("number of sites")
    ax.tick_params(length=0); ax.grid(axis="y",color=LINE,lw=1); ax.set_axisbelow(True)
    ax.legend(frameon=False,loc="upper right")
    title(ax,"Calibrated on 202 real sites, the best ones read as human-crafted",
          "After learning where top sites actually sit, AI-default pages stand out, real craft does not.")
    save(fig,"fig6_realworld.png")

def fig_empirical():
    radii=[len(r) for r in (json.load(open(f,encoding="utf-8")).get("radii",[]) for f in glob.glob(os.path.join(DATA,"sites","*.json")))]
    # reload signals properly
    sigs=[json.load(open(f,encoding="utf-8")) for f in glob.glob(os.path.join(DATA,"sites","*.json"))]
    sigs=[s for s in sigs if s.get("ok")]
    radii=[len(s["radii"]) for s in sigs]
    fonts=[len(s["font_sizes"]) for s in sigs]
    cent=[s["layout"]["centered_fraction"]*100 for s in sigs]
    panels=[("distinct border-radii",radii,np.arange(0,22,2),2,"AI default: 1, one radius"),
            ("distinct font sizes",fonts,np.arange(0,22,2),3,"AI default: <=3"),
            ("% blocks centered",cent,np.arange(0,105,8),100,"AI default: 100%")]
    fig,axes=plt.subplots(1,3,figsize=(13,3.9))
    for ax,(lab,xs,bins,aival,note) in zip(axes,panels):
        ax.hist(xs,bins=bins,color=GOOD,alpha=.85,zorder=3)
        ax.axvline(np.median(xs),color=INK,lw=2);
        ax.text(np.median(xs),ax.get_ylim()[1]*0.9,f"med {np.median(xs):.0f}",fontsize=9.5,color=INK)
        ax.axvline(min(aival,bins[-1]),color=SLOP,lw=2,ls=(0,(3,2)))
        ax.set_title(lab,fontsize=12,color=INK,loc="left")
        ax.set_xlabel(note,color=SLOP,fontsize=9)
        ax.tick_params(length=0); ax.grid(axis="y",color=LINE,lw=1); ax.set_axisbelow(True)
    fig.suptitle("What human-crafted design actually does (202 sites), and where the AI default sits",
                 fontproperties=fm.FontProperties(family=SERIF,size=17),x=0.012,ha="left",y=1.06,color=INK)
    fig.tight_layout()
    save(fig,"fig7_empirical.png")

def fig_credits():
    # famous sites: cosmetic-signal counts vs final score; craft credits offset them
    want=["stripe.com","linear.app","www.toss.im","www.apple.com","vercel.com","github.com"]
    byname={r["name"]:r for r in SITE_SCORES}
    rows=[]
    for f in glob.glob(os.path.join(DATA,"sites","*.json")):
        d=json.load(open(f,encoding="utf-8"))
        if d.get("name") in want and d.get("ok"):
            sc=byname.get(d["name"],{}).get("score",0)
            cr=byname.get(d["name"],{}).get("credits",0)
            rows.append((d["name"],d["color"]["purple_accents"],d["color"]["blue_purple_gradients"],cr,sc))
    rows=sorted(rows,key=lambda r:-r[1])
    rows.append(("ai-default (fixture)",3,2,0,FIX.get("ai-default",0)))
    fig,ax=plt.subplots(figsize=(10.5,4.6))
    y=np.arange(len(rows))
    names=[r[0] for r in rows]
    purp=[r[1] for r in rows]; scores=[r[4] for r in rows]; creds=[r[3] for r in rows]
    ax.barh(y,purp,color=SLOP,alpha=.85,zorder=3,height=.6)
    for i,(nm,p,g,cr,sc) in enumerate(rows):
        ax.text(p+2,i,f"score {sc:.0f}  ·  {cr} craft credits",va="center",fontsize=10,
                color=GOOD if sc<28 else CLAY,fontweight="bold")
    ax.set_yticks(y); ax.set_yticklabels(names,fontsize=11); ax.invert_yaxis()
    ax.set_xlabel("purple accent colors used on the page")
    ax.tick_params(length=0); ax.grid(axis="x",color=LINE,lw=1); ax.set_axisbelow(True)
    title(ax,"Purple is not the tell. The missing craft is.",
          "Stripe uses purple heavily and scores 0: a custom font, optical tracking and a radius hierarchy offset it.")
    save(fig,"fig9_credits.png")

def fig_gallery():
    # montage of real-site folds (the diversity a single AI default collapses)
    picks=["stripe.com","linear.app","www.toss.im","www.apple.com","vercel.com","www.framer.com",
           "www.notion.so","www.figma.com","supabase.com","www.anthropic.com","openai.com","github.com",
           "www.airbnb.com","www.nike.com","www.spotify.com","arc.net","mercury.com","ramp.com",
           "www.raycast.com","resend.com","clerk.com","posthog.com","www.duolingo.com","www.canva.com",
           "railway.app","sentry.io","planetscale.com","www.cloudflare.com"]
    avail=[p for p in picks if os.path.exists(os.path.join(DATA,"shots",f"{p}.png"))]
    cols=4; rows=(len(avail)+cols-1)//cols
    tw,th=360,225; pad=10; lab=20
    W=cols*tw+(cols+1)*pad; H=rows*(th+lab)+(rows+1)*pad+50
    canvas=Image.new("RGB",(W,H),(251,250,248))
    from PIL import ImageDraw,ImageFont
    d=ImageDraw.Draw(canvas)
    def font(sz,b=False):
        for p in (["/System/Library/Fonts/Supplemental/Georgia Bold.ttf"] if b else ["/System/Library/Fonts/Supplemental/Georgia.ttf"]):
            if os.path.exists(p): return ImageFont.truetype(p,sz)
        return ImageFont.load_default()
    d.text((pad,14),"A montage of 28 human-crafted sites. Each made different choices, that is the point.",font=font(22,True),fill=(22,24,29))
    for i,name in enumerate(avail):
        r,c=divmod(i,cols)
        x=pad+c*(tw+pad); y=50+pad+r*(th+lab+pad)
        try:
            im=Image.open(os.path.join(DATA,"shots",f"{name}.png")).convert("RGB").resize((tw,th))
            canvas.paste(im,(x,y))
        except Exception: pass
        d.rectangle([x,y,x+tw,y+th],outline=(231,228,222),width=1)
        d.text((x+2,y+th+3),name,font=font(13),fill=(91,96,102))
    canvas.save(os.path.join(FIGS,"fig8_gallery.png"))
    print("fig8_gallery.png", f"({len(avail)} sites)")

if __name__=="__main__":
    fig_realworld(); fig_empirical(); fig_credits(); fig_gallery(); print("done.")
