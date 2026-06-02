# Korean web specs, and how they differ from the global set

Measured the same way as the global catalog, on 48 Korean design-led sites (Toss, Kakao, 당근, 무신사, 29CM, 오늘의집, 마켓컬리, 배민, 업비트, and more), read straight off their live computed styles in light and dark. The point is the *differences*: Korean (hangul/CJK) type is set differently from Latin, and the numbers show it.

> Source: `src/scrape_detail.py` over `data/site_list_kr.txt`, aggregated by `scripts/build_korean_catalog.py`. Corpus: 48 sites. Global comparison from `data/spec_catalog.json` (199 mostly-Western sites).

## The headline differences

| | Korean sites | Global sites |
|---|---|---|
| **Default body font** | Pretendard / hangul sans (69% a Korean face, 44% Pretendard) | Inter / system sans |
| **Body font-size** | 14.3px | 16.0px |
| **Body line-height** | 1.5 | 1.5 |
| **h1 size (median)** | 28.0px (bimodal) | 64.0px |

Two differences are real, one is a corpus artifact worth explaining.

**1. The font.** Pretendard is the body face on 44% of these sites and some hangul sans on 69%. Pretendard is to the Korean web what Inter is to the Western web: the free, well-hinted default. So the *type tell* translates: shipping bare Pretendard with no scale is the Korean equivalent of bare Inter, and the fix is the same, a real scale plus a commissioned face where the brand warrants it (Toss Product Sans, Bithumb Trading Sans, Gmarket Sans, Wanted Sans).

**2. Body size.** Korean body text sets *smaller*: a 14.3px median against 16.0px globally, clustering at 13 to 15px. Hangul carries more ink per character, so 14px hangul reads at roughly the presence of 16px Latin; Korean product culture is also denser. Setting hangul at a Western 16 to 18px often looks oversized to a Korean eye.

**Not a difference: line-height.** Both land at ~1.5. Hangul does want air, but Pretendard already ships a generous default, so the median matches the West rather than running looser. Keep body leading around 1.5 to 1.7 and you are inside both distributions.

**The h1 caveat.** The Korean h1 median (28.0px) is *bimodal*, not small. Design-led product sites (Toss, 당근, 오늘의집, 무신사) use 56 to 90px heroes exactly like the West; portals and commerce (Naver, Coupang, Gmarket, SSG, Melon) are banner-and-carousel driven with a small or absent display headline. The low median is the density culture of Korean commerce, not a different idea of what a headline is. Read it as: pick your lane, and if you are a product site, the big-hero numbers from the global catalog still apply.

## Fonts

- **Body typeface:** `pretendard` (13), `pretendard variable` (6), `-apple-system` (3), `toss product sans` (2), `noto sans kr` (2), `맑은 고딕` (2), `noto sans demilight` (1), `source code pro` (1).
- **Heading typeface:** `pretendard` (10), `pretendard variable` (7), `-apple-system` (4), `toss product sans` (2), `noto sans kr` (2), `맑은 고딕` (2), `noto sans demilight` (1), `poppins` (1).
- **Pretendard** alone is the body face on **44%** of these sites; a Korean-designed face covers **69%**. Pretendard is to the Korean web what Inter is to the Western web, the safe, free, well-hinted default. The owned-craft move is a commissioned face (Toss Product Sans, Bithumb Trading Sans, Gmarket Sans, Wanted Sans), not avoiding Pretendard.

## Type scale (light)

| Element | Size (median) | Line-height | Weight | Negative tracking |
|---|---|---|---|---|
| **h1** (26) | 28.0px | 1.3 | 700.0 | 46% |
| **h2** (35) | 26.0px | 1.3 | 700 | 34% |
| **h3** (25) | 24.0px | 1.4 | 700 | 40% |
| **body** (44) | 14.3px | 1.5 | 400.0 | 25% |

Body sizes cluster at `14px` (9), `16px` (8), `12px` (7), `20px` (5), `18px` (3), `13px` (3). Negative letter-spacing is common on hangul (25% of body blocks track in); a touch of negative tracking (around -0.02em) tightens the gaps between syllable blocks. Do not over-track, hangul loses legibility faster than Latin.

## Buttons

- **Primary:** radius median `4.0px` (full pill on 15%), label `15.0px`, weight `400`.
- The radius story matches the global one (a soft round or a full pill, sharp corners rare). Korean button geometry is noisier to read off the DOM because many primary actions are styled links or icon-and-label rows rather than a single padded `<button>`.

## Color

- **Light page bg:** `#ffffff` (25), `#000000` (3), `#f8f8f8` (2), `#e9ecf1` (1), `#f6f6f6` (1), `#fbfbfb` (1).
- **Primary text:** `#000000` (15), `#333333` (6), `#ffffff` (3), `#666666` (3), `#222222` (3), `#424242` (2).
- **Accent (primary action):** `#4e608e` (1), `#31a552` (1), `#000a73` (1), `#0b84ff` (1), `#0078ff` (1), `#1e9eff` (1), `#000c1e` (1), `#0062df` (1). A spread of owned brand colors (Toss and Coupang blues, a Naver-style green, and more), each appearing once, never a shared default indigo. As in the global set, the hue is not the tell.
- **Dark mode:** 3 of 48 repaint for `prefers-color-scheme: dark`; dark bg `#0c0c0c` (1), `#000000` (1), `#1a1a1a` (1) (the same tinted-near-black grammar).

## Appendix: per-site body font + size

| Site | Body font | Body px | Body line-height | h1 px |
|---|---|---|---|---|
| brunch.co.kr | Noto Sans DemiLight | 16 | 1.63 | 28 |
| channel.io | Source Code Pro | 11.66 | 1.29 | 44 |
| class101.net | - | - | - | 40 |
| fastcampus.co.kr | Pretendard Variable | 14 | 1.5 | 32 |
| hyperconnect.com | Poppins | 10 | 1.5 | 62 |
| line.me | SFPro | 20 | 1.6 | 20 |
| moloco.com | Montserrat Uploaded | 14 | 1.35 | 64 |
| ohou.se | Pretendard Variable | 16 | 1.25 | 30 |
| programmers.co.kr | Inter | 26 | 1.5 | - |
| ridibooks.com | - | - | - | - |
| sendbird.com | Helvetica Now Text | 18 | 1.4 | 72 |
| toss.im | Toss Product Sans | 20 | 1.5 | 66 |
| upbit.com | Roboto | 14 | 1.5 | - |
| watcha.com | Pretendard | 12 | 1.5 | - |
| www.11st.co.kr | Noto Sans KR | 14 | 1.5 | 14 |
| www.29cm.co.kr | Pretendard Variable | 12 | 1.36 | - |
| www.aladin.co.kr | Malgun Gothic | 14 | 1.4 | 0 |
| www.baemin.com | -apple-system | 20 | 1.45 | - |
| www.banksalad.com | Pretendard | 22 | 1.14 | - |
| www.bithumb.com | Bithumb Trading Sans | 14 | 1.5 | 60 |
| www.cgv.co.kr | pretendard | 10 | 1 | 10 |
| www.coupang.com | Apple SD Gothic Neo | 11 | 1.5 | - |
| www.daangn.com | - | - | - | - |
| www.gmarket.co.kr | -apple-system | 0 | None | 0 |
| www.inflearn.com | Pretendard | 16 | 1.5 | 22 |
| www.kakaobank.com | Pretendard Variable | 16 | 1.5 | 90 |
| www.kakaocorp.com | KakaoBig | 16 | 1.75 | 28 |
| www.kbstar.com | 맑은 고딕 | 13 | 1.5 | 14 |
| www.kurly.com | Pretendard | 14 | 1.36 | - |
| www.lguplus.com | nskr | 18 | 1.2 | 20 |
| www.lottecinema.co.kr | Noto Sans KR | 12 | 1.1 | 24 |
| www.megabox.co.kr | NanumBarunGothic | 15 | 1.5 | 30 |
| www.melon.com | Pretendard | 12 | None | 12 |
| www.musinsa.com | Pretendard | 13 | 1.38 | - |
| www.naver.com | -apple-system | 14.7 | 1.36 | 14.7 |
| www.oliveyoung.co.kr | Montserrat | 14 | 2.86 | 28 |
| www.rememberapp.co.kr | Pretendard | 16 | 1.3 | - |
| www.shinhancard.com | SpoqaHanSansNeo | 14 | 1.53 | - |
| www.socar.kr | Pretendard | 13 | 1.54 | 26 |
| www.ssg.com | Pretendard | 15 | None | 12 |
| www.tossbank.com | Toss Product Sans | 12 | 1.6 | - |
| www.tving.com | Pretendard | 19.8 | 1.5 | - |
| www.wanted.co.kr | Pretendard Variable | 16 | 1.5 | - |
| www.woowahan.com | Pretendard Variable | 16 | 1.5 | 16 |
| www.yanolja.com | pretendard | 20 | 1.2 | - |
| www.yes24.com | 맑은 고딕 | 12 | None | - |
| www.zigbang.com | Pretendard | 22 | 1.45 | - |
| zigzag.kr | Pretendard JP | 18 | None | - |

<!-- generated by scripts/build_korean_catalog.py from 48 sites -->